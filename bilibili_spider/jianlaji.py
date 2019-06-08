# -*- coding: utf-8 -*-
import requests
import time
import json
import pymysql
import re
import logging
import Downloader
import random

from multiprocessing.dummy import Pool as ThreadPool

logging.basicConfig(level=logging.INFO,  
                    format='%(asctime)s - %(levelname)s - %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename='/home/veetsin/qwerty/Projects/fun/bilibili_spider/test.log',  
                    filemode='a')  
def get_url(number_subzone=1):
#获得手机平板分区的视频列表
    urls=[]
#    url = 'http://api.bilibili.com/x/web-interface/newlist?rid=191&pn='
#    for i in range(1, 12):#524 actually , totally653*12
#        urls.append(url + str(i) + '&ps=50')
#    if number_subzone==4:
#        url = 'http://api.bilibili.com/x/web-interface/newlist?rid=190&pn='
#        for i in range(1, 914):
#            urls.append(url + str(i) + '&ps=50')
#        url = 'http://api.bilibili.com/x/web-interface/newlist?rid=189&pn='
#        for i in range(1, 1649):
#            urls.append(url + str(i) + '&ps=50')
    url = 'http://api.bilibili.com/x/web-interface/newlist?rid=95&pn='
    for i in range(1, 3700):#4786actually679*7
        urls.append(url + str(i) + '&ps=50')
    return urls

   
#def check_jianlaji(tag_data):
#    for i in range(len(tag_data)):
#        if (tag_data[i]['tag_name'] == u'捡垃圾'):    
#            return i
#    return None

def new_check(set_kw):
    if u'捡垃圾' in set_kw:
        return True
    else:
        return False
    
brand={'小米':0,'华为':1,'荣耀':2, 'oppo':3,'vivo':4,'魅族':5,
       '联想':6,'三星':7,'lg':8,'锤子':9,'一加':10, 
       '谷歌':11,'诺基亚':12,'索尼':13,'sony':103,'苹果':14,'iphone':104,'红米':15}
brand_keys={'lg','oppo','iphone','sony','vivo','一加',
 '三星', '华为','小米','索尼','联想', '苹果', '荣耀','诺基亚', '谷歌', '锤子', '魅族'}
def get_brand(set_kw):
    if (set_kw & brand_keys):
         number = brand[(list(set_kw&brand_keys))[0]]
         if number == 103:
             number = 13
         if number == 104:
             number = 14
         return number
        
    else:
        return -1
        

def get_price(title):
    match_price = re.search(u'(\d*)元',title)
    match_price_alt = re.search(u'(\d*)块',title)
    if match_price:
        return round(float(str2int(match_price.groups()[0])))
    elif match_price_alt:
        return round(float(str2int(match_price_alt.groups()[0])))
    else:
        return -1
        
    
def str2int(totalCount):
    return re.sub("\D", "", totalCount)
    
def get_time_str(pubdate):
    cur_time = time.localtime(pubdate)
    if cur_time[1] < 10:
        month = '0'+str(cur_time[1])
    else:
        month = str(cur_time[1])
#    if cur_time[2] < 10:
#        day = '0'+str(cur_time[2])        
    str_time = str(cur_time[0])+month
    return int(str2int(str_time))


def into_db_video(list_v,cursor,conn):
    for i,dict_v in enumerate(list_v):
        cursor.execute('INSERT INTO video_info(id,av_id,pubdate,brand_id,price,view) VALUES ("%i","%i","%i","%i","%i","%i") ;'
                       %(i+1,dict_v['av_id'],dict_v['pubdate'],dict_v['brand_id'],dict_v['price'],dict_v['view']))
        conn.commit()
        
def into_db_up(list_u,cursor,conn):
    for i,dict_u in enumerate(list_u):
        cursor.execute('INSERT INTO up_info(id,up_id,up_fans,up_videos) VALUES ("%i","%i","%i","%i") ;'
                       %(i+1,dict_u['up_id'],dict_u['up_fans'],dict_u['up_videos']))
        conn.commit()

