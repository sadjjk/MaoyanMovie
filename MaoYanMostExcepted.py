import requests
import re
import os
import json
from requests.exceptions import RequestException
from fontTools.ttLib import TTFont
from multiprocessing import Pool 
# 获取网页源码


def get_html(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # return response.text.encode('gbk','ignore').decode('gbk')
            return response.content
        return None
    except RequestException:
        return None

# 下载新字体


def create_woff(html):
    pattern = re.compile(r"url\('(.*?)'\) format\('woff'\)")
    font_url = re.findall(pattern, html)[0]
    font_url = "http:" + font_url
    font_name = font_url.split('/')[-1]
    file_list = os.listdir('./fonts')
    if font_name not in file_list:
        print('不在字体库中, 下载:', font_name)
        response = get_html(font_url)
        with open('./fonts/' + font_name, 'wb') as f:
            f.write(response)
            f.close()
    newFont = TTFont('./fonts/' + font_name)
    return newFont

# 字体解密 将源码不可读数字替换成可读数字


def modify_html(newFont, html):
    baseFont = TTFont('./3a3b3fa669eb498c3d519e768855622b2084.woff')
    uniList = newFont['cmap'].tables[0].ttFont.getGlyphOrder()
    numList = []
    baseNumList = ['3', '5', '8', '7', '0', '1', '9', '6', '2', '4']
    baseUniCode = ['uniEBDA', 'uniF0ED', 'uniE285', 'uniF0C0', 'uniF4B9', 'uniE417',
                   'uniF5E3', 'uniE0B0', 'uniE76A', 'uniE99C']
    for i in range(1, 12):
        newGlyph = newFont['glyf'][uniList[i]]
        for j in range(10):
            baseGlyph = baseFont['glyf'][baseUniCode[j]]
            if newGlyph == baseGlyph:
                numList.append(baseNumList[j])
                break
    rowList = []
    for i in uniList[2:]:
        i = i.replace('uni', '&#x').lower() + ";"
        rowList.append(i)

    dictory = dict(zip(rowList, numList))

    for key in dictory:
        if key in html:
            html = html.replace(key, str(dictory[key]))
    return html

# 解析网页 获取电影相关数据


def parse_page(html):
    pattern = re.compile('<dd>.*?board-index-.*?>(.*?)</i>.*?data-src="(.*?)".*?'
                         + 'title="(.*?)".*?class="star">(.*?)</p>.*?releasetime">(.*?)</p>.*?'
                         + 'month-wish".*?stonefont">(.*?)</span>.*?'
                         + 'total-wish".*?stonefont">(.*?)</span>.*?</dd>', re.S)

    items = re.findall(pattern, html)
    for item in items:
        yield{
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'action': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'monthwish': item[5],
            'totalwish': item[6]
        }

# 写入


def write_to_file(content):
    with open('猫眼最受期待榜.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(offset):
    url = 'http://maoyan.com/board/6?offset='+str(offset)
    html = get_html(url).decode('utf-8')
    newFont = create_woff(html)
    html = modify_html(newFont, html)
    for item in parse_page(html):
        print(item)
        write_to_file(item)

#多进程 虽然不需要 有点杀鸡用牛刀
if __name__ == '__main__':
    pool = Pool()
    pool.map(main,[i * 10 for i in range(5)])
