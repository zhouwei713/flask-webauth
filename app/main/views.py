# coding = utf-8
"""
@author: zhou
@time:2019/1/15 12:36
"""

from .. import db
from . import main
from ..models import WebUser, ThirdOAuth
from flask import Flask, request, render_template, jsonify, g, session, redirect, url_for, flash, abort
import os
from flask_login import login_required
from .. import github
from flask_login.utils import current_user
from .forms import EditProfileForm


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        if 'userid' in session:
            user = ThirdOAuth.query.filter_by(user_id=session['userid']).first()
            if user:
                response = github.get('user', access_token=user.oauth_access_token)
                avatar = response['avatar_url']
                username = response['login']
                return render_template('index.html', username=username, avatar=avatar)
    return render_template('index.html')


@main.route('/userlist', methods=['GET', 'POST'])
@login_required
def userlist():
    if current_user.is_admin():
        user_list = WebUser.query.all()
        return render_template('userlist.html', userlist=user_list)
    flash('You have not permission to access this page')
    return redirect(url_for('main.index'))


@main.route('/blockuser/<username>', methods=['GET', 'POST'])
@login_required
def blockuser(username):
    if current_user.is_admin():
        user = WebUser.query.filter_by(username=username).first()
        if user.username == current_user.username:
            flash('Your can not block yourself')
            return redirect(url_for('main.userlist'))
        if user.is_block():
            user.block_status = False
            db.session.add(user)
            db.session.commit()
            flash('Have block this user')
            return redirect(url_for('main.userlist'))
        else:
            flash('This user have been blocked')
            return redirect(url_for('main.userlist'))
    flash('Your have no permission to operate it')
    return redirect(url_for('main.index'))


@main.route('/unblockuser/<username>', methods=['GET', 'POST'])
@login_required
def unblockuser(username):
    if current_user.is_admin():
        user = WebUser.query.filter_by(username=username).first()
        if user.is_block():
            flash('this user is not block')
            return redirect(url_for('main.userlist'))
        else:
            user.block_status = True
            db.session.add(user)
            db.session.commit()
            flash('Have unblock this user')
            return redirect(url_for('main.userlist'))
    flash('Your have no permission to operate it')
    return redirect(url_for('main.index'))


@main.route('/need')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@main.route('/needconfirm')
@login_required
def needconfirm():
    return 'Only confirmed users are allowed!'


@main.route('/onlyadmin')
@login_required
def onlyadmin():
    if current_user.is_admin():
        return 'Your are admin so you can see this page'
    else:
        return 'You are not admin user, Only admin user can access this page'


@main.route('/manageuser')
@login_required
def manageuser():
    return render_template('manageuser.html')


@main.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = WebUser.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    if 'userid' in session:
        thirduser = ThirdOAuth.query.filter_by(user_id=session['userid']).first()
        if thirduser:
            response = github.get('thirduser', access_token=thirduser.oauth_access_token)
            avatar = response['avatar_url']
            gituser = response['login']
            return render_template('user.html', user=user, avatar=avatar, gituser=gituser)
    return render_template('user.html', user=user, avatar=None, gituser=None)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        username = form.username.data
        if WebUser.query.filter_by(username=username).first() and username != current_user.username:
            flash('This username has been used')
            return redirect(url_for('main.edit_profile'))
        current_user.username = form.username.data
        current_user.nickname = form.nickname.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.nickname.data = current_user.nickname
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

