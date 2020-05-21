# This test is partly based from:
#     https://www.argpar.se/posts/programming/testing-django-admin/
from django import forms
from django.contrib.admin.sites import AdminSite
from django.test import (
    RequestFactory, TestCase
)

from core.admin import (
    AdminCreationForm, VoterCreationForm, AdminUserAdmin, VoterAdmin,
    VoterProfileInline, AdminUser, Voter
)
from core.models import (
    User, Batch, Section, VoterProfile, UserType
)


class MockSuperUser:
    def has_perm(self, perm):
        return True


class AdminUserAdminTest(TestCase):
    """
    Tests the Admin user admin.
    """
    def test_queryset_returns_with_admin_users_only(self):
        User.objects.create(username='admin', type=UserType.ADMIN)
        User.objects.create(username='voter', type=UserType.VOTER)

        admin = AdminUserAdmin(model=AdminUser, admin_site=AdminSite())
        query = admin.get_queryset(None)

        self.assertEqual(query.first().type, UserType.ADMIN)
        self.assertEqual(query.count(), 1)


class VoterAdminTest(TestCase):
    """
    Tests the Voter admin.
    """
    def test_queryset_returns_with_voters_only(self):
        User.objects.create(username='admin', type=UserType.ADMIN)
        User.objects.create(username='voter', type=UserType.VOTER)

        admin = VoterAdmin(model=Voter, admin_site=AdminSite())
        query = admin.get_queryset(None)

        self.assertEqual(query.first().type, UserType.VOTER)
        self.assertEqual(query.count(), 1)


class UserCreationFormTest(TestCase):
    """
    Tests the user creation forms in core/admin.py.
    """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=0)
        cls._section = Section.objects.create(section_name='Superusers')

        request_factory = RequestFactory()
        cls._request = request_factory.get('/admin')
        cls._request.user = MockSuperUser()

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

    def test_add_new_voter_from_admin(self):
        # No need to check if a voter profile gets created because Django
        # provides us with an assurance that one will be created because
        # we created an admin inline for VoterProfile to the VoterAdmin.
        admin = VoterAdmin(Voter, AdminSite())
        voter = User(username='voter')
        admin.save_model(self._request, voter, None, None)

        try:
            voter = User.objects.get(username='voter')
        except User.DoesNotExist:
            self.fail('Voter was not created.')
        else:
            self.assertEqual(voter.type, UserType.VOTER)

    def test_add_new_admin_from_admin(self):
        # No need to check if a voter profile gets created because Django
        # provides us with an assurance that one will be created because
        # we created an admin inline for VoterProfile to the VoterAdmin.
        admin = AdminUserAdmin(AdminUser, AdminSite())
        admin_user = User(username='admin')
        admin.save_model(self._request, admin_user, None, None)

        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created.')
        else:
            self.assertEqual(admin_user.type, UserType.ADMIN)

    def test_voter_admin_has_voter_profile_inline(self):
        admin = VoterAdmin(Voter, AdminSite())
        self.assertTrue(lambda: VoterProfileInline in admin.inlines)


class AdminUserProxyUserTest(TestCase):
    """
    Tests the admin user admin list filter.
    """
    def test_save_admin_user_model(self):
        AdminUser.objects.create(username='admin')

        try:
            user = AdminUser.objects.get(username='admin')
        except AdminUser.DoesNotExist:
            self.fail('Admin was not created.')
        else:
            self.assertEqual(user.type, UserType.ADMIN)

class VoterProxyUserTest(TestCase):
    """
    Tests the admin user admin list filter.
    """
    def test_save_voter_model(self):
        Voter.objects.create(username='voter')

        try:
            user = Voter.objects.get(username='voter')
        except AdminUser.DoesNotExist:
            self.fail('Voter was not created.')
        else:
            self.assertEqual(user.type, UserType.VOTER)
