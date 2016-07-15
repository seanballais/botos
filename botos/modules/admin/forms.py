# botos/modules/admin/forms.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

""" Forms for the admin page.

"""

from flask_wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import DataRequired


class AdminLoginForm(Form):
    """Login form for the admins."""

    username = StringField('username',
                           validators=[DataRequired()],
                           render_kw={
                               'id': "login-username",
                               'placeholder': "Enter your username"
                           }
                           )
    password = PasswordField('password',
                             validators=[DataRequired()],
                             render_kw={
                                 'id': "login-password",
                                 'placeholder': "Enter your password"
                             }
                             )