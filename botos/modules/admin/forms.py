# botos/modules/admin/forms.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

""" Forms for the voting page.

"""

from flask_wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms.validators import DataRequired


class AdminCreationForm(Form):
    """Login form for the voters."""

    username = StringField('username',
                           validators=[DataRequired()],
                           render_kw={
                               'id': "register-admin-username",
                               'placeholder': "Enter the username"
                           }
                           )
    password = PasswordField('password',
                             validators=[DataRequired()],
                             render_kw={
                                 'id': "register-admin-password",
                                 'placeholder': "Enter the password"
                             }
                             )
    role     = SelectField('role',
                           choices=[
                               ['admin', 'Admin'],
                               ['viewer', 'Viewer']
                           ],
                           validators=[DataRequired()],
                           render_kw={
                               'id': "register-admin-role"
                           })