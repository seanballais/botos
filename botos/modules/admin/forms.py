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

        section_list.sort()
        return section_list

    def __init__(self):
        """
        Initialize a few variables.
        """
        super(VoterCreationForm, self).__init__()
        self.section_id = self._get_section_list()


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

    def _get_batch_list(self):
        """
        Get a list of all batches but only including the name and ID.

        :return: List of the batches.
        """
        batch_list = []
        temp_batch_list = controllers.VoterBatch.get_all()
        for batch in temp_batch_list:
            list_batch_item = [
                batch.id,
                batch.section_names
            ]

            batch_list.append(list_batch_item)

        batch_list.sort()
        return batch_list

    def __init__(self):
        """
        Initialize a few variables.
        """
        super(VoterSectionCreationForm, self).__init__()
        self.batches = self._get_batch_list()

class CandidateCreationForm(Form):
    """From for creating candidates."""


class CandidatePartyCreationForm(Form):
    """Form for creating candidate parties."""


class CandidatePositionCreationForm(Form):
    """Form for creating candidate positions."""


