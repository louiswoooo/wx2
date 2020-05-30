# 需要加上对于小数的处理
# 需要加上对订单空格的兼容
import re
# 订单信息的分割器
ORDER_SPLIT = '[。，., \n]'

class aigou:
    def __init__(self, price='', order=''):
        self.price = price
        self.order = order

    # 获取以包含 start 关键字的行开头,包含 end 关键字结尾的行的中间信息
    def SliceInfo(self, info, start, end):
        pat1 = r".*" + start + ".*"
        find_list1 = re.findall(pat1, info)
        if len(find_list1) == 0:
            return ''
        else:
            start_line = find_list1[0]

        pat2 = r".*" + end + ".*"
        find_list2 = re.findall(pat2, info)
        if len(find_list2) == 0:
            return ''
        else:
            end_line = find_list2[0]

        pat = start_line + "(.+)" + end_line
        info = re.findall(pat, self.price, re.S | re.M)[0]
        return info

    # 获取产品列表，获取不到返回 0 和错误信息，成功返回 1 和列表
    def GetProductList(self):
        res = re.findall('.*返利.*', self.price)      #查找返利行
        if len(res)>0:
            fanli_info = res[-1]
        else:
            return 0, '报价信息当中没有找到返利关键字！'
        fan_list = fanli_info.split('，')                #分割返利信息
        fanli_list = []
        for line in fan_list:
            fanli_dict = {}
            res_name = re.findall('(.+)无返利', line)      #查找无返利行
            if len(res_name)>0:
                fanli_dict['name'] = res_name[0]
                fanli_dict['fanli'] = 0
                fanli_list.append(fanli_dict)
                continue
            res_name = re.findall('(.+)返利', line)       #查找返利商品名和价格
            res_fanli = re.findall('\d+', line)
            if len(res_name)>0 and len(res_fanli)>0:
                fanli_dict['name'] = res_name[0]
                fanli_dict['fanli'] = float(res_fanli[-1])
                fanli_list.append(fanli_dict)
                res = re.findall('其他',fanli_dict['name'])   #查找其他返利
                if len(res)>0:
                    other_fanli = fanli_dict['fanli']           #设置一个其他返利变量
                else:
                    return 0, '在返利信息“%s”当中没有找到商品返利信息！' % line
            else:
                return 0, '在返利信息“%s”当中没有找到商品返利信息！'%line

        info_temp = self.SliceInfo(self.price, "报价", "下单格式")        #查找产品报价信息
        info = info_temp
        if len(info) == 0:
            return 0, '报价信息当中找不到报价或下单格式关键字！'
        prd_info = info.split("\n")             #以行为分割，信息大于4个留下
        temp_list=[]
        for line in prd_info:
            if len(line) > 4:
                pat = '\d*[.，、。]*(.*)'          #过滤产品列表当中的各种前缀字符，数字和标点符号
                res = re.findall(pat, line)
                temp_list.append(res[0])
        prd_list = []
        for prd_line in temp_list:          #获取商品报价信息
            prd_dict = {}
            name = prd_line.split('，')[0]   #获得商品全名
            pat = ".*分销(\d*)"
            res = re.findall(pat, prd_line)
            if res:
                fenxiao = float(res[0])     #获得分销报价
            else:
                return 0, '找不到产品%s的分销价格'%prd_line
            pat = ".*团购(\d*)"               #获得团购报价
            res = re.findall(pat, prd_line)
            if res:
                tuangou = float(res[0])
            else:
                return 0, '找不到产品%s的团购价格'%prd_line
            prd_dict['name'] = name
            prd_dict['fenxiao'] = fenxiao
            prd_dict['tuangou'] = tuangou
            for fanli_dict in fanli_list:       #通过配对返利名称，合并返利信息与产品报价信息
                pat_fanli = fanli_dict['name'].replace('.', '[.]')
                res = re.findall(pat_fanli, prd_dict['name'])
                if len(res)>0:
                    prd_dict['fanli'] = fanli_dict['fanli']     #如果匹配到名称，设置商品返利
                    break;
            if fanli_dict == fanli_list[-1]:    #如果循环结束还没有找到这个商品名称，则为其他返利
                prd_dict['fanli'] = other_fanli;
            prd_list.append(prd_dict)
        return 1, prd_list

    # 获取订单格式列表，获取不到返回 0 和原因
    def GetFormList(self):
        info_temp = self.SliceInfo(self.price, "下单格式", "返利")
        info = info_temp
        if len(info) == 0:
            return 0, '团购报价当中找不到下单格式或返利关键字！'
        form_info = info.split("\n")
        form_list = []
        for line in form_info:
            form_dict = {}
            if len(line) > 4:
                temp = line.split('。')
                name = temp[0]
                count = temp[1]
                if name and count:
                    form_dict['name'] = name
                    form_dict['count'] = int(count)
                else:
                    return 0, '订单格式当中“%s”找不到商品或单份数量！'%line
                form_list.append(form_dict)
        return 1, form_list

    # 合并产品列表和格式列表得到价格列表，由于产品列表和格式列表名称不一致，需要做产品名称匹配
    # 匹配的方式是先取 form_list name 中头两个字 对prd_list name 进行匹配，如果只有唯一结果，就算成功
    # 如果>2 就取 3 个字，如此直到匹配成功为止
    #如果有 =0 的情况，就取 prd_list name 取匹配 form_list name 方法类似
    def GetPriceList(self, prd_list, form_list):
        Price_list = []
        for form_line in form_list:         #取form_list 每一行进行匹配
            Price_dict = {}
            i = 2                                   #从两个字开始
            while i<len(form_line['name']):         #直到名字结束
                count = 0                           #匹配计数器
                form_name_short = form_line['name'][0:i]
                for prd_line in prd_list:               #到 prd_list 当中去匹配name
                    if len(re.findall(form_name_short, prd_line['name']))>0:
                        prd_pt = prd_line               #指针指向匹配的那个
                        count += 1
                if count == 1:                          #匹配完毕如果总数 =1，则合并
                    Price_dict['name'] =  form_name_short
                    Price_dict['count'] = form_line['count']
                    Price_dict['fenxiao'] = prd_pt['fenxiao']
                    Price_dict['tuangou'] = prd_pt['tuangou']
                    Price_dict['fanli'] = prd_pt['fanli']
                    Price_list.append(Price_dict)
                    break
                elif count > 1:             #如果匹配到多个，说明有多个重名，加字数
                    i += 1
                else:                       #如果匹配不到，转到取prd_list 当中去取 name 匹配 form_list
                    for temp_line in prd_list:
                        prd_name_short = temp_line['name'][0:2]
                        if len(re.findall(prd_name_short, form_line['name'])) >0:
                            Price_dict['name'] = prd_name_short
                            Price_dict['count'] = form_line['count']
                            Price_dict['fenxiao'] = temp_line['fenxiao']
                            Price_dict['tuangou'] = temp_line['tuangou']
                            Price_dict['fanli'] = temp_line['fanli']
                            Price_list.append(Price_dict)
                            break;
                        if temp_line == prd_list[-1]:
                            return 0, '报价表中找不到这个产品：%s'%form_line
                    break
            if i>= len(form_line['name']):
                return 0, '报价表中找不到这个产品：%s'%form_line
        return 1, Price_list

    #查找订单列表当中的信息，形成订单列表，其中商品通过 price_list 获取
    def GetOrderList(self, price_list):
        Order_list = []
        prd_list = []
        for line in price_list:             #获取商品名称的列表
            prd_list.append(line['name'])
        info = self.order
        temp_list = []
        temp0_list = info.split('\n')
        for line in temp0_list:             #简化订单有用信息
            if len(line)>4:
                temp_list.append(line)
        for prd_name in prd_list:           #轮询统计 prd_list 当中的商品名称
            i = 0
            all_count = 0
            pat = prd_name.replace('.', '[.]')      #商品名字种的.替换
            while i<len(temp_list):         #轮询订单列表当中的行
                res = re.findall(pat, temp_list[i])
                if len(res):                                #如果找到商品关键字
                    res1 = re.findall('。 *(\d+) *$', temp_list[i])      #查找数量
                    if res1:
                        all_count += int(res1[0])           #如果找到数量则累加
                    else:
                        return 0, '订单信息 %s 当中找不到商品的数量'%temp_list[i]
                i += 1
            if all_count>0:                 #形成订单列表
                Order_list.append({'name':prd_name, 'all_count':all_count})

        return  1, Order_list


    def cal(self):
        prd_ret = self.GetProductList()
        if prd_ret[0] == 0:
            return 0,prd_ret[1]
        else:
            prd_list = prd_ret[1]
        form_ret = self.GetFormList()
        if form_ret[0] == 0:
            return 0,form_ret[1]
        else:
            form_list = form_ret[1]
        price_ret = self.GetPriceList(prd_list, form_list)
        if price_ret[0] == 0:
            return 0,price_ret[1]
        else:
            price_list = price_ret[1]
        for line in price_list:
            print(line)

        order_ret = self.GetOrderList(price_list)
        if order_ret[0] == 0:
            return 0,order_ret[1]
        else:
            order_list = order_ret[1]
        for line in order_list:
            print(line)

        all_list = []
        ret_str = ''
        for order_line in order_list:
            all_dict = {}
            for price_line in price_list:
                if price_line['name'] == order_line['name']:
                    all_dict['name'] = order_line['name']
                    all_dict['num'] = order_line['all_count'] / price_line['count']
                    all_dict['fenxiao'] = price_line['fenxiao'] * all_dict['num']
                    all_dict['tuangou'] = price_line['tuangou']*all_dict['num']
                    all_list.append(all_dict)
                    ret_str += "%s，数量：%d，成本：%d\n" % (all_dict['name'],all_dict['num'],all_dict['fenxiao'] )
                    break
        total_num = 0
        total_fenxiao = 0
        total_tuangou = 0
        for line in all_list:
            total_num += line['num']
            total_fenxiao += line['fenxiao']
            total_tuangou += line['tuangou']
        ret_str += "总%d单\n总货款%d\n利润%d\n应付%d" % (total_num, total_tuangou,total_tuangou - total_fenxiao,total_fenxiao)
        return 1,ret_str









