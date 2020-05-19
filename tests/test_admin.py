from django import forms
from django.test import TestCase

from core.admin import CustomUserCreationForm
from core.models import (
    User, Batch, Section
)


class CustomUserCreationFormTest(TestCase):
    """
    Tests the CustomUserCreationForm formm in core/admin.py.
    """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=0)
        cls._section = Section.objects.create(section_name='Superusers')

    def test_user_does_not_exist(self):
        data = {
            'username': 'admin',
            'email': 'admin@botos.system',
            'password1': '!(root)@',
            'password2': '!(root)@',
            'batch': self._batch,
            'section': self._section
        }
        form = CustomUserCreationForm(data)

        form.is_valid()  # This calls clean_username() down the line.

        # is_valid() handles exceptions raised by clean_username(), creates an
        # HTML snippet displaying the error, and stores it in a dict. As such,
        # we cannot catch the exception raised by clean_username().
        # Fortunately, we can use .has_error() to check if any exceptions has
        # been raised by any of the clean methods in the form object, including
        # any exceptions raised by clean_username().
        self.assertFalse(form.has_error('username'))

    def test_username_already_exists(self):
        User.objects.create(
            username='admin',
            batch=self._batch,
            section=self._section,
            is_staff=True,
            is_superuser=True
        )

        try:
            u = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('User, \'admin\' was not created.')

        data = {
            'username': 'admin',
            'email': 'admin@botos.system',
            'password1': '!(root)@',
            'password2': '!(root)@',
            'batch': self._batch,
            'section': self._section
        }
        form = CustomUserCreationForm(data)
        form.is_valid()  # This calls clean_username() down the line.

        # is_valid() handles exceptions raised by clean_username(), creates an
        # HTML snippet displaying the error, and stores it in a dict. As such,
        # we cannot catch the exception raised by clean_username().
        # Fortunately, we can use .has_error() to check if any exceptions has
        # been raised by any of the clean methods in the form object, including
        # any exceptions raised by clean_username().
        self.assertTrue(form.has_error('username'))
