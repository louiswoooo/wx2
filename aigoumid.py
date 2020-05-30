from aigou import aigou
from dbmg import *
import re
#微信信息的过滤器定义，只保留指定的编码字符，
# 包括中文、英文大小写、数字等，
WX_CONTENT_PAT = "[^\u4e00-\u9fa5^a-z^A-Z^0-9^\n^ ^(^)^+^-^.^:^/^ ^（^）^，^。^：^、^＋^-]"

class aigoumid:
    def __init__(self):
        pass

    def filter_emoji(self, desstr, restr=''):
        # 过滤除中英文及数字以外的其他字符
        # 原生字符串加 r，\符号不转义；转义字符串
        res = re.compile(WX_CONTENT_PAT)
        return res.sub(restr, desstr)

    def check_price(self, price_info):
        price = self.filter_emoji(price_info)
        price_ag = aigou(price)
        prd_temp = price_ag.GetProductList()
        if prd_temp[0] == 0:
            return prd_temp[1]
        else:
            prd_list = prd_temp[1]
        form_temp = price_ag.GetFormList()
        if form_temp[0] == 0:
            return form_temp[1]
        else:
            form_list = form_temp[1]
        price_temp = price_ag.GetPriceList(prd_list, form_list)
        if price_temp[0] == 0:
            return price_temp[1]
        else:
            price_list = price_temp[1]
        price_db = aigou_db()
        price_db.insert_price(price)
        ret_str = "商品 单数 分销 团购 返利\n"
        for line in price_list:
            ret_str += "%s %d %.2f %.2f %.2f\n" % (line['name'],line['count'],line['fenxiao'],line['tuangou'],line['fanli'])
        return ret_str

    def cal_order(self,order_info=''):
        agdb = aigou_db()
        price = agdb.find_price()
        order = self.filter_emoji(order_info)
        order_ag = aigou(price, order)
        ret = order_ag.cal()
        if ret[0] == 1:
            order_db = aigou_db()
            order_db.insert_order(order)
            order_db.insert_result(ret[1])
            return ret[1]
        else:
            return ret[1]

