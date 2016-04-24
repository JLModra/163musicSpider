#   -*- coding:utf-8  -*-
'''
Created on 2016年4月24日

@author: Modra
'''
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.MIMEMultipart import MIMEMultipart
import email.MIMEBase 
import os.path  
import smtplib
from musicSpider import debug_info


#用于格式化邮件地址
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


def send_email(num, time, file):
    #发送地址
    from_addr = 'q12010117@njupt.edu.cn'

    #发送邮箱密码
    password = '321027199405076617'

    #接收地址
    to_addr = '754675419@qq.com'

    #输入SMTP服务器地址
    smtp_server = 'em.njupt.edu.cn'
    
    #需要发送的附件
    file_name = file
    
    #构造MIMEMultipart对象做为根容器 
    main_msg = MIMEMultipart()

    #构建一个最简单的邮件内容
    contant = 'hello, 您的爬虫代码运行结束,一共爬得数据：'+str(num)+'条。'+'花费时间：'+str(time)+'s'
    msg = MIMEText(contant, 'plain', 'utf-8')
#     msg['From'] = _format_addr(u'Python <%s>' % from_addr)
#     msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
#     msg['Subject'] = Header(u'Q12010117', 'utf-8').encode()
    
    #构造MIMEText对象做为邮件显示内容并附加到根容器 
    main_msg.attach(msg)
    
    #构造MIMEBase对象做为文件附件内容并附加到根容器  
    contype = 'application/octet-stream'  
    maintype, subtype = contype.split('/', 1)  
    
    #读入文件内容并格式化  
    data = open(file_name, 'rb')  
    file_msg = email.MIMEBase.MIMEBase(maintype, subtype)  
    file_msg.set_payload(data.read( ))  
    data.close( )  
    email.Encoders.encode_base64(file_msg) 
    
    #设置附件头  
    basename = os.path.basename(file_name)  
    file_msg.add_header('Content-Disposition',  
                        'attachment', filename = basename)  
    main_msg.attach(file_msg) 
    
    #设置根容器属性  
    main_msg['From'] = _format_addr(u'Python <%s>' % from_addr) 
    main_msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
    main_msg['Subject'] = Header(u'Q12010117', 'utf-8').encode()  
    main_msg['Date'] = email.Utils.formatdate()
    
    #得到格式化后的完整文本  
    fullText = main_msg.as_string( )   

    #连接SMTP服务器的25端口，SMTP默认端口就是25，QQ的SMTP端口是465或者587
    server = smtplib.SMTP()

    #连接邮箱服务器
    server.connect(smtp_server, 25)

    #打印出和SMTP服务器交互的所有消息
    server.set_debuglevel(1)

    #登陆SMTP服务器
    server.login(from_addr, password)

    #发送邮件
    #server.sendmail(from_addr, [to_addr], msg.as_string())
    server.sendmail(from_addr, [to_addr], fullText)

    #退出
    server.quit()
    
    #提示
    print '已发送邮件！'
    
send_email(debug_info.find_one()['num'], debug_info.find_one()['time'], '/163musicSpider/music_list_info.csv')