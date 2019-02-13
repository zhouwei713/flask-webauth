# coding = utf-8
"""
@author: zhou
@time:2019/2/12 13:46
"""

from flask import render_template, redirect, request, url_for, flash, g, session
from . import auth
from .forms import LoginForm
from ..models import WebUser, ThirdOAuth
from flask_login import login_user, login_required, logout_user
from .. import github
import time
from app import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = WebUser.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password!')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    if 'userid' in session:
        session.pop('userid')
    flash('You have logged out!')
    return redirect(url_for('main.index'))


@auth.route('/githublogin', methods=['GET', 'POST'])
def githublogin():
    return github.authorize(scope='repo')


@auth.route('/callback/github')
@github.authorized_handler
def authorized(access_token):
    if access_token is None:
        flash('Login Failed!')
        return redirect(url_for('main.index'))
    response = github.get('user', access_token=access_token)
    username = response['login']
    u_id = response['id']
    email = response['email']
    avatar = response['avatar_url']
    user = WebUser.query.filter_by(username=username).first()
    if user is None:
        user = WebUser(username=username, user_id=time.time())
        db.session.add(user)
        db.session.commit()
        thirduser = ThirdOAuth(user_id=WebUser.query.filter_by(username=username).first().user_id,
                               oauth_name='github', oauth_access_token=access_token,
                               oauth_id=u_id)
        db.session.add(thirduser)
        db.session.commit()
        login_user(user)
        user.email = email
        db.session.add(user)
        db.session.commit()
        session['userid'] = user.user_id
        return render_template('index.html', avatar=avatar)
    else:
        thirduser = ThirdOAuth.query.filter_by(user_id=user.user_id).first()
        thirduser.oauth_access_token = access_token
        db.session.add(thirduser)
        db.session.commit()
        user.email = email
        db.session.add(user)
        db.session.commit()
        login_user(user)
        session['userid'] = user.user_id
        return render_template('index.html', avatar=avatar)
