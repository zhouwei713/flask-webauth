# coding = utf-8
"""
@author: zhou
@time:2019/2/12 14:08
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..models import WebUser
from wtforms import ValidationError


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z0-9_.]*$', 0,
                                              '用户名只能是字母，数字，点号或者下划线。')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='两次输入的密码需要一致。')
    ])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if WebUser.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已经存在。')

    def validate_username(self, field):
        if WebUser.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经存在。')


class ChangePwdForm(FlaskForm):
    oldpwd = PasswordField('Old Password', validators=[DataRequired()])
    newpwd = PasswordField('New Password', validators=[DataRequired(),
                                                       EqualTo('newpwd2', message='两次输入的密码需要一致。')])
    newpwd2 = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')


class ResetPwdEmailForm(FlaskForm):
    email = StringField('Your Register Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')


class ResetPwdForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    newpwd = PasswordField('New Password', validators=[DataRequired(),
                                                       EqualTo('newpwd2', message='两次输入的密码需要一致。')])
    newpwd2 = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if WebUser.query.filter_by(email=field.data).first() is None:
            raise ValidationError('This Email is Invalid')
