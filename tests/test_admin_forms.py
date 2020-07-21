from abc import ABC
from distutils.dir_util import copy_tree
import json
import os
import shutil
from unittest import mock

from bs4 import BeautifulSoup

from django.conf import settings
from django.template.backends.django import DjangoTemplates
from django.template.base import Template
from django.test import (
    RequestFactory, TestCase
)
from django.urls import reverse

from core.forms.admin import (
    ElectionSettingsCurrentTemplateForm, ElectionSettingsElectionStateForm,
    AdminChangeForm, AdminCreationForm, VoterChangeForm,
    VoterCreationForm, CandidateForm
)
from core.models import (
    User, Batch, Section, Candidate, CandidateParty, CandidatePosition, Vote,
    UserType, Election, VoterProfile
)
from core.utils import AppSettings


class MockSuperUser:
    def has_perm(self, perm):
        return True


class BaseAdminFormTest(ABC):
    """
    Base test for all admin forms.
    """
    @classmethod
    def setUpTestData(cls):
        user = User(
            username='admin',
            email='admin@admin.com',
            type=UserType.ADMIN
        )
        user.set_password('root')
        user.save()


class ElectionSettingsCurrentTemplateFormTest(BaseAdminFormTest, TestCase):
    """
    Tests the current template form of the election settings.

    This form must only contain a single dropdown field. The default value for
    the text field must be 'default' or whatever is set in the app settings,
    but with higher priority on the latter.
    """
    def setUp(self):
        self.client.login(username='admin', password='root')

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
        response = self.client.get(reverse('admin-election-index'))
        form_fields = response.context['current_template_form'].fields
        form_template_name = form_fields['template_name']
        self.assertEquals(
            form_template_name.initial,
            'default'
        )

    def test_value_of_dropdown_field_if_template_set(self):
        AppSettings().set('template', 'yes-or-yes')

        # We have to create an actual yes-or-yes template since I still do not
        # know how to mock a template in Django. Let's just copy the default
        # template and rename the copied folder as 'yes-or-yes'. This will
        # remove the need to create a unique template and make this test
        # simpler. We may do this since this test is just going to test whether
        # or not the correct template is being rendered by Botos. This test
        # does not require the creation of a *unique* template. Future
        # revisions of Botos may choose to redo this in favour of mocking
        # instead.
        template_dir = os.path.join(settings.BASE_DIR, 'botos/templates')
        default_template_dir = os.path.join(template_dir, 'default')
        new_template_dir = os.path.join(template_dir, 'yes-or-yes')
        copy_tree(default_template_dir, new_template_dir)

        # Dropdown field should have a value of `yes-or-yes`.
        response = self.client.get(reverse('admin-election-index'))
        form_fields = response.context['current_template_form'].fields
        form_template_name = form_fields['template_name']
        self.assertEquals(form_template_name.initial, 'yes-or-yes')

        # And, of course, we better clean up the mess we did and delete the
        # 'yes-or-yes' template we created.
        shutil.rmtree(new_template_dir)

    def test_values_of_dropdown_field_if_you_only_have_default_template(self):
        # Dropdown field should only have an option of `default`.
        response = self.client.get(reverse('admin-election-index'))
        form_fields = response.context['current_template_form'].fields
        form_template_name = form_fields['template_name']
        self.assertEquals(
            form_template_name.choices,
            [ ('default', 'default') ]
        )

    def test_values_of_dropdown_field_with_many_templates(self):
        # Assume that we have the following fake templates:
        #    - yes-or-yes
        #    - nothing-at-all
        #    - pink-lemonade
        #
        # The choices will be based on the list of folders immediately under
        # the `botos/tempates/` folder.

        template_dir = os.path.join(settings.BASE_DIR, 'botos/templates')

        # Making "physical" folders is a hassle, so let's mock them instead.
        with mock.patch('os.listdir') as mocked_listdir, \
             mock.patch('os.path.isdir') as mocked_path_isdir:
            # Let's create the folders for the fake templates first.
            mocked_listdir.return_value = [
                'default',
                'nothing-at-all',
                'pink-lemonade',
                'yes-or-yes'
            ]
            mocked_path_isdir.side_effect = lambda f: 'file' not in f

            # Now test.
            response = self.client.get(reverse('admin-election-index'))
            response = self.client.get(reverse('admin-election-index'))
            form_fields = response.context['current_template_form'].fields
            form_template_name = form_fields['template_name']
            self.assertEquals(
                sorted(form_template_name.choices),
                [
                    ('default', 'default'),
                    ('nothing-at-all', 'nothing-at-all'),
                    ('pink-lemonade', 'pink-lemonade'),
                    ('yes-or-yes', 'yes-or-yes')
                ]
            )

            # Make sure the correct directory has been passed to os.listdir().
            # Note that the Django uses os.listdir(). Since we mocked the
            # aforementioned function, Django will be using the mocked version
            # of the function. As a result, Django will cause the mocked
            # os.listdir() to have additional mock calls (e.g. calls to
            # somewhere in the Django admin folder). This is the reason why we
            # are using assert_any_call() instead of assert_called_with().
            # However, this is what I would consider an unstable mock since
            # this mock can unintentionally and unknowingly alter Django's
            # behaviour. As such, future revisions of this test must limit
            # mocking of os.listdir() to just the form,
            # ElectionSettingsCurrentTemplateForm.
            mocked_listdir.assert_any_call(template_dir)

    def test_form_skips_admin_folder(self):
        # Assume that we have the following fake templates:
        #    - yes-or-yes
        #    - nothing-at-all
        #    - pink-lemonade
        #
        # The admin folder in the templates is not intended to be a template.
        # Rather, it stores the static files of Django Admin. As such, we must
        # skip it.

        template_dir = os.path.join(settings.BASE_DIR, 'botos/templates')

        # Mock the contents of the template directory.
        with mock.patch('os.listdir') as mocked_listdir, \
             mock.patch('os.path.isdir') as mocked_path_isdir:
            # Set up mocks.
            dir_contents = [
                'default',
                'nothing-at-all',
                'pink-lemonade',
                'yes-or-yes',
                'admin'
            ]
            mocked_listdir.return_value = dir_contents
            mocked_path_isdir.side_effect = lambda f: 'file' not in f

            # Now test.
            response = self.client.get(reverse('admin-election-index'))
            form_fields = response.context['current_template_form'].fields
            form_template_name = form_fields['template_name']
            self.assertEquals(
                sorted(form_template_name.choices),
                [
                    ('default', 'default'),
                    ('nothing-at-all', 'nothing-at-all'),
                    ('pink-lemonade', 'pink-lemonade'),
                    ('yes-or-yes', 'yes-or-yes')
                ]
            )

            # Make sure the correct directory has been passed to os.listdir().
            # Note that the Django uses os.listdir(). Since we mocked the
            # aforementioned function, Django will be using the mocked version
            # of the function. As a result, Django will cause the mocked
            # os.listdir() to have additional mock calls (e.g. calls to
            # somewhere in the Django admin folder). This is the reason why we
            # are using assert_any_call() instead of assert_called_with().
            # However, this is what I would consider an unstable mock since
            # this mock can unintentionally and unknowingly alter Django's
            # behaviour. As such, future revisions of this test must limit
            # mocking of os.listdir() to just the form,
            # ElectionSettingsCurrentTemplateForm.
            mocked_listdir.assert_any_call(template_dir)

    def test_form_shows_correct_template_choices(self):
        # Assume that we have the following fake templates:
        #    - yes-or-yes
        #    - nothing-at-all
        #    - pink-lemonade
        #
        # The choices will be based on the list of folders immediately under
        # the `botos/tempates/` folder. Names of files must not appear in the
        # choices.

        template_dir = os.path.join(settings.BASE_DIR, 'botos/templates')

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
            response = self.client.get(reverse('admin-election-index'))
            form_fields = response.context['current_template_form'].fields
            form_template_name = form_fields['template_name']
            self.assertEquals(
                sorted(form_template_name.choices),
                [
                    ('default', 'default'),
                    ('nothing-at-all', 'nothing-at-all'),
                    ('pink-lemonade', 'pink-lemonade'),
                    ('yes-or-yes', 'yes-or-yes')
                ]
            )

            # Make sure the correct directory has been passed to os.listdir().
            # Note that the Django uses os.listdir(). Since we mocked the
            # aforementioned function, Django will be using the mocked version
            # of the function. As a result, Django will cause the mocked
            # os.listdir() to have additional mock calls (e.g. calls to
            # somewhere in the Django admin folder). This is the reason why we
            # are using assert_any_call() instead of assert_called_with().
            # However, this is what I would consider an unstable mock since
            # this mock can unintentionally and unknowingly alter Django's
            # behaviour. As such, future revisions of this test must limit
            # mocking of os.listdir() to just the form,
            # ElectionSettingsCurrentTemplateForm.
            mocked_listdir.assert_any_call(template_dir)

            # We're using assert_any_call() for the same reasons as above.
            # It should be noted Django will also use the mocked
            # os.path.isdir() instead of the actuall os.path.isdir().
            for dir_content in dir_contents:
                mocked_path_isdir.assert_any_call(
                    os.path.join(template_dir, dir_content)
                )