video_info_list=[]
up_info_list=[]
set_up=set([])
flag = True
u_c_request = Downloader.Downloader()



def get_message(url):
#    logging.info(url[-7])
    time.sleep(random.uniform(1,3))# without multiprocess
    try:
        r = u_c_request.get(url, timeout=5)
#        r = requests.get(url, timeout=5)

        if r.status_code == 200:
            data = json.loads(r.text)['data']['archives']
            for j in range(len(data)):
                pubtime = get_time_str(data[j]['pubdate'])
                if pubtime>201710:
                    av = data[j]['aid']
                    time.sleep(0.1)
                    url_tag = 'https://api.bilibili.com/x/tag/archive/tags?aid='+str(av)
                    tag_data = u_c_request.get(url_tag,timeout=5).json()['data']
                    set_kw = set( i['tag_name'].lower() for i in tag_data )

                    if new_check(set_kw):
                        content = {}
                        content['av_id'] = data[j]['aid']
                        content['pubdate'] = pubtime
                        content['brand_id'] = get_brand(set_kw)
                        content['price'] = get_price(data[j]['title'])
                        content['view'] = data[j]['stat']['view']
    #                   content['danmaku'] = data[j]['stat']['danmaku']
    #                   content['reply'] = data[j]['stat']['reply']
    #                   content['favorite'] = data[j]['stat']['favorite']
    #                   content['coin'] = data[j]['stat']['coin']
                        video_info_list.append(content)
                        
                        up_id = data[j]['owner']['mid']
                        if up_id not in set_up:
                            set_up.add(up_id)
                            cont={}
                            cont['up_id'] = up_id
                            url_up = 'https://api.bilibili.com/x/web-interface/card?mid='+str(up_id)
                            time.sleep(0.1)
                            up_data = u_c_request.get(url_up,timeout=5).json()['data']
                            cont['up_fans'] = up_data['follower']
                            cont['up_videos'] = up_data['archive_count']
                            up_info_list.append(cont)
#                            logging.info(" data_amount:%i" % (len(video_info_list)))
#                            print ("data_amount:%i" % (len(video_info_list)))
                else:
                    global flag 
                    flag = False
                    break
        else:
            logging.info("请求网页失败！")
    except Exception as e:
        logging.info(e)
        print(e)

#CREATE TABLE jianlaji(id varchar(10), av_id varchar(50), pubdate varchar(50), title varchar(256), view varchar(50));


import threading 
class MyThread(threading.Thread):
    def __init__(self,arg):
        super(MyThread,self).__init__()
        self.arg = arg
    
    def run(self):
        get_message(urls[self.arg])
        
import json

if __name__ == '__main__':
    urls=get_url()
#    pool = ThreadPool(6)
#    pool.map(get_message,urls) 
#    pool.close()
#    pool.join()
    for i in range(len(urls)):
        if flag:
            start=time.time()
            get_message(urls[i])
#            t=MyThread(i)
#            t.start()
#            t.join()
            total_time = time.time()-start
            if total_time < 26:
                get_message(urls[i])
            logging.info("page: %i , time:%d , data_amount:%i" % (i, (total_time),len(video_info_list)))
            print ("page: %i , time:%d , data_amount:%i" % (i, (total_time),len(video_info_list)))
        else:
            break
    jsobj = json.dumps(video_info_list)
    fileobj = open('video.json','w')
    fileobj.write(jsobj)
    fileobj.close()
    jsobj = json.dumps(up_info_list)
    fileobj = open('up.json','w')
    fileobj.write(jsobj)
    fileobj.close()
    conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',password='qw13906294204',db='amount_jianlaji_digital',charset='utf8')
    cur = conn.cursor()
    into_db_video(video_info_list,cur,conn)
    into_db_up(up_info_list,cur,conn)
    conn.close()
