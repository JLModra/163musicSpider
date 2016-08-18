# -*- coding:utf-8 -*-
'''
Created on 2016年4月17日
爬虫部分
@author: Modra
'''
import pymongo
import requests
import time
import json
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool
import re
# import mail
import sys

#初始化
client = pymongo.MongoClient('localhost',27017)
#新建数据库
netease_music_list = client['netease_music_list']
#新建一个表用来存储歌单的url
music_list_url = netease_music_list['music_list_link']
#新建一个表用来存储歌单的信息
music_list_info = netease_music_list['music_list_info']
#新建一个表来测试
music_list_info_debug = netease_music_list['music_list_info_debug']
#用来训练的数据
music_list_info_train = netease_music_list['music_list_info_train']
#用来测试的数据
music_list_info_test = netease_music_list['music_list_info_test']
#新建一个表用来存储程序运行的信息
debug_info = netease_music_list['debug_info']

#歌单首页的url
main_url = 'http://music.163.com/?_t=t#/discover/playlist'

#请求歌单的数据包
data = {'order' : 'hot', 'cat' : '全部', 'limit' : '35', 'offset' : '0'}

#请求头
header = {'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'\
, 'Accept-Encoding' : 'gzip, deflate, sdch', 'Accept-Language' : 'zh-CN,zh;q=0.8'\
, 'Cache-Control' : 'max-age=0' , 'Connection' : 'keep-alive' , 'Cookie' : \
'JSESSIONID-WYYY=ce75d4c3a12891615d62ceb2596d3d5ba7fbf9f3e3db8efef5cabf9a641d8326c4ba05acc5156be25dbf073673d911fbf5023ff3c828edd77a6870afbbbfb589a428f45285da4a9a35ca20024a264ac59adfd8f34dd9ca2d6b3de520e7f320d3d4f5a7b087d478d152e4ce011e1b69913a2f185f81f62d26795a3771d591eb87f7cce74f%3A1461031288911; _iuqxldmzr_=25; __utma=94650624.188668016.1461029492.1461029492.1461029492.1; __utmb=94650624.2.10.1461029492; __utmc=94650624; __utmz=94650624.1461029492.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'\
, 'Host' : 'music.163.com' , 'Referer' : 'http://music.163.com/' , 'Upgrade-Insecure-Requests' : '1'\
, 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'}

#每种音乐风格的分数
style_map = {u'华语' : 6, u'欧美' : 5, u'日语' : 4, u'韩语' : 3, u'粤语' : 2, u'小语种' : 1, u'流行' : 24, u'摇滚' : 23, 
             u'民谣' : 22, u'电子' : 21, u'舞曲' : 20, u'说唱' : 19, u'轻音乐' : 18, u'爵士' : 17, u'乡村' : 16, u'R&B/Soul' : 15, 
             u'古典' : 14, u'民族' : 13, u'英伦' : 12, u'金属' : 11, u'朋克' : 10, u'蓝调' : 9, u'雷鬼' : 8, u'世界音乐' : 7, 
             u'拉丁' : 6, u'另类/独立' : 5, u'New Age' : 4, u'古风' : 3, u'后摇' : 2, u'Bossa Nova' : 1, u'清晨' : 12, 
             u'夜晚' : 11, u'学习' : 10, u'工作' : 9, u'午休' : 8, u'下午茶' : 7, u'地铁' : 6, u'驾车' : 5, 
             u'运动' : 4, u'旅行' : 3, u'散步' : 2, u'酒吧' : 1, u'怀旧' : 13, u'清新' : 12, u'浪漫' : 11, u'性感' : 10, 
             u'伤感' : 9, u'治愈' : 8, u'放松' : 7, u'孤独' : 6, u'感动' : 5, u'兴奋' : 4, u'快乐' : 3, u'安静' : 2, 
             u'思念' : 1, u'影视原声' : 17, u'ACG' : 16, u'校园' : 15, u'游戏' : 14, u'70后' : 13, u'80后' : 12, u'90后' : 11, 
             u'网络歌曲' : 10, u'KTV' : 9, u'经典' : 8, u'翻唱' : 7, u'吉他' : 6, u'钢琴' : 5, u'器乐' : 4, u'儿童' : 3, 
             u'榜单' : 2, u'00后' : 1}

#获得歌单的url，参数page是想获取的页数
def get_music_list_url(page):
    #歌单url的数据库清空
    music_list_url.remove()
    #每页的元url
    page_url = 'http://music.163.com/discover/playlist/?order=hot&cat=%E5%85%A8%E9%83%A8&limit=35&offset=0'
    #用来装每页url的list
    page_url_list = []
    #观察链接发现每页的url之间有一个35的差值
    page_num = [i for i in range(0,int(page[1])*35 ,35)]
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
        print '此歌单没有标签'
        return 0
    else:
        value = 0
        tab = music_list_tags[0].text[5:]
        for i in tab.split('\n'):
            if i in style_map.keys():
                value = value + style_map[i]
        return value
 
  
#获取歌单的介绍  
def get_music_list_introduce(url):
    data = {'id' : str(url[33:])}
    music_list_page = requests.get(url, headers=header, data=json.dumps(data))
    soup = BeautifulSoup(music_list_page.text, "html5lib")
    music_list_introduce = soup.find_all(id='album-desc-more')
    if len(music_list_introduce) == 0:
        #return '此歌单没有介绍'
        return 0
    else:
        return len(music_list_introduce[0].text[4:])

#得到歌单创建者的信息
def get_owner_info(url):
    data = {'id' : str(url[34:])}
    web_page = requests.get(url, headers=header, data=json.dumps(data))
    soup = BeautifulSoup(web_page.text)
    try:
        #获取粉丝数
        fan_num = soup.find_all(id='fan_count')[0].string
    except:
        fan_num = 0
        print '获取粉丝数目时出现异常' , soup.title.string
    try:
        #获取听歌数
        listen_music_num = soup.h4.string[4:-1]
    except:
        listen_music_num = 0
        print '获取听歌数时出现异常' , soup.title.string
    try:
        #获取创建的歌单数
        music_list_num = re.findall(r'(\d+)',soup.find_all(class_='f-ff2')[-2].string)[0]
    except:
        music_list_num = 0
        print '获取创建歌单数目时出现异常' , soup.title.string
    try:
        #获取收藏的歌单数
        collect_music_list_num = re.findall(r'(\d+)',soup.find_all(class_='f-ff2')[-1].string)[0]
    except:
        collect_music_list_num = 0
        print '获取收藏歌单数目时出现异常' , soup.title.string
    return fan_num, listen_music_num, music_list_num, collect_music_list_num

def get_tab_score(list_url, music_list_owner_href): 
    try:
        #请求歌单数据的data
        data_1 = {'id' : str(url[33:])}
        #请求创建者数据的data
        data_2 = {'id' : str(url[34:])}  
        web_page_1 = requests.get(list_url, headers = header, data=json.dumps(data_1))
        web_page_2 = requests.get(music_list_owner_href, headers = header, data=json.dumps(data_2))
        soup_1 = BeautifulSoup(web_page_1.text)
        soup_2 = BeautifulSoup(web_page_2.text)
        tab_raw = soup_1.find_all(class_='tags f-cb')[0].text[5:]
        good_at_title = soup_2.find_all(class_='djp f-fs1 s-fc3')[0].text
        tab = tab_raw.split('\n')
        del tab[-1]
        result = []
        score = 10
        for i in tab:
            result.append(re.findall(i, good_at_title))
        for i in result:
            if len(i) != 0:
                score = score + 10
        return score
    except:
        return 0
#得到歌单的数据，参数为歌单的url
def get_data(url):
    data = {'id' : str(url[33:])}
    music_list_page = requests.get(url, headers=header, data=json.dumps(data))
    soup = BeautifulSoup(music_list_page.text, "html5lib")
    title = soup.h2.string
    #输出歌单名，便于调试
    print title
    music_list_owner_name = soup.find_all(class_='s-fc7')[0].string
    music_list_owner_href = 'http://music.163.com' + str(soup.a['href'])
    owner_fan_num , owner_listen_music_num, owner_music_list_num, owner_collect_music_list_num = get_owner_info(music_list_owner_href) 
    music_list_creat_time = soup.find_all(class_='time s-fc4')[0].string[:10]
    music_list_collect_num = get_music_list_collect_num(url)
    music_list_share_num = get_music_list_share_num(url)
    music_list_comment_count = get_music_list_comment_count(url)
    music_list_play_count = soup.find_all(id='play-count')[0].string
    music_list_count = soup.find_all(id='playlist-track-count')[0].string
    music_list_tags = get_music_list_tags(url)
    music_list_introduce = get_music_list_introduce(url)
    score = get_tab_score(url, music_list_owner_href)
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
            'introduce' : music_list_introduce,
            'classification' : -1,
            'owner_fan_num' : owner_fan_num,
            'owner_listen_music_num' : owner_listen_music_num,
            'owner_music_list_num' : owner_music_list_num,
            'owner_collect_music_list_num' : owner_collect_music_list_num,
            'score' : score
        }
    return data
       
