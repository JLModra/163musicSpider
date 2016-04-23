#   -*- coding:utf-8  -*-
'''
Created on 2016年4月24日

@author: Modra
'''
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

#用于格式化邮件地址
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


def send_email(num, time):
    #发送地址
    from_addr = 'q12010117@njupt.edu.cn'

    #发送邮箱密码
    password = '321027199405076617'

    #接收地址
    to_addr = '754675419@qq.com'

    #输入SMTP服务器地址
    smtp_server = 'em.njupt.edu.cn'

    #构建一个最简单的邮件内容
    msg = MIMEText('hello, 您的爬虫代码运行结束,一共爬得数据：'+str(num)+'条。'+'花费时间：'+str(time)+'s', 'plain', 'utf-8')
    msg['From'] = _format_addr(u'Python <%s>' % from_addr)
    msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
    msg['Subject'] = Header(u'Q12010117', 'utf-8').encode()

    #连接SMTP服务器的25端口，SMTP默认端口就是25，QQ的SMTP端口是465或者587
    server = smtplib.SMTP()

    #连接邮箱服务器
    server.connect(smtp_server, 25)

    #打印出和SMTP服务器交互的所有消息
    #server.set_debuglevel(1)

    #登陆SMTP服务器
    server.login(from_addr, password)

    #发送邮件
    server.sendmail(from_addr, [to_addr], msg.as_string())

    #退出
    server.quit()
    
    #提示
    print '已发送邮件！'
  
