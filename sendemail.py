# coding = utf-8
"""
@author: zhou
@time:2019/2/14 15:12
"""

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
from threading import Thread


def sendmail(to, subject, text):
    # 第三方 SMTP 服务
    mail_host = "smtp.gmail.com"  # 设置服务器
    mail_user = os.environ.get('MAIL_USERNAME')  # 用户名， 从环境变量中获取
    mail_pass = os.environ.get('MAIL_PASSWORD')  # 口令

    sender = os.environ.get('MAIL_USERNAME')
    receivers = [to]

    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = Header('萝卜大杂烩', 'utf-8')
    message['to'] = Header(to, 'utf-8')

    subject = subject
    message['Subject'] = Header(subject, 'utf-8')

    smtpobj = smtplib.SMTP(mail_host, 25)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.login(mail_user, mail_pass)
    thr = Thread(target=smtpobj.sendmail, args=[sender, receivers, message.as_string()])
    # smtpobj.sendmail(sender, receivers, message.as_string())
    thr.start()
    return thr


if __name__ == "__main__":
    sendmail('luobodazahui@123.com', '非常好', '看看怎么样')



