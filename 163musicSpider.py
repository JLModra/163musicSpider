# -*- coding:utf-8 -*-
'''
Created on 2016年4月17日

@author: Modra
'''
import pymongo
import requests
import time
import json
from bs4 import BeautifulSoup
import mail
import sys
reload(sys)

#sys.setdefaultencoding('utf-8')

#初始化数据库
client = pymongo.MongoClient('localhost',27017)
#建立歌单数据库netease_music_list
netease_music_list = client['netease_music_list']
#歌单的链接music_list_url
music_list_url = netease_music_list['music_list_link']
#歌单的信息music_list_info
music_list_info = netease_music_list['music_list_info']

#网易云音乐歌单首页
main_url = 'http://music.163.com/?_t=t#/discover/playlist'

#请求歌单的数据包
data = {'order' : 'hot', 'cat' : '全部', 'limit' : '35', 'offset' : '0'}

#请求的头部
header = {'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'\
, 'Accept-Encoding' : 'gzip, deflate, sdch', 'Accept-Language' : 'zh-CN,zh;q=0.8'\
, 'Cache-Control' : 'max-age=0' , 'Connection' : 'keep-alive' , 'Cookie' : \
'JSESSIONID-WYYY=ce75d4c3a12891615d62ceb2596d3d5ba7fbf9f3e3db8efef5cabf9a641d8326c4ba05acc5156be25dbf073673d911fbf5023ff3c828edd77a6870afbbbfb589a428f45285da4a9a35ca20024a264ac59adfd8f34dd9ca2d6b3de520e7f320d3d4f5a7b087d478d152e4ce011e1b69913a2f185f81f62d26795a3771d591eb87f7cce74f%3A1461031288911; _iuqxldmzr_=25; __utma=94650624.188668016.1461029492.1461029492.1461029492.1; __utmb=94650624.2.10.1461029492; __utmc=94650624; __utmz=94650624.1461029492.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'\
, 'Host' : 'music.163.com' , 'Referer' : 'http://music.163.com/' , 'Upgrade-Insecure-Requests' : '1'\
, 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'}

#获得歌单的url，参数page是想获取的页数
def get_music_list_url(page):
    #歌单url的数据库清空
    music_list_url.remove()
    #每页的元url
    page_url = 'http://music.163.com/discover/playlist/?order=hot&cat=%E5%85%A8%E9%83%A8&limit=35&offset=0'
    #用来装每页url的list
    page_url_list = []
    #观察链接发现每页的url之间有一个35的差值
    page_num = [i for i in range(0,page*35 ,35)]
    #for循环构造每页的url
    for page in page_num:
        #把每页的url加入到list中
        page_url_list.append(page_url+str(page))
    #打印测试每页的url是否能正确得到
    #print page_url_list
    #遍历每页，找到每个歌单的url
    for url in page_url_list:
        #得到歌单的html页面
        web_page = requests.get(url, headers=header, data=json.dumps(data))
        #用soup解析歌单的html页面
        soup = BeautifulSoup(web_page.text, "html5lib")
        #找到歌单的链接
        for i in soup.find_all(class_='msk'):
            #组装歌单的url
            url = 'http://music.163.com' + str(i.get('href'))
            #把歌单的url装入数据库
            music_list_url.insert_one({'url' : url}) 
    #输出url测试
    #for i in music_list_url.find():
        #print i['url']

#获取歌单的被收藏数
def get_music_list_collect_num(url):
    data = {'id' : str(url[33:])}
    music_list_page = requests.get(url, headers=header, data=json.dumps(data))
    soup = BeautifulSoup(music_list_page.text, "html5lib")
    music_list_collect_num = soup.find_all(class_='u-btni u-btni-fav ')[0].text
    if len(music_list_collect_num) == 4:
        return '0'
    else:
        return music_list_collect_num[2:-2]

#获得歌单的被分享数
def get_music_list_share_num(url):
    data = {'id' : str(url[33:])}
    music_list_page = requests.get(url, headers=header, data=json.dumps(data))
    soup = BeautifulSoup(music_list_page.text, "html5lib")
    music_list_share_num = soup.find_all(class_='u-btni u-btni-share ')
    if len(music_list_share_num) == 0:
        return '0'
    else:
        return music_list_share_num[0].text[1:-1]
    
#获取歌单评论数 
def get_music_list_comment_count(url):
    data = {'id' : str(url[33:])}
    music_list_page = requests.get(url, headers=header, data=json.dumps(data))
    soup = BeautifulSoup(music_list_page.text, "html5lib")
    music_list_comment_count = soup.find_all(id='cnt_comment_count')
    if len(music_list_comment_count) == 0:
        return '此歌单没有评论'
    else:
        return music_list_comment_count[0].string
    
#获取歌单的标签      
def get_music_list_tags(url):
    data = {'id' : str(url[33:])}
    music_list_page = requests.get(url, headers=header, data=json.dumps(data))
    soup = BeautifulSoup(music_list_page.text, "html5lib")
    music_list_tags = soup.find_all(class_='tags f-cb')
    if len(music_list_tags) == 0:
        return '此歌单没有标签'
    else:
        return music_list_tags[0].text[5:]
 
  
#获取歌单的介绍  
def get_music_list_introduce(url):
    data = {'id' : str(url[33:])}
    music_list_page = requests.get(url, headers=header, data=json.dumps(data))
    soup = BeautifulSoup(music_list_page.text, "html5lib")
    music_list_introduce = soup.find_all(id='album-desc-more')
    if len(music_list_introduce) == 0:
        return '此歌单没有介绍'
    else:
        return music_list_introduce[0].text[4:]
    
#获取歌单的信息
def get_music_list_info():
    music_list_info.remove()
    for i in music_list_url.find():
        url = i['url']
        data = {'id' : str(url[33:])}
        music_list_page = requests.get(url, headers=header, data=json.dumps(data))
        soup = BeautifulSoup(music_list_page.text, "html5lib")
        title = soup.h2.string
        music_list_owner_name = soup.find_all(class_='s-fc7')[0].string
        music_list_owner_href = 'http://music.163.com' + str(soup.a['href'])
        music_list_creat_time = soup.find_all(class_='time s-fc4')[0].string[:10]
        music_list_collect_num = get_music_list_collect_num(url)
        music_list_share_num = get_music_list_share_num(url)
        music_list_comment_count = get_music_list_comment_count(url)
        music_list_play_count = soup.find_all(id='play-count')[0].string
        music_list_count = soup.find_all(id='playlist-track-count')[0].string
        music_list_tags = get_music_list_tags(url)
        music_list_introduce = get_music_list_introduce(url)
        data = {'title' : title,
                'owner_name' : music_list_owner_name,
                'owner_href' : music_list_owner_href,
                'creat_time' : music_list_creat_time,
                'collect_num' : music_list_collect_num,
                'share_num' : music_list_share_num,
                'comment_count' : music_list_comment_count,
                'play_count' : music_list_play_count,
                'count' : music_list_count,
                'tags' : music_list_tags,
                'introduce' : music_list_introduce
            }
#         data = {'歌单名' : title,
#                 '创建者' : music_list_owner_name,
#                 '创建者链接' : music_list_owner_href,
#                 '创建时间' : music_list_creat_time,
#                 '收藏数' : music_list_collect_num,
#                 '分享数'  : music_list_share_num,
#                 '评论数' : music_list_comment_count,
#                 '播放数' : music_list_play_count,
#                 '歌曲数' : music_list_count,
#                 '标签' : music_list_tags,
#                 '介绍' : music_list_introduce
#             }
        #把数据导入数据库
        music_list_info.insert_one(data)
        #print title
#         print music_list_owner_name
#         print music_list_owner_href
#         print music_list_creat_time
#         print music_list_collect_num
#         print music_list_share_num
#         print music_list_comment_count
#         print music_list_play_count
#         print music_list_count
#         print music_list_tags
#         print music_list_introduce
        
start = time.time()
get_music_list_url(1)
get_music_list_info()
print music_list_url.count()
print '运行时间是：', time.time()-start
mail.send_email(music_list_url.count(), time.time()-start)
    
    
