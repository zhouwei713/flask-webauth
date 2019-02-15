# coding = utf-8
"""
@author: zhou
@time:2019/1/15 11:17
"""


from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
import time
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return WebUser.query.get(int(user_id))


class WebUser(UserMixin, db.Model):
    __tablename__ = 'webuser'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    @staticmethod
    def init_user():
        users = WebUser.query.filter_by(username='admin').first()
        if users is None:
            users = WebUser(user_id=time.time(), email='admin@123.com', username='admin', confirmed=True)
        users.password = '123456'
        db.session.add(users)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash is not None:
            return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, newpwd):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = newpwd
        db.session.add(self)
        db.session.commit()
        return True

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True


class ThirdOAuth(db.Model):
    __tablename__ = 'thirdoauth'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), unique=True, index=True)
    oauth_name = db.Column(db.String(128))
    oauth_id = db.Column(db.String(128), unique=True, index=True)
    oauth_access_token = db.Column(db.String(128), unique=True, index=True)
    oauth_expires = db.Column(db.String(64), unique=True, index=True)
