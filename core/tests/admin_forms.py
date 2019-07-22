from abc import ABC
import os
from unittest import mock

from bs4 import BeautifulSoup

from django.conf import settings
from django.test import TestCase

from core.forms.admin import (
    ElectionSettingsCurrentTemplateForm, ElectionSettingsElectionStateForm
)
from core.models import (
    User, Batch, Section
)
from core.utils import AppSettings


class BaseAdminFormTest(ABC, TestCase):
    """
    Base test for all admin forms.
    """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=2019)
        cls._section = Section.objects.create(section_name='Section')
        cls._admin_batch = Batch.objects.create(year=0)
        cls._admin_section = Section.objects.create(section_name='Superusers')

        User.objects.create_user(
            username='admin',
            email='admin@admin.com',
            password='root',
            batch=cls._admin_batch,
            section=cls._admin_section,
            is_superuser=True
        )


class ElectionSettingsCurrentTemplateFormTest(BaseAdminFormTest):
    """
    Tests the current template form of the election settings.

    This form must only contain a single dropdown field. The default value for
    the text field must be 'default' or whatever is set in the app settings,
    but with higher priority on the latter.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_valid_data(self):
        form = ElectionSettingsCurrentTemplateForm(
            data={
                'template_name': 'default'
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = ElectionSettingsCurrentTemplateForm(
            data={
                'template_name': ''
            }
        )
        self.assertFalse(form.is_valid())

    def test_value_of_dropdown_field_if_no_template_set_yet(self):
        # Dropdown field should have a value of `default`.
        response = self.client.get('/admin/election')
        self.assertEquals(
            response.context['current_template_form'].initial['template_name'],
            'default'
        )

    def test_value_of_dropdown_field_if_template_set(self):
        AppSettings().set('template', 'yes-or-yes')

        # Dropdown field should have a value of `yes-or-yes`.
        response = self.client.get('/admin/election')
        self.assertEquals(
            response.context['current_template_form'].initial['template_name'],
            'yes-or-yes'
        )

    def test_values_of_dropdown_field_if_you_only_have_default_template(self):
        # Dropdown field should only have an option of `default`.
        response = self.client.get('/admin/election')
        self.assertEquals(
            response.context['current_template_form'].choices['template_name'],
            [ 'default' ]
        )

    def test_values_of_dropdown_field_with_many_templates(self):
        # Assume that we have the following fake templates:
        #    - yes-or-yes
        #    - nothing-at-all
        #    - pink-lemonade
        #
        # The choices will be based on the list of folders immediately under
        # the `botos/tempates/` folder.

        # Making "physical" folders is a hassle, so let's mock them instead.
        with mock.patch('os.listdir') as mocked_listdir:
            # Let's create the folders for the fake templates first.
            mocked_listdir.return_value = [
                'default',
                'nothing-at-all',
                'pink-lemonade',
                'yes-or-yes'
            ]

            # Now test.
            response = self.client.get('/admin/election')
            template_form_context = response.context['current_template_form']
            self.assertEquals(
                sorted(template_form_context.choices['template_name']),
                [ 'default', 'nothing-at-all', 'pink-lemonade', 'yes-or-yes' ]
            )

            # Make sure the correct directory has been passed to os.listdir().
            mocked_listdir.assert_called_with(
                os.path.join(settings.BASE_DIR, 'botos/templates')
            )

    def test_form_skips_admin_folder(self):
        # Assume that we have the following fake templates:
        #    - yes-or-yes
        #    - nothing-at-all
        #    - pink-lemonade
        #
        # The admin folder in the templates is not intended to be a template.
        # Rather, it stores the static files of Django Admin. As such, we must
        # skip it.

        # Mock the contents of the template directory.
        with mock.patch('os.listdir') as mocked_listdir
            # Set up mocks.
            dir_contents = [
                'default',
                'nothing-at-all',
                'pink-lemonade',
                'yes-or-yes',
                'admin'
            ]
            mocked_listdir.return_value = dir_contents

            # Now test.
            response = self.client.get('/admin/election')
            template_form_context = response.context['current_template_form']
            self.assertEquals(
                sorted(template_form_context.choices['template_name']),
                [ 'default', 'nothing-at-all', 'pink-lemonade', 'yes-or-yes' ]
            )

            # Make sure the correct directory has been passed to os.listdir().
            mocked_listdir.assert_called_with(
                os.path.join(settings.BASE_DIR, 'botos/templates')
            )

    def test_form_shows_correct_template_choices(self):
        # Assume that we have the following fake templates:
        #    - yes-or-yes
        #    - nothing-at-all
        #    - pink-lemonade
        #
        # The choices will be based on the list of folders immediately under
        # the `botos/tempates/` folder. Names of files must not appear in the
        # choices.

        # Mock the contents of the template directory.
        with mock.patch('os.listdir') as mocked_listdir, \
             mock.patch('os.path.isdir') as mocked_path_isdir:
            # Set up mocks.
            dir_contents = [
                'default',
                'nothing-at-all',
                'pink-lemonade',
                'yes-or-yes',
                'file123',
                'h3h3file',
                'justanotherfile'
            ]
            mocked_listdir.return_value = dir_contents
            mocked_path_isdir.side_effect = lambda f: 'file' not in f

            # Now test.
            response = self.client.get('/admin/election')
            template_form_context = response.context['current_template_form']
            self.assertEquals(
                sorted(template_form_context.choices['template_name']),
                [ 'default', 'nothing-at-all', 'pink-lemonade', 'yes-or-yes' ]
            )

            # Make sure the correct directory has been passed to os.listdir().
            mocked_listdir.assert_called_with(
                os.path.join(settings.BASE_DIR, 'botos/templates')
            )
            mocked_path_isdir.assert_called_with(*dir_contents)


class ElectionSettingsElectionStateFormTest(BaseAdminFormTest):
    """
    Tests the current template form of the election settings.

    This form must only contain a single radio box.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_valid_data(self):
        form = ElectionSettingsElectionStateForm(
            data={
                'state': 'open'
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = ElectionSettingsElectionStateForm(
            data={
                'state': 'x'
            }
        )
        self.assertFalse(form.is_valid())

    def test_value_of_radio_box_if_state_have_not_been_set_yet(self):
        # State should default to closed.
        response = self.client.get('/admin/election')
        self.assertEquals(
            response.context['current_election_state_form'].initial['state'],
            'closed'
        )

    def test_value_of_radio_box_if_state_have_been_set(self):
        AppSettings().set('election_state', 'open')

        # Dropdown field should have a value of `yes-or-yes`.
        response = self.client.get('/admin/election')
        self.assertEquals(
            response.context['current_election_state_form'].initial['state'],
            'open'
        )


class ElectionSettingsPubPrivKeysFormTest(BaseAdminFormTest):
    """
    Tests the current template form of the election settings.

    This form must only contain a single text field.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_button_is_active_if_there_are_no_votes(self):
        response = self.client.get('/admin/election')
        self.assertTrue(self._is_form_button_enabled(response.content))

    def test_button_is_disabled_if_votes_are_present(self):
        # Create the test non-superuser.
        _user = User.objects.create(
            username='juan',
            batch=self._batch,
            section=self._section
        )
        _party = CandidateParty.objects.create(party_name='Awesome Party')
        _position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        _candidate = Candidate.objects.create(
            user=_user,
            party=_party,
            position=_position
        )

        # Create a dummy vote.
        _vote = Vote.objects.create(
            user=_user,
            candidate=_candidate,
            vote_cipher=json.dumps(dict())
        )

        # Now test.
        response = self.client.get('/admin/election')
        self.assertFalse(self._is_form_button_enabled(response.content))

    def test_button_is_active_if_elections_are_closed(self):
        AppSettings().set('election_state', 'closed')

        response = self.client.get('/admin/election')
        self.assertTrue(self._is_form_button_enabled(response.content))

    def test_button_is_disabled_if_elections_are_open(self):
        AppSettings().set('election_state', 'open')

        response = self.client.get('/admin/election')
        self.assertFalse(self._is_form_button_enabled(response.content))

    def _is_form_button_enabled(self, view_html):
        view_html_soup = BeautifulSoup(view_html, 'html.parser')
        form_button = view_html_soup.find('form', id='pub-priv-key') \
                                    .find('button', type='submit')

        # Sure, we can just check if "disabled" is inside the HTML string of
        # form_button. However, the output would be incorrect if the button is
        # not actually disabled, but its HTML string has a substring
        # "disabled".
        return not form_button.has_attr('disabled')
