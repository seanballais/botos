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
from wtforms import IntegerField
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
    section_id = []
    num_voters = IntegerField('num_voters',
                              validators=[DataRequired()],
                              render_kw={
                                  'id': "register-admin-username",
                                  'placeholder': "Enter the username"
                              })

    section    = SelectField('role',
                             choices=section_id,
                             validators=[DataRequired()],
                             render_kw={
                                 'id': "register-admin-role"
                             })

    def __init__(self,
                 sections
                 ):
        """
        Initialize a few variables.

        :param sections: List of sections.
        """
        super(VoterCreationForm, self).__init__()
        self.section_id = sections


class VoterBatchCreationForm(Form):
    """For for creating voter batches."""
    batch_name = StringField('batch_name',
                             validators=[DataRequired()],
                             render_kw={
                                 'id': "register-batch-name",
                                 'placeholder': "Enter the batch name"
                             })


class VoterSectionCreationForm(Form):
    """Form for creating voter sections."""
    batches      = []
    section_name = StringField('section_name',
                               validators=[DataRequired()],
                               render_kw={
                                   'id': "register-section-name",
                                   'placeholder': "Enter the section name"
                               })

    batch        = SelectField('batch',
                               choices=batches,
                               validators=[DataRequired()],
                               render_kw={
                                   'id': "register-batch-category"
                               })

    def __init__(self,
                 batches
                 ):
        """
        Initialize a few variables.

        :param batches: List of batches.
        """
        super(VoterSectionCreationForm, self).__init__()
        self.batches = batches

class CandidateCreationForm(Form):
    """From for creating candidates."""


class CandidatePartyCreationForm(Form):
    """Form for creating candidate parties."""


class CandidatePositionCreationForm(Form):
    """Form for creating candidate positions."""


