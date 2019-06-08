#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  9 09:19:08 2019

@author: veetsin
"""

import requests
# 用于从列表中随机选择
import random 
import time
# 导入“上篇”实现好的类
def LoadUserAgents(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[:-1])
    random.shuffle(uas)
    return uas



class Downloader:

    def __init__(self):
        with open("proxies.txt") as f:
            self.proxies = f.readlines()
        
        self.proxy = random.choice(self.proxies).strip()
        
#        with open("ua.txt") as f:
#            self.user_agent_list = f.readlines()
        self.uas = LoadUserAgents("ua.txt")
#        
#        self.user_agent_list = [
#        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
#        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
#        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
#        "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
#        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
#        "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
#        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
#        "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
#        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
#        "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
#        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
#        "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
#        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
#        "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
#        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
#        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
#        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
#        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
#        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
#        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
#        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
#        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
#        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
#        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
#        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
#        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
#        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
#        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
#        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
#        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
#        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
#        "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
#        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
#        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
#        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
#        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
#    ]

    def get(self, url, timeout=5):
        '''
        :param str url: 要访问的链接
        :param int timeout: 连接超时时间，默认为 5 秒
        '''
#        time.sleep(random.uniform(0.5,5))# without multiprocess
        headers = {
            # 从已有的 User-Agent 列表随机选一个添加到请求头
            # 请求头中还可以添加其他参数，
            # 比如 Referer，用于破解多媒体文件（图片、视频）的防盗链
            'User-Agent':random.choice(self.uas).strip()
        }
        # 明确代理的协议类型
        protocol = 'https' if 'https' in self.proxy else 'http'
        self.proxy = random.choice(self.proxies).strip()
        proxies = {
            protocol: self.proxy
        }
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
#            response = requests.get(url, headers=headers, timeout=timeout)

        except:
            # 若请求出错，则更换代理 ip，并在一秒后重新发送请求，
            # 也就是只要不出错，会一直使用同一个 ip 进行访问，这样可以提高每个有效 ip 的利用率。
            print('[requests]正在更换代理ip...')
#            self.proxies.pop(self.proxies.index(self.proxy+'\n'))
            self.proxy = random.choice(self.proxies).strip()

            time.sleep(random.uniform(0.5,2))# without multiprocess

            return self.get(url)
        else:
            # 请求成功则返回响应文本
            return response