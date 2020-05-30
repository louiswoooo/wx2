import hashlib
import pymysql
import xml.etree.cElementTree as et
import muban
from time import time
from flask import redirect,abort,url_for,Flask,render_template,request
from aigou import *
import re
from dbmg import aigou_db
from aigoumid import *

#电话号码的过滤条件
PHONE_PAT = ".*(1[35678]\d{9}).*"

db = pymysql.connect(host="localhost", user="root", \
                     password="genius", database="dict", charset="utf8")
cur = db.cursor()
app = Flask(__name__)

#微信信息的过滤器定义，只保留指定的编码字符，
# 包括中文、英文大小写、数字等，
WX_CONTENT_PAT = "[^\u4e00-\u9fa5^a-z^A-Z^0-9^\n^ ^(^)^+^-^.^:^/^ ^（^）^，^。^：^、^＋^-]"

# def filter_emoji(info, restr=''):
#     # 过滤表情
#     try:
#         co = re.compile(u'[\U00010000-\U0010ffff]')
#     except re.error:
#         co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
#     return co.sub(restr, info)

def filter_emoji(desstr,restr=''):
    #过滤除中英文及数字以外的其他字符
    # 原生字符串加 r，\符号不转义；转义字符串
    res = re.compile(WX_CONTENT_PAT)
    return res.sub(restr, desstr)

def DoQuery(word):
    sql_sen="select interpret from words where word='%s'"%word
    print(sql_sen)
    try:
        cur.execute(sql_sen)
    except Exception as e:
        print(e)
        db.connect()
        cur.execute(sql_sen)
    interpret=cur.fetchone()
    if interpret:
        result=interpret[0].split("。")
        print("result count is %d"%len(result))
        return result[0]
    else:
        return "找不到这个单词"

@app.route('/')
def index():
    user = { 'nickname': '天才' } # fake user
    posts = [ # fake array of posts
        {
            'author': { 'nickname': 'John' },
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': { 'nickname': 'Susan' },
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html",
        title = 'Home',
        user = user,
        posts = posts)

@app.route('/ag/instruct')
def ag_ins():
    user = { 'nickname': '天才' } # fake user
    posts = [ # fake array of posts
        {
            'author': { 'nickname': 'John' },
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': { 'nickname': 'Susan' },
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("instruct.html",
        title = 'Home',
        user = user,
        posts = posts)

#天才AI实验室公众号响应的地址
@app.route('/wx', methods=['GET', 'POST'])
def wx():
    if request.method == 'GET':
        signiture = request.args.get('signiture')
        timestamp = request.args.get('timestamp')
        echostr = request.args.get('echostr')
        nonce = request.args.get('nonce')
        token = 'louiswoo'
        if len(request.args) == 0:
            return "hello, this is handle view!!!"
        list = [token, timestamp, nonce]
        list.sort()
        s = list[1] + list[0] + list[2]
        hashcode = hashlib.sha1(s.encode('utf8')).hexdigest()
        if hashcode == signiture:
            print(request.data)
            return echostr
        else:
            print('wechat verify failed!')
            return ""

    elif request.method == 'POST':
        xmldata = request.data
        print(xmldata)
        xml_rec = et.fromstring(xmldata)

        ToUserName = xml_rec.find('ToUserName').text
        fromUser = xml_rec.find('FromUserName').text
        MsgType = xml_rec.find('MsgType').text
        # MsgId = xml_rec.find('MsgId').text

        if MsgType == 'text':
            Content = xml_rec.find('Content').text
            intepret = DoQuery(Content)
            if intepret == None:
                intepret = '找不到这个单词！'
            ret_str = muban.replay_muban('text') % (fromUser, ToUserName, int(time()), intepret)
            return ret_str

        elif MsgType == 'voice':
            Recognition = xml_rec.find('Recognition').text
            ret_str = muban.replay_muban('text') % (fromUser, ToUserName, int(time()), Recognition)
            return ret_str

#要像花儿一样灿烂公众号响应的地址
@app.route('/ag',methods=['GET','POST'])
def ag():
    if request.method == 'GET':
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        echostr = request.args.get('echostr')
        nonce = request.args.get('nonce')
        token = 'louiswoo'
        if len(request.args)==0:
            return "hello, this is handle view"
        list = [token, timestamp, nonce]
        list.sort()
        s = list[0]+list[1]+list[2]
        hashcode = hashlib.sha1(s.encode('utf-8')).hexdigest()
        if hashcode == signature:
            return echostr
        else:
            print('验证失败')
            return ""
    elif request.method=='POST':
        xmldata=request.data
        #print(xmldata)
        xml_rec=et.fromstring(xmldata)

        ToUserName = xml_rec.find('ToUserName').text
        fromUser = xml_rec.find('FromUserName').text
        MsgType = xml_rec.find('MsgType').text
        # MsgId = xml_rec.find('MsgId').text

        if MsgType == 'event':
            event = xml_rec.find('Event').text
            if event == 'subscribe':
                temp_str = '(^-^)  您好！\n欢迎进入爱购订单核算中心！' \
                           '请您花一点时间先了解一下中心的强大功能，请点击' \
                           '<a href="http://119.3.233.56/ag/instruct">使用说明</a>！'
                ret_str = muban.replay_muban('text') % (fromUser, ToUserName, int(time()), temp_str)
            else:
                temp_str = '谢谢使用，期待再次见到您，拜拜咯！！！'
                ret_str = muban.replay_muban('text') % (fromUser, ToUserName, int(time()), temp_str)
            return ret_str

        elif MsgType=='voice':
            Recognition = xml_rec.find('Recognition').text
            ret_str = muban.replay_muban('text') % (fromUser,ToUserName,int(time()),Recognition)
            return ret_str

        elif MsgType=='text':
            Content = filter_emoji(xml_rec.find('Content').text)
            title = Content.split('\n')[0]
            pat = r'内部报价'                   #有“内部报价”关键字就认为是报价信息
            res = re.findall(pat, title)
            if res:
                ag = aigoumid()
                temp_str = ag.check_price(Content)
            elif len(re.findall(PHONE_PAT, Content))>0:
                #有手机号码就判定为订单信息
                order = Content
                ag = aigoumid()
                temp_str = ag.cal_order(order)
                ret_str = muban.replay_muban('text') % (fromUser, ToUserName, int(time()), temp_str)
            else:
                temp_str = '不知道你发给我的是什么！'
            ret_str =muban.replay_muban('text') % (fromUser,ToUserName,int(time()),temp_str)
            return ret_str

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)