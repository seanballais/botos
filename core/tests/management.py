from io import StringIO

from django.core import management
from django.contrib.auth.hashers import check_password
from django.test import TestCase

from core.models import (
    User, Batch, Section
)


class CreateSuperUserTest(TestCase):
    """ Tests the customized createsuperuser command. """
    @classmethod
    def setUpTestData(cls):
        cls._out = StringIO()
        management.call_command(
            'createsuperuser',
            username='admin',
            password='root',
            email='admin@admin.com',
            stdout=cls._out
        )

    def test_superuser_gets_created(self):
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Superuser \'admin\' was not created.')

    def test_superuser_password_is_correct(self):
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Superuser \'admin\' was not created.')
        else:
            self.assertTrue(user.check_password('root'))

    def test_batch_0_exists(self):
        try:
            Batch.objects.get(year=0)
        except Batch.DoesNotExist:
            self.fail('Batch for superusers, 0, does not exist.')

    def test_section_superusers_exists(self):
        try:
            Section.objects.get(section_name='Superusers')
        except Section.DoesNotExist:
            self.fail(
                'Section for superusers, \'Superusers\', does not exist.'
            )

    def test_superuser_has_batch_0(self):
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Superuser \'admin\' got the wrong batch.')
        else:
            self.assertEquals(user.batch.year, 0)

    def test_superuser_has_section_superuser(self):
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Superuser \'admin\' got the wrong section.')
        else:
            self.assertEquals(user.section.section_name, 'Superusers')

