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

    @staticmethod
    def init_user():
        users = WebUser.query.filter_by(username='admin').first()
        if users is None:
            users = WebUser(email='admin@123.com', username='admin', user_id=time.time())
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
        return check_password_hash(self.password_hash, password)


class ThirdOAuth(db.Model):
    __tablename__ = 'thirdoauth'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), unique=True, index=True)
    oauth_name = db.Column(db.String(128))
    oauth_id = db.Column(db.String(128), unique=True, index=True)
    oauth_access_token = db.Column(db.String(128), unique=True, index=True)
    oauth_expires = db.Column(db.String(64), unique=True, index=True)








