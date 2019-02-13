# coding = utf-8
"""
@author: zhou
@time:2019/1/15 11:42
"""

import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "hardtoguess"
    GITHUB_CLIENT_ID = 'cf1de35ef11d20bcdab2'
    GITHUB_CLIENT_SECRET = 'ba7c8c83be9cd574eb3da1b5e704d11d35acccb8'
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'myweb.sqlite3')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
