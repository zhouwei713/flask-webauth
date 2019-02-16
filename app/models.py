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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=1)
    block_status = db.Column(db.Boolean, default=True)

    @staticmethod
    def init_user():
        users = WebUser.query.filter_by(username='admin').first()
        admin_role = Role.query.filter_by(name='Admin').first()
        if users is None:
            users = WebUser(user_id=time.time(), email='admin@123.com',
                            username='admin', confirmed=True, role=admin_role)
        users.password = '123456'
        db.session.add(users)
        db.session.commit()

    @staticmethod
    def insert_user():
        users = {
            'user1': ['user1@luobo.com', 'test1', 1],
            'user2': ['user2@luobo.com', 'test2', 1],
            'admin1': ['admin1@luobo.com', 'admin1', 2],
            'admin2': ['admin2@luobo.com', 'admin2', 2]
        }
        for u in users:
            user = WebUser.query.filter_by(username=u[0]).first()
            if user is None:
                user = WebUser(user_id=time.time(), username=u, email=users[u][0],
                               confirmed=True, role_id=users[u][2])
                user.password = users[u][1]
                db.session.add(user)
            db.session.commit()

    def is_admin(self):
        if self.role_id is 2:
            return True
        else:
            return False

    def is_block(self):
        if self.block_status:
            return True
        else:
            return False

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


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('WebUser', backref='role')

    @staticmethod
    def init_roles():
        roles = ['User', 'Admin']
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                db.session.add(role)
        db.session.commit()
