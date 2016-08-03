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
from wtforms import FileField
from wtforms.validators import DataRequired

from botos.modules.admin.controllers import Utility


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
    num_voters = IntegerField('num_voters',
                              validators=[DataRequired()],
                              render_kw={
                                  'id': "register-admin-username",
                                  'placeholder': "Enter the number of voters"
                              })

    section    = SelectField('role',
                             choices=[],
                             coerce=int,
                             validators=[DataRequired()],
                             render_kw={
                                 'id': "register-admin-role"
                             })

    @classmethod
    def new(cls):
        """Create a new dynamically loading form."""
        form = cls()

        form.section.choices = Utility.get_section_list()
        return form


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
    section_name = StringField('section_name',
                               validators=[DataRequired()],
                               render_kw={
                                   'id': "register-section-name",
                                   'placeholder': "Enter the section name"
                               })

    batch        = SelectField('batch',
                               choices=[],
                               coerce=int,
                               validators=[DataRequired()],
                               render_kw={
                                   'id': "register-batch-category"
                               })

    @classmethod
    def new(cls):
        """Create a new dynamically loading form."""
        form = cls()

        form.batch.choices = Utility.get_batch_list()
        return form


class CandidateCreationForm(Form):
    """From for creating candidates."""
    first_name  = StringField('first_name',
                              validators=[DataRequired()],
                              render_kw={
                                  'id': "register-candidate-first-name",
                                  'placeholder': "Enter candidate first name"
                              })
    last_name   = StringField('last_name',
                              validators=[DataRequired()],
                              render_kw={
                                  'id': "register-candidate-last-name",
                                  'placeholder': "Enter candidate last name"
                              })
    middle_name = StringField('middle_name',
                              validators=[DataRequired()],
                              render_kw={
                                  'id': "register-candidate-middle-name",
                                  'placeholder': "Enter candidate middle name"
                              })
    profile_pic = FileField('profile_pic',
                            validators=[DataRequired()],
                            render_kw={
                                'id': "register-candidate-profile-pic",
                                'placeholder': "Upload the candidate's picture. Minimum size of 140x140."
                            })
    position    = SelectField('batch',
                              choices=[],
                              coerce=int,
                              validators=[DataRequired()],
                              render_kw={
                                  'id': "register-candidate-position"
                              })
    party       = SelectField('batch',
                              choices=[],
                              coerce=int,
                              validators=[DataRequired()],
                              render_kw={
                                  'id': "register-party-position"
                              })

    @classmethod
    def new(cls):
        """Create a new dynamically loaded form."""
        form = cls()

        position_list = []
        temp_position_list = Utility.get_position_list()
        for position in temp_position_list:
            position_list.append([
                position[0],
                position[1]
            ])

        form.position.choices = position_list
        form.party.choices    = Utility.get_party_list()

        return form


class CandidatePartyCreationForm(Form):
    """Form for creating candidate parties."""
    party_name = StringField('party_name',
                             validators=[DataRequired()],
                             render_kw={
                                 'id': "register-party-name",
                                 'placeholder': "Enter the party name"
                             })


class CandidatePositionCreationForm(Form):
    """Form for creating candidate positions."""
    position_name = StringField('position_name',
                                validators=[DataRequired()],
                                render_kw={
                                    'id': "register-position-name",
                                    'placeholder': "Enter the batch name"
                                })
    level         = IntegerField('position_level',
                                 validators=[DataRequired()],
                                 render_kw={
                                     'id': "register-position-level",
                                     'placeholder': "Enter the position level"
                                 })