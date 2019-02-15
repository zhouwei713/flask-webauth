# coding = utf-8
"""
@author: zhou
@time:2019/1/15 12:36
"""

from .. import db
from . import main
from ..models import WebUser, ThirdOAuth
from flask import Flask, request, render_template, jsonify, g, session
import os
from flask_login import login_required
from .. import github
from flask_login.utils import current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    # print(session)
    if current_user.is_authenticated:
        if 'userid' in session:
            user = ThirdOAuth.query.filter_by(user_id=session['userid']).first()
            if user:
                response = github.get('user', access_token=user.oauth_access_token)
                avatar = response['avatar_url']
                username = response['login']
                return render_template('index.html', username=username, avatar=avatar)
    return render_template('index.html')


@main.route('/need')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@main.route('/needconfirm')
@login_required
def needconfirm():
    print(request.endpoint)
    return 'Only confirmed users are allowed!'


@main.route('/manageuser')
@login_required
def manageuser():
    return render_template('manageuser.html')



