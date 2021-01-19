import requests
import pymysql
from bs4 import BeautifulSoup
from queue import Queue
import threading


class GetData(object):
    def __init__(self):
        city = 'gz'
        self.start_url = "http://%s.lianjia.com/zufang" % city
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/65.0.3325.181 Safari/537.36 '
        }
        # 创建队列
        self.url_queue = Queue()
        self.parse_queue = Queue()
        self.content_queue = Queue()

    def get_url(self):
        for page_num in range(1, 11):
            part_url = "%s/pg%d" % (self.start_url, page_num)
            self.url_queue.put(part_url)

    def parse_url(self):
        while True:
            url = self.url_queue.get()
            response = requests.request("get", url, headers=self.headers).content.decode()
            htmlsoup = BeautifulSoup(response, "html.parser")
            self.parse_queue.put(htmlsoup)
            self.url_queue.task_done()

    def get_data(self):
        # 获取数据
        while True:
            datalist = []
            htmlsoup = self.parse_queue.get()
            div = htmlsoup.find(attrs={"class": "content__list"})
            div_list = div.find_all("div", {'class': 'content__list--item'})
            for info in div_list:
                house_url = info.find('a')['href']
                address = info.find('a', {'class': 'content__list--item--aside'})['title']
                money = info.find('span', {'class': 'content__list--item-price'}).text
                data = {'url': '%s%s' % (self.start_url, house_url), 'address': address, 'money': money}
                datalist.append(data)
            self.content_queue.put(datalist)
            self.parse_queue.task_done()

    def save_data(self):
        while True:
            datalist = self.content_queue.get()
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
            self.content_queue.task_done()

    def run(self):
        thread_list = []
        # 1.获取url
        t_url = threading.Thread(target=self.get_url)
        thread_list.append(t_url)
        # 2.获取响应并解析网页
        for i in range(5):
            t_response = threading.Thread(target=self.parse_url)
            thread_list.append(t_response)
        # 4.获取数据
        for i in range(5):
            t_data = threading.Thread(target=self.get_data)
            thread_list.append(t_data)
        # 5.保存数据
        t_save = threading.Thread(target=self.save_data)
        thread_list.append(t_save)
        for t in thread_list:
            t.setDaemon(True)  # 把子线程设置为守护线程
            t.start()
        for q in [self.url_queue, self.parse_queue, self.content_queue]:
            q.join()  # 让主线程等待阻塞，等待队列的任务完成之后再完成
        print('主线程结束')


if __name__ == '__main__':
    getdatatosql = GetData()
    getdatatosql.run()
