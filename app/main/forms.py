# coding = utf-8
"""
@author: zhou
@time:2019/2/18 14:14
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[Length(0, 64)])
    nickname = StringField('Nickname', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
