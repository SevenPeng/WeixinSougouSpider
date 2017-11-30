# *-* coding:utf-8 *-*
import requests
from bs4 import BeautifulSoup


class Proxies(object):
    """docstring for Proxies"""

    def __init__(self, page=3):
        self.proxies = []
        self.text = ''
        self.verify_pro = []
        self.page = page
        self.headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        self.get_proxies()
        # self.get_proxies_nn()

    def get_proxies(self):
        url = 'http://webapi.http.zhimacangku.com/getip?num=40&type=1&pro=0&city=0&yys=0&port=1&pack=7627&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=2'
        html = requests.get(url, headers=self.headers).content
        soup = BeautifulSoup(html, 'lxml')
        self.text = html


if __name__ == '__main__':
    a = Proxies()
    temp = []
    print(a.text)
    w = str(a.text).split("'", 2)[1]
    temp = w.split('\\r\\n', -1)

    with open('proxies.txt', 'w') as f:
        for line in temp:
            f.write(line + '\n')
