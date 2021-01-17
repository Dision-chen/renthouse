# coding:utf-8

import requests
import pymysql
from bs4 import BeautifulSoup


class GetData(object):
    def __init__(self):
        self.url = "http://%s.lianjia.com/zufang/pg%d"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/65.0.3325.181 Safari/537.36 '
        }

    def parse_url(self, url):
        response = requests.request("GET", url, headers=self.headers)
        return response

    def soup_url(self, response):
        htmlsoup = BeautifulSoup(response.text, "html.parser")
        return htmlsoup

    def get_data(self, htmlsoup, url, datalist):
        div = htmlsoup.find(attrs={"class": "content__list"})
        div_list = div.find_all("div", {'class': 'content__list--item'})
        for info in div_list:
            house_url = info.find('a')['href']
            address = info.find('a', {'class': 'content__list--item--aside'})['title']
            money = info.find('span', {'class': 'content__list--item-price'}).text
            data = {'url': '%s%s' % (url, house_url), 'address': address, 'money': money}
            datalist.append(data)
        return datalist

    def save_data(self, datalist):
        db = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='mysql',
                             db='renthouse')
        cursor = db.cursor()
        for j in range(len(datalist)):
            datarow = datalist[j]
            addr = datarow['address']
            url = datarow['url']
            money = datarow['money']
            sql = "INSERT INTO houses(url,address,money)VALUES('%s','%s','%s')" % (url, addr, money)
            try:
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print('数据写入失败', e)
                db.rollback()
                db.close()

    def run(self):
        city = 'gz'  # 爬取的城市，请对照链家的城市简写
        datalist = []  # 存放数据
        # 1.获取url
        for page_num in range(1, 11):
            url = self.url % (city, page_num)
            # 2.发送请求获取响应
            response = self.parse_url(url)
            # 3.解析数据
            htmlsoup = self.soup_url(response)
            # 4.提取数据
            datalist = self.get_data(htmlsoup, url, datalist)
        # 5.保存数据
        self.save_data(datalist)


if __name__ == '__main__':
    getdatatosql = GetData()
    getdatatosql.run()
