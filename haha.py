# -*- coding:utf-8 -*-
'''
Created on 2016��5��30��

@author: asus
'''

import json
import re
from bs4 import BeautifulSoup
import requests


header = {'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'\
, 'Accept-Encoding' : 'gzip, deflate, sdch', 'Accept-Language' : 'zh-CN,zh;q=0.8'\
, 'Cache-Control' : 'max-age=0' , 'Connection' : 'keep-alive' , 'Cookie' : \
'JSESSIONID-WYYY=ce75d4c3a12891615d62ceb2596d3d5ba7fbf9f3e3db8efef5cabf9a641d8326c4ba05acc5156be25dbf073673d911fbf5023ff3c828edd77a6870afbbbfb589a428f45285da4a9a35ca20024a264ac59adfd8f34dd9ca2d6b3de520e7f320d3d4f5a7b087d478d152e4ce011e1b69913a2f185f81f62d26795a3771d591eb87f7cce74f%3A1461031288911; _iuqxldmzr_=25; __utma=94650624.188668016.1461029492.1461029492.1461029492.1; __utmb=94650624.2.10.1461029492; __utmc=94650624; __utmz=94650624.1461029492.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'\
, 'Host' : 'music.163.com' , 'Referer' : 'http://music.163.com/' , 'Upgrade-Insecure-Requests' : '1'\
, 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'}


style_map = {'华语' : 6, '欧美' : 5, '日语' : 4, '韩语' : 3, '粤语' : 2, '小语种' : 1, '流行' : 24, '摇滚' : 23, 
             '民谣' : 22, '电子' : 21, '舞曲' : 20, '说唱' : 19, '轻音乐' : 18, '爵士' : 17, '乡村' : 16, 'R&B/Soul' : 15, 
             '古典' : 14, '民族' : 13, '英伦' : 12, '金属' : 11, '朋克' : 10, '蓝调' : 9, '雷鬼' : 8, '世界音乐' : 7, 
             '拉丁' : 6, '另类/独立' : 5, 'New Age' : 4, '古风' : 3, '后摇' : 2, 'Bossa Nova' : 1, '清晨' : 13, 
             '夜晚' : 12, '学习' : 11, '工作' : 10, '午休' : 9, '华语' : 8, '下午茶' : 7, '地铁' : 6, '驾车' : 5, 
             '运动' : 4, '旅行' : 3, '散步' : 2, '酒吧' : 1, '怀旧' : 13, '清新' : 12, '浪漫' : 11, '性感' : 10, 
             '伤感' : 9, '治愈' : 8, '放松' : 7, '孤独' : 6, '感动' : 5, '兴奋' : 4, '快乐' : 3, '安静' : 2, 
             '思念' : 1, '影视原声' : 17, 'ACG' : 16, '校园' : 15, '游戏' : 14, '70后' : 13, '80后' : 12, '90后' : 11, 
             '网络歌曲' : 10, 'KTV' : 9, '经典' : 8, '翻唱' : 7, '吉他' : 6, '钢琴' : 5, '器乐' : 4, '儿童' : 3, 
             '榜单' : 2, '00后' : 1}

url = 'http://music.163.com/playlist?id=394889583'

data = {'id' : str(url[33:])}

web_page = requests.get(url, headers = header, data=json.dumps(data))

soup = BeautifulSoup(web_page.text)

# tab = soup.find_all(class_='tags f-cb')[0].text[5:]
#music_list_num = re.findall(r'(\d+)',soup.find_all(class_='f-ff2')[-2].string)[0]
music_list_num = soup.find_all(id='play-count')[0].string
print music_list_num
#print style_map
# a = []
#  
# for i in tab.split('\n'):
#     if i in style_map.keys():
#         print i , style_map[i]