#单线程获取歌单的信息
def get_music_list_info():
    music_list_info.remove()
    for i in music_list_url.find():
        url = i['url']
        data = get_data(url)
        #把数据导入数据库
        music_list_info.insert_one(data)
 
#多线程获取歌单的信息
def get_music_list_info_pool(url):
    data = get_data(url)
    title = data['title']
    play_count = data['play_count']
    tit = {}
    for i in music_list_info.find():
        tit[i['title']] = i['play_count']
    if title in tit.keys():
        if play_count == tit[title]:
            print title, '在数据库中已经存在且数据不需要更新'
        else:
            music_list_info.remove({'title' : title})
            music_list_info.insert_one(data)
            print title, '在数据库中存在但是数据需要更新'
    else:
        #把数据导入数据库
        music_list_info.insert_one(data)
#     music_list_info_debug.insert_one(data)
    

#生成所有歌单的url
def get_all_url(num):
    music_list_url.remove()
    i = 1
    url_base = 'http://music.163.com/playlist?id='
    while i != num:
        print '正在建立url库，当前是第' + str(i) + '条url'
        url = url_base + str(i)
        music_list_url.insert_one({'url' : url})
        i = i + 1
    print 'url库建立结束，共有' +  str(music_list_url.count()) + '条url纪录'
    
