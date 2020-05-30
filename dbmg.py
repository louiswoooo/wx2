import pymysql
import datetime

db = pymysql.connect(host="localhost", user="root", \
                     password="genius", database="aigou", charset="utf8")
cur = db.cursor()
#创建数据库连接类
class aigou_db:
    def __init__(self):
        pass
    # 找到最近的一份报价
    def find_price(self):
        sql_sen = " select info from price where dat=(select max(dat) from price) order by tim desc limit 1;"
        try:
            cur.execute(sql_sen)
        except Exception as e:
            print(e)
            db.connect()
            cur.execute(sql_sen)
        info = cur.fetchone()[0]
        return info
    # 插入价格信息进入 price 表
    def insert_price(self, price):
        db.connect()
        now_time = datetime.datetime.now()
        sql = "insert into price (name, dat, tim, info) values (\"%s\",\"%s\",\"%s\",\"%s\")"      \
              % ("伍柳军", now_time.strftime('%Y-%m-%d'),now_time.strftime('%H:%M:%S'), price)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
    # 插入订单信息进入 order 表
    def insert_order(self, order):
        db.connect()
        now_time = datetime.datetime.now()
        sql = "insert into order_list (name, dat, tim, info) values (\"%s\",\"%s\",\"%s\",\"%s\")"\
              % ("杨博纯", now_time.strftime('%Y-%m-%d'),now_time.strftime('%H:%M:%S'), order)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
    # 插入计算结果
    def insert_result(self, result):
        db.connect()
        now_time = datetime.datetime.now()
        try:
            sql_sen = "select MAX(id) from price"
            temp = cur.execute(sql_sen)
        except Exception as e:
            print(e)
        price_id = cur.fetchone()[0]
        try:
            sql_sen = "select MAX(id) from order_list where name = '杨博纯'"
            temp = cur.execute(sql_sen)
        except Exception as e:
            print(e)
        order_id = cur.fetchone()[0]

        sql = "insert into result (name, dat, tim, info, price_id, order_id) " \
              "values (\"%s\",\"%s\",\"%s\",\"%s\",\"%d\",\"%d\")"\
              % ("杨博纯", now_time.strftime('%Y-%m-%d'),now_time.strftime('%H:%M:%S'), result, price_id, order_id)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)

