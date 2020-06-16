# This test is partly based from:
#     https://www.argpar.se/posts/programming/testing-django-admin/
import json

from django import forms
from django.contrib.admin.sites import AdminSite
from django.test import (
    RequestFactory, TestCase
)
from django.urls import reverse

from core.admin import (
    AdminUserAdmin, VoterAdmin, VoterProfileInline, AdminUser, Voter,
    AdminCreationForm, VoterCreationForm, CandidateForm,
)
from core.models import (
    User, Batch, Section, VoterProfile, UserType, Candidate, CandidateParty,
    CandidatePosition, Election
)


class MockSuperUser:
    def has_perm(self, perm):
        return True


class AdminUserAdminTest(TestCase):
    """
    Tests the Admin user admin.
    """
    @classmethod
    def setUpTestData(cls):
        request_factory = RequestFactory()
        cls._request = request_factory.get('/admin')
        cls._request.user = MockSuperUser()

    def test_queryset_returns_with_admin_users_only(self):
        User.objects.create(username='admin', type=UserType.ADMIN)
        User.objects.create(username='voter', type=UserType.VOTER)

        admin = AdminUserAdmin(model=AdminUser, admin_site=AdminSite())
        query = admin.get_queryset(None)

        self.assertEqual(query.first().type, UserType.ADMIN)
        self.assertTrue(query.first().is_staff)
        self.assertTrue(query.first().is_superuser)
        self.assertEqual(query.count(), 1)

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


class VoterAdminTest(TestCase):
    """
    Tests the Voter admin.
    """
    @classmethod
    def setUpTestData(cls):
        request_factory = RequestFactory()
        cls._request = request_factory.get('/admin')
        cls._request.user = MockSuperUser()

    def test_queryset_returns_with_voters_only(self):
        User.objects.create(username='admin', type=UserType.ADMIN)
        User.objects.create(username='voter', type=UserType.VOTER)

        admin = VoterAdmin(model=Voter, admin_site=AdminSite())
        query = admin.get_queryset(None)

        self.assertEqual(query.first().type, UserType.VOTER)
        self.assertFalse(query.first().is_staff)
        self.assertFalse(query.first().is_superuser)
        self.assertEqual(query.count(), 1)

    def test_voter_admin_has_voter_profile_inline(self):
        admin = VoterAdmin(Voter, AdminSite())
        self.assertTrue(lambda: VoterProfileInline in admin.inlines)

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
