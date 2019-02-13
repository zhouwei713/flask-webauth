# coding = utf-8
"""
@author: zhou
@time:2019/2/12 13:45
"""

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