class ElectionSettingsElectionStateFormTest(BaseAdminFormTest, TestCase):
    """
    Tests the current template form of the election settings.

    This form must only contain a single radio box.
    """
    def setUp(self):
        self.client.login(username='admin', password='root')

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
        # State should default to "closed".
        response = self.client.get(reverse('admin-election-index'))
        form_fields = response.context['current_election_state_form'].fields
        form_state = form_fields['state']
        self.assertEquals(form_state.initial, 'closed')

    def test_value_of_radio_box_if_state_have_been_set(self):
        AppSettings().set('election_state', 'open')

        # Dropdown field should have a value of `yes-or-yes`.
        response = self.client.get(reverse('admin-election-index'))
        form_fields = response.context['current_election_state_form'].fields
        form_state = form_fields['state']
        self.assertEquals(form_state.initial, 'open')


class UserCreationFormTest(TestCase):
    """
    Tests the user creation forms in core/forms/admin.py.
    """
    @classmethod
    def setUpTestData(cls):
        cls._election = Election.objects.create(name='Election')
        cls._batch = Batch.objects.create(year=0, election=cls._election)
        cls._section = Section.objects.create(section_name='Superusers')

    def test_adding_new_voter_from_form(self):
        data = {
            'username': 'voter',
            'email': 'voter@botos.system',
            'password1': '!(root)@',
            'password2': '!(root)@'
        }
        form = VoterCreationForm(data)

        form.is_valid()  # This calls clean_username() down the line.

        # is_valid() handles exceptions raised by clean_username(), creates an
        # HTML snippet displaying the error, and stores it in a dict. As such,
        # we cannot catch the exception raised by clean_username().
        # Fortunately, we can use .has_error() to check if any exceptions has
        # been raised by any of the clean methods in the form object, including
        # any exceptions raised by clean_username().
        self.assertFalse(form.has_error('username'))

    def test_adding_new_admin_from_form(self):
        data = {
            'username': 'admin',
            'email': 'admin@botos.system',
            'password1': '!(root)@',
            'password2': '!(root)@',
        }
        form = AdminCreationForm(data)

        form.is_valid()  # This calls clean_username() down the line.

        # is_valid() handles exceptions raised by clean_username(), creates an
        # HTML snippet displaying the error, and stores it in a dict. As such,
        # we cannot catch the exception raised by clean_username().
        # Fortunately, we can use .has_error() to check if any exceptions has
        # been raised by any of the clean methods in the form object, including
        # any exceptions raised by clean_username().
        self.assertFalse(form.has_error('username'))

    def test_adding_preexisting_voter_from_form(self):
        User.objects.create(username='voter', type=UserType.VOTER)

        try:
            u = User.objects.get(username='voter')
        except User.DoesNotExist:
            self.fail('User, \'voter\', was not created.')

        data = {
            'username': 'voter',
            'email': 'voter@botos.system',
            'password1': '!(root)@',
            'password2': '!(root)@'
        }
        form = VoterCreationForm(data)
        form.is_valid()  # This calls clean_username() down the line.

        # is_valid() handles exceptions raised by clean_username(), creates an
        # HTML snippet displaying the error, and stores it in a dict. As such,
        # we cannot catch the exception raised by clean_username().
        # Fortunately, we can use .has_error() to check if any exceptions has
        # been raised by any of the clean methods in the form object, including
        # any exceptions raised by clean_username().
        self.assertTrue(form.has_error('username'))

    def test_adding_preexisting_admin_from_form(self):
        User.objects.create(username='admin', type=UserType.ADMIN)

        try:
            u = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('User, \'admin\' was not created.')

        data = {
            'username': 'admin',
            'email': 'admin@botos.system',
            'password1': '!(root)@',
            'password2': '!(root)@'
        }
        form = AdminCreationForm(data)
        form.is_valid()  # This calls clean_username() down the line.

        # is_valid() handles exceptions raised by clean_username(), creates an
        # HTML snippet displaying the error, and stores it in a dict. As such,
        # we cannot catch the exception raised by clean_username().
        # Fortunately, we can use .has_error() to check if any exceptions has
        # been raised by any of the clean methods in the form object, including
        # any exceptions raised by clean_username().
        self.assertTrue(form.has_error('username'))


