import re
import requests
from requests.exceptions import RequestException
import json
from multiprocessing import Pool


def get_one_page(url):
    #异常处理
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text.encode('GBK', 'ignore').decode('GBk')
        return None
    except RequestException:
        return None


def parse_one_page(url):
    pattern = re.compile('dd.*?board-index.*?">(\d+)</i>.*?'
                         + 'data-src="(.*?)".*?title="(.*?)".*?class="star">(.*?)</p>.*?'
                         + 'releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, url)
    for item in items:
        yield{
            "index": item[0],
            "image": item[1],
            "title": item[2],
            "actor": item[3].strip()[3:],
            "time": item[4].strip()[5:],
            "score": item[5] + item[6]
        }


def write_to_file(content):
    with open('猫眼Top100榜.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)

if __name__ == '__main__':
    # for i in range(10):
        # main(i*10)
    # 多进程
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])


# text = requests.get('http://maoyan.com/board/4').text
# print(text.encode('GBK','ignore').decode('GBk'))
