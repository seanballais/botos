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

from botos.modules.app_data import controllers


class AdminCreationForm(Form):
    """Form for creating admins."""

    username = StringField('username',
                           validators=[DataRequired()],
                           render_kw={
                               'id': "register-admin-username",
                               'placeholder': "Enter the username"
                           })
    password = PasswordField('password',
                             validators=[DataRequired()],
                             render_kw={
                                 'id': "register-admin-password",
                                 'placeholder': "Enter the password"
                             })
    role     = SelectField('role',
                           choices=[
                               ['admin', 'Admin'],
                               ['viewer', 'Viewer']
                           ],
                           validators=[DataRequired()],
                           render_kw={
                               'id': "register-admin-role"
                           })


class VoterCreationForm(Form):
    """Form for creating voters."""
    pass


class VoterSectionCreationForm(Form):
    """Form for creating voter sections."""

    num_voters = StringField('username',
                             validators=[DataRequired()],
                             render_kw={
                                 'id': "register-admin-username",
                                 'placeholder': "Enter the username"
                             })
    section    = SelectField('role',
                             choices=_get_section_list(),
                             validators=[DataRequired()],
                             render_kw={
                                 'id': "register-admin-role"
                             })

    def _get_section_list(self):
        """
        Get a list of all sections but only including the name and ID.

        :return: List of the sections.
        """
        section_list = []
        temp_section_list = controllers.VoterSection.get_all()
        for section in temp_section_list:
            list_section_item = [
                section.id,
                section.section_names
            ]

            section_list.append(list_section_item)

        return section_list.sort()