class CandidateFormTest(TestCase):
    # Right now, we are not testing chained fields (the ones using a
    # Select2QuerySetView) since it seems that chained fields only react when
    # in a view. Note that we're just testing the form itself here.
    @classmethod
    def setUpTestData(cls):
        cls._election0 = Election.objects.create(name='Election 0')
        cls._election1 = Election.objects.create(name='Election 1')

        cls._batch0 = Batch.objects.create(year=0, election=cls._election0)
        cls._batch1 = Batch.objects.create(year=1, election=cls._election1)

        cls._section0 = Section.objects.create(section_name='Section 0')
        cls._section1 = Section.objects.create(section_name='Section 1')

        cls._user0 = User.objects.create(username='user0')
        cls._user1 = User.objects.create(username='user1')

        VoterProfile.objects.create(
            user=cls._user0,
            batch=cls._batch0,
            section=cls._section0
        )
        VoterProfile.objects.create(
            user=cls._user1,
            batch=cls._batch1,
            section=cls._section1
        )

        cls._candidate_party0 = CandidateParty.objects.create(
            party_name='Awesome Party 0',
            election=cls._election0
        )
        cls._candidate_party1 = CandidateParty.objects.create(
            party_name='Another Party 0',
            election=cls._election0
        )
        cls._candidate_party2 = CandidateParty.objects.create(
            party_name='Another Party 1',
            election=cls._election1
        )
        cls._candidate_position0 = CandidatePosition.objects.create(
            position_name='Awesome Position 0',
            position_level=0,
            election=cls._election0
        )
        cls._candidate_position1 = CandidatePosition.objects.create(
            position_name='Awesome Position 1',
            position_level=1,
            election=cls._election0
        )
        cls._candidate_position2 = CandidatePosition.objects.create(
            position_name='Awesome Position 2',
            position_level=0,
            election=cls._election1
        )
        cls._form = CandidateForm

    def test_adding_new_candidate_from_form(self):
        data = {
            'user': self._user0.pk,
            'election': self._election0.pk,
            'party': self._candidate_party0.pk,
            'position': self._candidate_position0.pk
        }
        form = self._form(data)

        form.is_valid()  # This calls clean_username() down the line.

        # is_valid() handles exceptions raised by clean_username(), creates an
        # HTML snippet displaying the error, and stores it in a dict. As such,
        # we cannot catch the exception raised by clean_username().
        # Fortunately, we can use .has_error() to check if any exceptions has
        # been raised by any of the clean methods in the form object, including
        # any exceptions raised by clean_username().
        self.assertFalse(form.has_error('user'))

    def test_adding_preexisting_from_form(self):
        try:
            Candidate.objects.create(
                user=self._user0,
                party=self._candidate_party0,
                position=self._candidate_position0,
                election=self._election0
            )
        except Candidate.DoesNotExist:
            self.fail('Candidate was not created.')

        data = {
            'user': self._user0.pk,
            'election': self._election0.pk,
            'party': self._candidate_party0.pk,
            'position': self._candidate_position0.pk
        }
        form = self._form(data)

        form.is_valid()  # This calls clean_username() down the line.

        # is_valid() handles exceptions raised by clean_username(), creates an
        # HTML snippet displaying the error, and stores it in a dict. As such,
        # we cannot catch the exception raised by clean_username().
        # Fortunately, we can use .has_error() to check if any exceptions has
        # been raised by any of the clean methods in the form object, including
        # any exceptions raised by clean_username().
        self.assertTrue(form.has_error('user'))