#获取网易云音乐所有歌单
def get_all_music_list(url): 
    music_list_info.remove()   
    if (is_url_valid(url)):
        print url + '有效歌单'
        try:
            data = get_data(url)
            music_list_info.insert_one(data)
        except:
            print url + '爬取歌单信息时except'      
    else:
        print url + '无效歌单'
        
#判断url是否有效    
def is_url_valid(url): 
    data = {'id' : str(url[33:])}
    music_list_page = requests.get(url, headers=header, data=json.dumps(data))
    soup = BeautifulSoup(music_list_page.text, "html5lib")
    if (soup.find_all(class_='note s-fc3')):
        return False
    else:
        return True


# if __name__ == "__main__":   
#     start = time.time()
#     #url = get_all_url(379948286)
#     for i in music_list_url.find():
#         get_all_music_list(i['url'])
# #     pool = Pool()
# #     pool.map(get_all_music_list,url)
# #     pool.close()
# #     pool.join()
#     print music_list_url.count()
#     print '运行时间是：', time.time()-start

if __name__ == "__main__":   
    start = time.time()
#     music_list_info_debug.remove()
    get_music_list_url(sys.argv)
    #get_music_list_info()
    url = []
    for i in music_list_url.find():
        url.append(i['url'])
    pool = Pool()
    pool.map(get_music_list_info_pool,url)
    pool.close()
    pool.join()
    print music_list_url.count()
    print '运行时间是：', time.time()-start
    debug_info.remove()
    #把程序运行的数据装入数据库
    debug_info.insert_one({'num' : music_list_url.count(), 'time' : time.time()-start})
 
    # print debug_info.find_one()['num']
    # print debug_info.find_one()['time']
#     mail.send_email(music_list_url.count(), time.time()-start)    

    
    
