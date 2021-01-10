import requests
import pymysql
from bs4 import BeautifulSoup


def get_data():
    datalist = []
    city = 'sz'
    city_url = 'http://%s.lianjia.com' % city
    for page_num in range(1, 11):
        url = "%s/zufang/pg%d/" % (city_url, page_num)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/65.0.3325.181 Safari/537.36 '
        }
        response = requests.request("GET", url, headers=headers)
        htmlSoup = BeautifulSoup(response.text, "html.parser")
        div = htmlSoup.find(attrs={"class": "content__list"})
        if div is None:
            continue
        div_list = div.find_all("div", {'class': 'content__list--item'})
        if div_list is None:
            continue
        for info in div_list:
            house_url = info.find('a')['href']
            address = info.find('a', {'class': 'content__list--item--aside'})['title']
            money = info.find('span', {'class': 'content__list--item-price'}).text
            data = {'url': '%s%s' % (city_url, house_url), 'address': address, 'money': money}
            datalist.append(data)
    return datalist


def into_mysql(datalist):
    db = pymysql.connect(host='127.0.0.1',
                         user='root',
                         password='mysql',
                         db='renthouse')
    cursor = db.cursor()
    for j in range(len(datalist)):
        datarow = datalist[j]
        addr = datarow['address']
        hurl = datarow['url']
        money = datarow['money']
        sql = "INSERT INTO houses(url,address,money)VALUES('%s','%s','%s')" % (hurl, addr, money)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print('数据写入失败', e)
            db.rollback()
            db.close()


def main():
    datalist = get_data()
    into_mysql(datalist)


if __name__ == '__main__':
    main()
