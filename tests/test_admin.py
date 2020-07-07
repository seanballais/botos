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


class AdminLoginViewTest(TestCase):
    """
    Tests admin login view.
    """
    def test_admin_login_redirects_to_index(self):
        response = self.client.get(reverse('admin:login'), follow=True)
        self.assertRedirects(response, reverse('index'))

    def test_admin_login_with_next_redirects_to_index(self):
        response = self.client.get(
            reverse('admin:login'),
            {
                'next': reverse('results')
            },
            follow=True
        )
        self.assertRedirects(
            response,
            '{}?next={}'.format(reverse('index'), reverse('results'))
        )


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

    def test_queryset_returns_in_the_proper_order(self):
        election0 = Election.objects.create(name='Election 0')
        election1 = Election.objects.create(name='Election 1')
        
        batch0 = Batch.objects.create(year=0, election=election0)
        batch1 = Batch.objects.create(year=1, election=election1)

        section0 = Section.objects.create(section_name='Section 0')
        section1 = Section.objects.create(section_name='Section 1')

        User.objects.create(username='admin', type=UserType.ADMIN)
        
        voter0 = User.objects.create(
            username='voter0',
            first_name='A',
            last_name='A',
            type=UserType.VOTER
        )
        voter1 = User.objects.create(
            username='voter1',
            first_name='B',
            last_name='B',
            type=UserType.VOTER
        )
        voter2 = User.objects.create(
            username='voter2',
            first_name='B',
            last_name='B',
            type=UserType.VOTER
        )

        VoterProfile.objects.create(
            user=voter0,
            batch=batch0,
            section=section0
        )
        VoterProfile.objects.create(
            user=voter1,
            batch=batch0,
            section=section0
        )
        VoterProfile.objects.create(
            user=voter2,
            batch=batch1,
            section=section1
        )

        admin = VoterAdmin(model=Voter, admin_site=AdminSite())
        query = admin.get_queryset(None)

        self.assertEqual(query[0].type, UserType.VOTER)
        self.assertEqual(query[0].first_name, 'A')
        self.assertEqual(query[0].last_name, 'A')
        self.assertEqual(query[0].voter_profile.batch.year, 0)
        self.assertEqual(
            query[0].voter_profile.section.section_name,
            'Section 0'
        )

        self.assertEqual(query[1].type, UserType.VOTER)
        self.assertEqual(query[1].first_name, 'B')
        self.assertEqual(query[1].last_name, 'B')
        self.assertEqual(query[1].voter_profile.batch.year, 0)
        self.assertEqual(
            query[1].voter_profile.section.section_name,
            'Section 0'
        )

        self.assertEqual(query[2].type, UserType.VOTER)
        self.assertEqual(query[2].first_name, 'B')
        self.assertEqual(query[2].last_name, 'B')
        self.assertEqual(query[2].voter_profile.batch.year, 1)
        self.assertEqual(
            query[2].voter_profile.section.section_name,
            'Section 1'
        )

        self.assertEqual(query.count(), 3)

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

    def test_batch_function(self):
        election = Election.objects.create(name='Election')
        batch = Batch.objects.create(year=0, election=election)
        section = Section.objects.create(section_name='Section')
        user = User.objects.create(username='voter', type=UserType.VOTER)
        VoterProfile.objects.create(user=user, batch=batch, section=section)

        admin = VoterAdmin(model=Voter, admin_site=AdminSite())
        self.assertEqual(admin.batch(user), 0)

    def test_section_function(self):
        election = Election.objects.create(name='Election')
        batch = Batch.objects.create(year=0, election=election)
        section = Section.objects.create(section_name='Section')
        user = User.objects.create(username='voter', type=UserType.VOTER)
        VoterProfile.objects.create(user=user, batch=batch, section=section)

        admin = VoterAdmin(model=Voter, admin_site=AdminSite())
        self.assertEqual(admin.section(user), 'Section')

    def test_election_function(self):
        election = Election.objects.create(name='Election')
        batch = Batch.objects.create(year=0, election=election)
        section = Section.objects.create(section_name='Section')
        user = User.objects.create(username='voter', type=UserType.VOTER)
        VoterProfile.objects.create(user=user, batch=batch, section=section)

        admin = VoterAdmin(model=Voter, admin_site=AdminSite())
        self.assertEqual(admin.election(user), 'Election')


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
