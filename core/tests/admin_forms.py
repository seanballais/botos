import os
from unittest import mock

from django.conf import settings
from django.test import TestCase

from core.forms.admin import (
    ElectionSettingsCurrentTemplateForm, ElectionSettingsElectionStateForm,
    ElectionSettingsPubPrivKeysForm
)
from core.models (
    User, Batch, Section
)
from core.utils import AppSettings


class ElectionSettingsCurrentTemplateFormTest(TestCase):
    """
    Tests the current template form of the election settings.

    This form must only contain a single dropdown field. The default value for
    the text field must be 'default' or whatever is set in the app settings,
    but with higher priority on the latter.
    """
    @classmethod
    def setUpClass(cls):
        cls._batch = Batch.objects.create(year=2019)
        cls._section = Section.objects.create(section_name='Section')
        cls._admin_batch = Batch.objects.create(year=0)
        cls._admin_section = Section.objects.create(section_name='Superusers')

        User.objects.create_user(
            username='admin',
            email='admin@admin.com',
            password='root',
            batch=cls._admin_batch,
            section=cls._admin_section
        )

        self.client.login(username='admin', password='root')

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
             mock.patch('os.isdir') as mocked_isdir:
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
            mocked_isdir.side_effect = lambda f: 'file' not in f

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
            mocked_isdir.assert_called_with(*dir_contents)


class ElectionSettingsElectionStateFormTest(TestCase):
    """
    Tests the current template form of the election settings.

    This form must only contain a single text field.
    """
    pass


class ElectionSettingsPubPrivKeysFormTest(TestCase):
    """
    Tests the current template form of the election settings.

    This form must only contain a single text field.
    """
    pass
