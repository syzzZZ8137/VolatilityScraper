# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 15:01:27 2018

@author: gxjy-003 yizhou
"""

# -*- coding: utf-8 -*-
# @Time    : 2018/10/19 14:24
# @Author  : Xin Zhang
# @File    : test_scrap.py

import requests
import pandas as pd
from lxml import etree
from selenium import webdriver
import datetime
import time


def fetch_quote_cycle(symbol):
    global header
    rsp = requests.post(
        'http://otc.gtjaqh.com/otc-project/otc/getquotecycle',
        data={
            'productId': symbol},
        headers=header)
    s = '<select>' + rsp.json()['quoteCycle'] + '</select>'
    h = etree.HTML(s)
    h_l = h.xpath('//select/*')
    return [opt.values()[-1] for opt in h_l]

'''
def update_symbol_collections():
    global SYMBOL_DATA
    # from selenium.webdriver.support.ui import Select
    option = webdriver.ChromeOptions()
    option.add_argument('headless')

    brs = webdriver.Chrome(options=option)

    brs.get('http://otc.gtjaqh.com/otc-project/otcprice.html')
    brs.implicitly_wait(2)

    # products = brs.find_element_by_xpath('//*[@id="productCode"]')

    # btn = brs.find_element_by_xpath('//*[@id="table"]/thead/tr/th/div[1]/button')
    # btn.click()

    products = brs.find_element_by_xpath('//*[@id="productCode"]')   
    products_names = products.find_elements_by_tag_name('option') 

    # slc = Select(products)

    # slc.select_by_value('hc')

    # brs.find_element_by_xpath('//*[@id="productCode"]/option[13]').click()

    for opt in products_names:
        SYMBOL_DATA[opt.get_attribute('value')] = None

    brs.quit()

    for ky in SYMBOL_DATA.keys():
        SYMBOL_DATA[ky] = fetch_quote_cycle(ky)
        
'''

header = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'otc.gtjaqh.com',
    'Origin': 'http://otc.gtjaqh.com',
    'Pragma': 'no-cache',
    'Referer': 'http://otc.gtjaqh.com/otc-project/otcprice.html',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

SYMBOL_DATA = dict()  # symbol list


def parse_otcprice(js_otc):
    res = '<table>' + js_otc + '</table>'
    tmp = pd.read_html(res)[0]
    tmp.columns = ['call_bid', 'call_ask', 'strike', 'put_bid', 'put_ask']
    return tmp


def parse_content(js):
    dt_str = datetime.datetime.now().date().strftime('%Y-%m-%d ')
    tmp = parse_otcprice(js['otcprice'])
    return tmp.assign(spot_price=float(js['spotPrice']),
                      instrument_id=js['instrumentId'],
                      update_time=dt_str + js['updateTime'])


def fetch_one_symbol(product_id, cycle):
    global header
    req = {'productId': product_id,
           'quoteCycle': cycle}
    resp = requests.post(
        'http://otc.gtjaqh.com/otc-project/otc/getprice',
        data=req,
        headers=header)

    tdf = parse_content(resp.json())

    print('=' * 80)
    print(tdf)
    print('=' * 80)


if __name__ == '__main__':
    print('\nUpdating product list....')
    update_symbol_collections()

    print('\nDisplay the price data....')
    for p_id, cycle_list in SYMBOL_DATA.items():
        for c in cycle_list:
            fetch_one_symbol(p_id, c)
            time.sleep(1)