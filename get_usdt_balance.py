#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
import datetime
import time
import xlrd
import xlwt
from xlutils.copy import copy

# tronscan 查询余额地址           
usdt_info_from_tronscan_url = "https://apilist.tronscan.org/api/token_trc20/holders?sort=-balance&start="
# 合约地址
contract_address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t" 
# trongrid查询余额地址
trongrid_url = "https://api.trongrid.io/v1/accounts/"
#add browser headers
headers={
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Cookie':'__cfduid=da90fabee5f4d96a316a104f96f0476bd1552904746; gtm_session_first=Mon%20Mar%2018%202019%2018:24:58%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4); _ga=GA1.2.1809757759.1552904698; _gid=GA1.2.1536504574.1552904698; _fbp=fb.1.1552904698688.846897282; __gads=ID=df0e159e39a6f1bc:T=1552904750:S=ALNI_Mb2GRbqU9zQCWB8Lc_nA4QIsEBTjw; cmc_gdpr_hide=1; gtm_session_last=Mon%20Mar%2018%202019%2020:24:30%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4); _awl=2.1552911928.0.4-68ecec8c-3d6c2c480ef438cc86a4fd41099005f0-6763652d75732d7765737431-5c8f8e38-0'
}


# get usdt info from trongrid
def get_trc20token_balanceOf_from_trongridV1(address):
    trc20token_balanceOf_from_trongrid = 0
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "from_trongrid    address:" + address)
    usdt_info_trongrid1 = requests.get(trongrid_url+address,headers=headers,timeout=20)
    usdt_info_trongrid_statuscode = usdt_info_trongrid1.status_code
    usdt_info_trongrid = usdt_info_trongrid1.json() # 获取address的余额信息
    if usdt_info_trongrid_statuscode ==200:
        if len(usdt_info_trongrid['data']) != 0:  # 如果data字段不为0，进入判断体，如果data字段长度为0，则余额为0
            for i in usdt_info_trongrid['data'][0]['trc20']: 
                for key,value in i.items():
                    if key == contract_address:
                        print("=====key:"+key+" value:"+str(value)+"========")
                        trc20token_balanceOf_from_trongrid = value             
        else:
            trc20token_balanceOf_from_trongrid = 0
    else:
        time.sleep(60)
        get_trc20token_balanceOf_from_trongridV1(address)
    print(trc20token_balanceOf_from_trongrid)
    return trc20token_balanceOf_from_trongrid


# get usdt info from tronscan
def get_trc20token_info_from_tronscan(tronscan_url,excel_path):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===========from_tronscan=============")
    usdt_info_form_tronscan_content1 = requests.get(tronscan_url,headers=headers,timeout=20)
    print(usdt_info_form_tronscan_content1.status_code)
    usdt_info_form_tronscan_content = usdt_info_form_tronscan_content1.json() # 获取tronscan 上USDT部分holder的余额信息
    if usdt_info_form_tronscan_content1.status_code == 200:
        for i in range(len(usdt_info_form_tronscan_content['trc20_tokens'])):
            address = usdt_info_form_tronscan_content['trc20_tokens'][i]['holder_address'] # 获取holders address
            balance_from_tronscan = usdt_info_form_tronscan_content['trc20_tokens'][i]['balance'] # 获取holders tronscan上返回的余额
            balance_from_trongrid_V1_API = get_trc20token_balanceOf_from_trongridV1(address) # 获取holders trongrid上返回的余额
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 获取当前时间
            print("balance_from_tronscan:" + str(balance_from_tronscan))
            print("balance_from_trongrid_V1_api:" + str(balance_from_trongrid_V1_API))
            if balance_from_tronscan != balance_from_trongrid_V1_API: # 判断余额是否相等，如果不相等，写入excel表
                value = [[address,balance_from_tronscan,balance_from_trongrid_V1_API,time],]
                write_diff_trc20token_info_to_excel(excel_path,value)
    else:
        print("====status_code error,will wait 60s tra again.")
        time.sleep(60)
        get_trc20token_info_from_tronscan(tronscan_url,excel_path)
    return 

def create_excel_xls(path, sheet_name, value):
    index = len(value)  # 获取需要写入数据的行数
    workbook = xlwt.Workbook()  # 新建一个工作簿
    sheet = workbook.add_sheet(sheet_name)  # 在工作簿中新建一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            sheet.write(i, j, value[i][j])  # 像表格中写入数据（对应的行和列）
    workbook.save(path)  # 保存工作簿
    print("xls格式表格初始化数据成功！")

def write_diff_trc20token_info_to_excel(path, value):
    index = len(value)  # 获取需要写入数据的行数
    workbook = xlrd.open_workbook(path)  # 打开工作簿
    sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
    worksheet = workbook.sheet_by_name(sheets[0])  # 获取工作簿中所有表格中的的第一个表格
    rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
    new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
    new_worksheet = new_workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            new_worksheet.write(i+rows_old, j, value[i][j])  # 追加写入数据，注意是从i+rows_old行开始写入
    new_workbook.save(path)  # 保存工作簿
    print("xls格式表格【追加】写入数据成功！")


def main():
    #--------------
    # 初始化excel表
    #--------------
    path = "/Users/tron/Desktop/usdt_check/usdt_check.xls" # excel表路径
    sheet_name = "usdt_balance_diff_check" 
    value_title = [["address", "tronscan_balance", "trongrid_balance", "check_time"],]
    create_excel_xls(path,sheet_name,value_title)
    #--------------
    # 对比余额是否相等
    #--------------
    start_num = 20
    for i in range(0,500):
        print("********************第" + str(i+1) + "页********************")
        tronscan_url = usdt_info_from_tronscan_url + str(i*start_num) + "&limit=20" + "&contract_address=" + contract_address
        print(tronscan_url)
        get_trc20token_info_from_tronscan(tronscan_url,path)
        time.sleep(30)
    print("-----CHECK DONE!!!-----")

if (__name__ == "__main__"):
    main()
    #get_trc20token_balanceOf_from_trongridV1("TQc1yCwBn9FQ94N1SdEavqjPE4YtSATi6a")

