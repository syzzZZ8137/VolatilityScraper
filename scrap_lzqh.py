# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 16:04:08 2018

@author: gxjy-003 yizhou
"""

import requests
import pandas as pd
from lxml import etree
from selenium import webdriver
import datetime as dt

#打开网页
#option = webdriver.ChromeOptions()
#option.add_argument('headless')
#brs = webdriver.Chrome(options=option)

#打开网页
brs = webdriver.Chrome()
URL = 'http://www.luzhengqh.com/rest/weixin/otcpricelist' #网页地址
brs.get(URL) 
brs.implicitly_wait(2)
request_URL = 'http://www.luzhengqh.com/rest/weixin/getOptionPrice'

#
#calender_month = brs.find_element_by_xpath('//*[@id="seldate"]')
#calender_month.click()
#
#cal_day = brs.find_element_by_xpath('/html/body/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr/td[3]/div/div[4]/div[1]/div[1]/div[1]/div[19]/div')
#cal_day.click()
#
#confirm = brs.find_element_by_xpath('/html/body/div[3]/div/div[2]/div[2]/div[3]/span[1]/span')
#confirm.click()
#
#table = brs.find_element_by_xpath('/html/body/div[1]/div/table')
#tab = table.get_attribute('innerHTML')
#tdf = pd.read_html('<table>'+tab+'</table>', header = 0)[0]
#tdf.columns

#table_html = 

def parse_symbol_month(contractcode):
    '''
    返回字符串 symbol, expiry_month
    contractcode前半部分为标的:symbol, 后半部分为expiry_month:到期月份(3-4位数字, YYMM或YMM格式)
    '''
    i = 0
    symbol = ''
    expiry_month = ''
    while i<len(contractcode):
        if contractcode[i].isdecimal() == False:
            symbol += contractcode[i]
        else: 
            expiry_month += contractcode[i]
        i += 1
    return symbol, expiry_month
#symbol, expiry_month = parse_symbol_month(contractcode)
    


#contractcode = 'A1901'; expiryDate = '2018-11-22'
def fetch_contract_quotes(contractcode, expiryDate):
    
    '''
    # 检查 ->Network->Headers
    # General：  Request URL
    # Form Data 作为查询字典data
    '''
    global request_URL
#    request_URL = 'http://www.luzhengqh.com/rest/weixin/getOptionPrice'
    # post qingqiu
    rsp = requests.post(request_URL,
            data={'contractcode': contractcode, 'expiryDate': expiryDate})   
    # rsp.headers = {'Server': 'TWebAP/1.0.8.28', 'Date': 'Mon, 22 Oct 2018 09:22:51 GMT', 'Content-Type': 'text/html;charset=UTF-8', 'Transfer-Encoding': 'chunked', 'Connection': 'keep-alive', 'X-Frame-Options': 'SAMEORIGIN', 'Pragma': 'no-cache', 'Expires': 'Thu, 01 Jan 1970 00:00:00 GMT', 'Cache-Control': 'no-cache, no-store'}
    j = rsp.json() #dict, j.keys(): dict_keys(['attributes', 'obj', 'msg', 'jsonStr', 'success'])
    price_df = pd.DataFrame(j['obj']['priceList'])
    #标准化
    price_df.columns = ['call_bid', 'call_ask', 'strike_price', 'put_bid', 'put_ask'] #Index(['call1', 'call2', 'optPrice', 'put1', 'put2'], dtype='object')
    # str -> float
    price_df = price_df.astype(float) #转为小数
    decimals = pd.Series([2, 2, 2, 2, 2], price_df.columns) #保留2位小数
    price_df = price_df.round(decimals)
    symbol, expiry_month = parse_symbol_month(contractcode)
    underlying_price = j['obj']['futurePrice']
    
    #evaluation_date
    #update_time #一天几次？
    return price_df
    

def construct_termstructure():
    '''
    在evaluation_date 对标的 contractcode，建立期限结构
    '''
    pass
'''
    price_df.call_mid = (price_df.call_ask + price_df.call_bid)/2
    price_df.put_mid = (price_df.put_ask + price_df.put_bid)/2
'''

SYMBOL_DATA = dict()

def update_symbol_collections():
    '''
    返回字典
    '''
    global SYMBOL_DATA
    
    
    brs = webdriver.Chrome()
    brs.get('http://www.luzhengqh.com/rest/weixin/otcpricelist') #网页地址
    brs.implicitly_wait(2)
    
    products = brs.find_element_by_xpath('//*[@id="codesel"]')       
    contractcodeList = products.text.split()
    
    products_names = products.find_elements_by_tag_name('option') 

    for opt in products_names:
        SYMBOL_DATA[opt.get_attribute('value')] = None
    brs.quit()
    #字典SYMBOL_DATA以contractcodeList中的所有元素为key
    
    for _contractcode in SYMBOL_DATA.keys():
        SYMBOL_DATA[_contractcode] = fetch_quote_cycle(_contractcode) # list of date strings
               
        
def fetch_quote_cycle(contractcode):        
    '''
    点击挂钩标的下拉菜单，选中contractcode，抓取到期日？？并返回
    '''
    #dt.datetime.strptime('2018-10-22', '%Y-%m-%d')+dt.timedelta(14)
    
    #request晚于合约到期月份的日期，抓取返回的msg中 不超出范围 的最晚日期
    
    global request_URL
    #request_URL = 'http://www.luzhengqh.com/rest/weixin/getOptionPrice'
    
    symbol, expiry_month = parse_symbol_month(contractcode)
    expDateNum = 20000000 + int(expiry_month)*100 + 28
    expDate = dt.datetime.strptime(str(expDateNum), '%Y%m%d')
    expDate_str = expDate.strftime("%Y-%m-%d")
    rsp = requests.post(request_URL,
            data={'contractcode': contractcode, 'expiryDate': expDate_str})
    j = rsp.json() 
    if not j['success']:
        msg = j['msg'] #'到期日超出范围，请选择小于等于2018-12-14的日期！'
        last_quoteDate = msg[-14:-4]
    
#        evaluationDate = brs.find_element_by_xpath('//*[@id="seldate"]')       
    
        expiryDate = last_quoteDate
        rsp = requests.post(request_URL, data={'contractcode': contractcode, 'expiryDate': expiryDate})
        rsp_headers = rsp.headers
        timestamp = rsp_headers['Date']
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
    