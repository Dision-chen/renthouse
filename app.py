from flask import Flask, request, jsonify
import pymysql


app = Flask(__name__)


@app.route('/')
def index():
    """定义视图函数"""
    global city, money, money1, money2
    city = request.args.get('city')  # 获取城市
    price = request.args.get('price')  # 获取价格
    if price:
        money = price.split('?')[0]
        if money:
            money1 = money.split('-')[0]
            money2 = money.split('-')[1]
    return app.send_static_file('index.html')  # 默认页面


@app.route("/get_houses_db/")
def get_houses_db():
    """从数据库拿数据"""
    db = pymysql.connect(host='127.0.0.1',
                         user='root',
                         password='mysql',
                         db='renthouse',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)  # 连接数据库 将结果作为字典返回
    try:
        with db.cursor() as cursor:  # 开启游标
            if money:
                sql = '''SELECT url,address,money FROM houses WHERE url like "%%%s%%" and money between "%s" and 
                "%s";''' % (city, money1, money2)  # sql语句拿数据
            else:
                sql = '''SELECT url,address,money FROM houses WHERE url like "%%%s%%";''' % city
            cursor.execute(sql)  # 执行sql语句
            houses = cursor.fetchall()  # 返回多个元组
    finally:
        db.close()
    return jsonify(houses)  # 返回json数据


if __name__ == '__main__':
    app.run(port=8888, debug=True)
