# coding = utf-8
"""
@author: zhou
@time:2019/1/15 12:35
"""

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors


