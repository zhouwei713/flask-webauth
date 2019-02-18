# coding = utf-8
"""
@author: zhou
@time:2019/2/16 14:50
"""


from twilio.rest import Client
import os
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import Config


def sendsms(code, num):
    account_sid = os.environ.get('A_SID')
    auth_token = os.environ.get('A_TK')
    mytwilio_num = os.environ.get('T_NUM')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_=mytwilio_num,
        body=code,
        to=num)


def generate_code(expiration=3600):
    random_num = ''.join(str(i) for i in random.sample(range(0, 9), 4))
    s = Serializer(Config.SECRET_KEY, expiration)
    return s.dumps({'code': random_num})


def decoding_code(code):
    s = Serializer(Config.SECRET_KEY)
    c = s.loads(code)
    return c['code']


if __name__ == "__main__":
    r = generate_code()
    decoding_code(r)
    sendsms(r, '+8613000002222')
