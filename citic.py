# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 10:38:45 2018

@author: Jax_GuoSen
"""

from selenium import webdriver
import pandas as pd
import time
import urllib.request
import os
import shutil
import ssl
from implied_vol import implied_vol

def url_open(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)    
    html = driver.page_source
    
    #ssl._create_default_https_context = ssl._create_unverified_context
    #req=urllib.request.Request(url)
    #req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
    #time.sleep(5)
    #response = urllib.request.urlopen(req)
    #html=response.read().decode('utf-8')#'gb18030') #make it to be string
    #print(html[10000:12000])
    #print(type(html))
    return html

def find_price(html,lastpos,start,end):
    temp1 = html.find(start,lastpos)
    temp2 = html.find(end,lastpos)
    #print(html[temp1+1:temp2])
    price = float(html[temp1+1:temp2])
    return price

def find_info(html):
    #pass
   #"GoToUrl('RU1901','SHF');">
    current = html.find('id="lbl_LastPrice"')
    current = find_price(html,current,'>','<')
    info = []
    a = html.find('<tbody id="TargetContractOffer">')
    while a!=-1:
        cb = html.find('CallBuyPrice',a)
        cs = html.find('CallSellPrice',cb)
        s = html.find('LastPrice',cs)
        pb = html.find("PutBuyPrice",s)
        ps = html.find("PutSellPrice",pb)
        
        callbuy = find_price(html,cb,'>','<')
        callsell = find_price(html,cs,'>','<')
        strike = find_price(html,s,'>','<')
        putbuy = find_price(html,pb,'>','<')
        putsell = find_price(html,ps,'>','<')
        
        info.append([callbuy,callsell,strike,putbuy,putsell])
        a = html.find('CallBuyPrice',ps) #find next
        
    return current,info
    
def save_info(folder,text,page):
    #pass
    f=open(r"C:\Users\Jax_GuoSen\Desktop\yingjiesheng","wb")
    for each in text:
        f.write(each.encode('utf-8'))
        
    f.close()
    
def downloadinfo(exchange,code,maturity,folder='Citic'):
    #if os.path.exists(folder): #if exits, delete
        #shutil.rmtree(folder)
    #os.mkdir(folder)  #create a folder in current path
    #os.chdir(folder)  #change the save path
    print('crawler begins')
    
    url = 'http://zb.citicsf.com/otcoption/CiticsfFinance/Option/TargetContractOffer.aspx?code=%s&exchangeCode=%s&tradingDate=%s'%(code,exchange,maturity)
    html = url_open(url)
    S,V = find_info(html)
    #save_info(folder,text,i+1)
    print('crawler completes')
    
    return S,V
    
def cal_vol(exchange,code,maturity):
    vol = []
    S,V = downloadinfo(exchange,code,maturity)
    maturity = maturity.split('-')
    maturity = pd.datetime(int(maturity[0]),int(maturity[1]),int(maturity[2]))
    T = (maturity-pd.datetime.now()).days/365
    for each in V:
        cb = implied_vol(S,0,each[0],each[2],T,'认购')
        cs = implied_vol(S,0,each[1],each[2],T,'认购')
        pb = implied_vol(S,0,each[3],each[2],T,'认沽')
        ps = implied_vol(S,0,each[4],each[2],T,'认沽')
        vol.append([cb,cs,each[2],pb,ps])
    vol = pd.DataFrame(vol,columns=['callbuy_vol','callsell_vol','strike','putbuy_vol','putsell_vol'])
    return S,vol

if __name__=='__main__':
    #-----------------输入--------------
    exchange='CZC'
    code='CF901'
    maturity='2018-10-16'
    #-----------------输入--------------
    
    S,vol = cal_vol(exchange,code,maturity)
    
    print('---------------------------参数信息-----------------------------')
    print('报价公司：','中信中证资本')
    print('交易所：',exchange)
    print('品种：',code)
    print('到期日：',maturity)
    print('实时标的价格：',S)

    print('--------------------------T字型波动率---------------------------')
    print(vol)



# download picture
#response= urllib.request.urlopen('http://wx2.sinaimg.cn/large/661eb95cly1fgiox0w8yjj20u00wvq5e.jpg')
#mm_img=response.read()
#with open('mm.jpg','wb') as f:  #wb 2jinzhi
#    f.write(mm_img)
