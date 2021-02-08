# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import pymysql


# class ZufangPipeline:
#     def __init__(self):
#         self.file = open("zufang.csv", "w+", encoding="utf-8")
#
#     def process_item(self, item, spider):
#         res = dict(item)
#         str = json.dumps(res, ensure_ascii=False)
#         self.file.write(str)
#         self.file.write(',\n')
#         print(item)
#
#     def close_spier(self, spider):
#         self.file.close()

class ZufangPipeline:
    def __init__(self):
        self.db = pymysql.connect(host='127.0.0.1',
                                  user='root',
                                  password='mysql',
                                  db='renthouse')
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        sql = "INSERT INTO houses(url,address,money)VALUES('%s','%s','%s')" % (
            item['href'], item['title'], item['money'])
        self.cursor.execute(sql)
        self.db.commit()

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()
