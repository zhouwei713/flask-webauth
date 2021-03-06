# coding = utf-8
"""
@author: zhou
@time:2019/2/12 13:46
"""

from flask import render_template, redirect, request, url_for, flash, session
from . import auth
from .forms import LoginForm, RegisterForm, ChangePwdForm, ResetPwdEmailForm, ResetPwdForm, LoginSMSForm, LoginSMSCodeForm
from ..models import WebUser, ThirdOAuth, Role, UserPhone
from flask_login import login_user, login_required, logout_user, current_user
from .. import github
import time
from app import db
from sendemail import sendmail
from sendsms import sendsms, generate_code, decoding_code


@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint == 'main.needconfirm':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = WebUser.query.filter_by(email=form.email.data).first()
        if user is not None:
            if user.password_hash is None:
                flash('Please use the third party service to login.')
                return redirect(url_for('.login'))
            if user.verify_password(form.password.data):
                if user.is_block() is False:
                    flash('You have been blocked, please contact admin')
                    return redirect(url_for('.login'))
                login_user(user)
                return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password!')
    return render_template('auth/login.html', form=form)


@auth.route('/loginnew', methods=['GET','POST'])
def login_new():
    form = LoginForm()
    if form.validate_on_submit():
        user = WebUser.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('login/login.html', form=form)


@auth.route('/login-check', methods=['GET', 'POST'])
def login_check():
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    user = WebUser.query.filter_by(email=email).first()
    if user is not None and user.verify_password(password):
        login_user(user)
        return "success"
    else:
        return "error"


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
        user = WebUser(username=username, user_id=time.time(), confirmed=True)
        db.session.add(user)
        db.session.commit()
        thirduser = ThirdOAuth(user_id=WebUser.query.filter_by(username=username).first().user_id,
                               oauth_name='github', oauth_access_token=access_token,
                               oauth_id=u_id)
        db.session.add(thirduser)
        db.session.commit()
        if user.is_block() is False:
            flash('You have been blocked, please contact admin')
            return redirect(url_for('.login'))
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
        if user.is_block() is False:
            flash('You have been blocked, please contact admin')
            return redirect(url_for('.login'))
        login_user(user)
        session['userid'] = user.user_id
        return render_template('index.html', avatar=avatar)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = WebUser(email=form.email.data,
                       username=form.username.data, password=form.password.data,
                       user_id=time.time(), confirmed=True)
        db.session.add(user)
        db.session.commit()
        flash('You can login now.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/register-check', methods=['GET', 'POST'])
def register_check():
    email = request.form.get('email1', '')
    password = request.form.get('password1', '')
    name = request.form.get('name1', '')
    user = WebUser.query.filter_by(email=email).first()
    if user is None:
        newuser = WebUser(email=email, username=name, password=password,
                          user_id=time.time(), confirmed=True)
        db.session.add(newuser)
        db.session.commit()
        # token = newuser.generate_confirmation_token()
        # text = render_template('auth/email/confirm.txt', user=newuser, token=token)
        # sendmail(newuser.email, 'Confirm your Account', text)
        return "success"
    else:
        return "error"


@auth.route('/registerconfirm', methods=['GET', 'POST'])
def register_confirm():
    form = RegisterForm()
    if form.validate_on_submit():
        user = WebUser(email=form.email.data,
                       username=form.username.data, password=form.password.data,
                       user_id=time.time())
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        text = render_template('auth/email/confirm.txt', user=user, token=token)
        sendmail(user.email, 'Confirm Your Account', text)
        flash('A Confirmation email has been sent to you by your registered email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/logincodesend/', methods=['GET', 'POST'])
def login_codesend():
    codeform = LoginSMSCodeForm()
    if codeform.validate_on_submit():
        num = codeform.phonenumber.data
        user = UserPhone.query.filter_by(phone=num).first()
        if user is None:
            user = UserPhone(phone=num)
            db.session.add(user)
            db.session.commit()
        code = generate_code()
        decod_code = decoding_code(code)
        sendsms(decod_code, '+86' + str(num))
        flash('Have send a validate code to your phone')
        return redirect(url_for('.login_codeverify', code=code, num=num))
    return render_template('auth/logincodesend.html', form=codeform)


@auth.route('/logincodeverify/<code>/<num>', methods=['GET', 'POST'])
def login_codeverify(code, num):
    form = LoginSMSForm()
    code = decoding_code(code)
    if form.validate_on_submit():
        if str(form.validatacode.data) == code:
            webuser = WebUser.query.filter_by(phone=num).first()
            if webuser is None:
                webuser = WebUser(username=num, phone=num, user_id=time.time(), confirmed=True)
                db.session.add(webuser)
                db.session.commit()
            phoneuser = UserPhone.query.filter_by(phone=num).first()
            if phoneuser:
                phoneuser.user_id = webuser.user_id
                db.session.add(phoneuser)
                db.session.commit()
                login_user(webuser)
                return redirect(url_for('main.index'))
        flash('Invalid verify code')
        return redirect(url_for('.login_codeverify', code=code, num=num))
    return render_template('auth/logincodeverify.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/resendconfirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    text = render_template('auth/email/confirm.txt', user=current_user, token=token)
    sendmail(current_user.email, 'Confirm Your Account', text)
    flash('A new confirmation email has been sent to you by your registered email')
    return redirect(url_for('main.index'))


@auth.route('/changepwd', methods=['GET', 'POST'])
@login_required
def changepwd():
    form = ChangePwdForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.oldpwd.data):
            current_user.password = form.newpwd.data
            db.session.add(current_user)
            db.session.commit()
            flash('You have changed your password!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template('auth/changepwd.html', form=form)


@auth.route('/resetpwdemail', methods=['GET', 'POST'])
def resetpwdemail():
    form = ResetPwdEmailForm()
    if form.validate_on_submit():
        user = WebUser.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            text = render_template('auth/email/resetpwdemail.txt', user=current_user, token=token)
            sendmail(user.email, 'Reset Your Password', text)
            flash('Have send a email to you')
            return redirect(url_for('auth.login'))
        else:
            flash('This email is not registered')
    return render_template('auth/resetpwdemail.html', form=form)


@auth.route('/resetpwd/<token>', methods=['GET', 'POST'])
def resetpwd(token):
    form = ResetPwdForm()
    if form.validate_on_submit():
        user = WebUser.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid Email')
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.newpwd.data):
            flash('Your password has been reset')
            return redirect(url_for('auth.login'))
        else:
            flash('Reset Password Failed')
            return redirect(url_for('main.index'))
    return render_template('auth/resetpwd.html', form=form)


@auth.route('/changemail')
@login_required
def changemail():
    return "功能还未实现，敬请期待"
