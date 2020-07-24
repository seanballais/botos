# This test is partly based from:
#     https://www.argpar.se/posts/programming/testing-django-admin/
from urllib.parse import urljoin
import json

from bs4 import BeautifulSoup

from django import forms
from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.test import (
    RequestFactory, TestCase
)
from django.urls import reverse

from core.admin import (
    AdminUserAdmin, ElectionAdmin, VoterAdmin, VoterProfileInline, AdminUser,
    Voter, AdminCreationForm, VoterCreationForm, CandidateForm,
)
from core.models import (
    User, Batch, Section, VoterProfile, UserType, Candidate, CandidateParty,
    CandidatePosition, Election, Vote
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


class BatchAdminTest(TestCase):
    """
    Tests the Batch admin.
    """
    @classmethod
    def setUpTestData(cls):
        cls._election0 = Election.objects.create(name='Election 0')
        cls._election1 = Election.objects.create(name='Election 1')

        cls._batch0 = Batch.objects.create(year=0, election=cls._election0)
        _batch1 = Batch.objects.create(year=1, election=cls._election1)

        _section0 = Section.objects.create(section_name='Section 0')
        _section1 = Section.objects.create(section_name='Section 1')

        _voted_user0 = User.objects.create(
            username='pedro',
            type=UserType.VOTER
        )
        _voted_user0.set_password('pendoko')
        _voted_user0.save()
        _voted_user1 = User.objects.create(
            username='pedro1',
            type=UserType.VOTER
        )
        _voted_user1.set_password('pendoko1')
        _voted_user1.save()

        VoterProfile.objects.create(
            user=_voted_user0,
            has_voted=True,
            batch=cls._batch0,
            section=_section0
        )
        VoterProfile.objects.create(
            user=_voted_user1,
            has_voted=True,
            batch=_batch1,
            section=_section1
        )

        _party0 = CandidateParty.objects.create(
            party_name='Awesome Party 0',
            election=cls._election0
        )
        _party1 = CandidateParty.objects.create(
            party_name='Awesome Party 1',
            election=cls._election1
        )

        _position0 = CandidatePosition.objects.create(
            position_name='Amazing Position 0',
            position_level=0,
            max_num_selected_candidates=2,
            election=cls._election0
        )
        _position1 = CandidatePosition.objects.create(
            position_name='Amazing Position 1',
            position_level=1,
            max_num_selected_candidates=1,
            election=cls._election1
        )

        _candidate0 = Candidate.objects.create(
            user=_voted_user0,
            party=_party0,
            position=_position0,
            election=cls._election0
        )
        _candidate1 = Candidate.objects.create(
            user=_voted_user1,
            party=_party1,
            position=_position1,
            election=cls._election1
        )

        admin = User.objects.create(
            username='admin',
            type=UserType.ADMIN
        )
        admin.set_password('root')
        admin.save()

    def setUp(self):
        self.client.login(username='admin', password='root')

        # We have to refresh _batch0 since it gets modified in many tests.
        # Modifications to an object created inside setUpTestData() in a test
        # method will persist across test methods. Fortunately, the changes
        # are only present in memory. So, we can just refresh the original
        # content of the object from the database using refresh_from_db().
        # For more related information, you may visit this page:
        #   https://docs.djangoproject.com
        #          /en/2.2/topics/testing/tools/
        #          #django.test.TestCase.setUpTestData
        self._batch0.refresh_from_db()

    def test_change_view_denies_anonymous_users(self):
        self.client.logout()

        response = self.client.get(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_batch_change',
                    args=(self._batch0.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_change_view_denies_voters(self):
        self.client.login(username='pedro', password='pendoko')

        response = self.client.get(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_batch_change',
                    args=(self._batch0.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_change_view_post_denies_anonymous_users(self):
        self.client.logout()

        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_batch_change',
                    args=(self._batch0.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_change_view_post_denies_voters(self):
        self.client.login(username='pedro', password='pendoko')

        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_batch_change',
                    args=(self._batch0.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_change_view_shows_form(self):
        response = self.client.get(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            follow=True
        )

        self.assertTemplateUsed(response, 'admin/change_form.html')

    def test_change_view_voter_saves_no_election_change(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': self._batch0.election.id,
                '_save': 'Save'
            },
            follow=True
        )

        self._batch0.refresh_from_db()

        self.assertEqual(self._batch0.year, 10)
        self.assertEqual(self._batch0.election.id, self._election0.id)
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRedirects(response, reverse('admin:core_batch_changelist'))

    def test_change_view_voter_saves_continue_editing_no_election_change(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': self._batch0.election.id,
                '_continue': 'Save and continue editing'
            },
            follow=True
        )

        self._batch0.refresh_from_db()

        self.assertEqual(self._batch0.year, 10)
        self.assertEqual(self._batch0.election.id, self._election0.id)
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRedirects(
            response,
            reverse('admin:core_batch_change', args=( self._batch0.id, ))
        )
        self.assertTemplateUsed(response, 'admin/change_form.html')

    def test_change_view_voter_saves_add_another_no_election_change(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': self._batch0.election.id,
                '_addanother': 'Save and add another'
            },
            follow=True
        )

        self._batch0.refresh_from_db()

        self.assertEqual(self._batch0.year, 10)
        self.assertEqual(self._batch0.election.id, self._election0.id)
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRedirects(response, reverse('admin:core_batch_add'))
        self.assertTemplateUsed(response, 'admin/change_form.html')

    def test_change_view_voter_saves_election_change(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': self._election1.id,
                '_save': 'Save'
            },
            follow=True
        )

        self._batch0.refresh_from_db()

        self.assertEqual(self._batch0.year, 0)
        self.assertEqual(self._batch0.election.id, self._election0.id)
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertTemplateUsed(
            response,
            'default/admin/save_batch_confirmation.html'
        )
        self.assertEqual(response.context['batch'], self._batch0)
        self.assertEqual(response.context['election'], self._election1)
        self.assertEqual(response.context['save_type'], '_save')
        self.assertEqual(response.context['save_type_value'], 'Save')

    def test_change_view_voter_saves_continue_editing_election_change(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': self._election1.id,
                '_continue': 'Save and continue editing'
            },
            follow=True
        )

        self._batch0.refresh_from_db()

        self.assertEqual(self._batch0.year, 0)
        self.assertEqual(self._batch0.election.id, self._election0.id)
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertTemplateUsed(
            response,
            'default/admin/save_batch_confirmation.html'
        )
        self.assertEqual(response.context['batch'], self._batch0)
        self.assertEqual(response.context['election'], self._election1)
        self.assertEqual(response.context['save_type'], '_continue')
        self.assertEqual(
            response.context['save_type_value'],
            'Save and continue editing'
        )

    def test_change_view_voter_saves_add_another_election_change(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': self._election1.id,
                '_addanother': 'Save and add another'
            },
            follow=True
        )

        self._batch0.refresh_from_db()

        self.assertEqual(self._batch0.year, 0)
        self.assertEqual(self._batch0.election.id, self._election0.id)
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertTemplateUsed(
            response,
            'default/admin/save_batch_confirmation.html'
        )
        self.assertEqual(response.context['batch'], self._batch0)
        self.assertEqual(response.context['election'], self._election1)
        self.assertEqual(response.context['save_type'], '_addanother')
        self.assertEqual(
            response.context['save_type_value'],
            'Save and add another'
        )

    def test_change_view_confirmed_saves_election_change(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': self._election1.id,
                '_save': 'Save',
                'save_confirmed': 'yes'
            },
            follow=True
        )

        self._batch0.refresh_from_db()

        self.assertEqual(self._batch0.year, 10)
        self.assertEqual(self._batch0.election.id, self._election1.id)
        self.assertEqual(Candidate.objects.all().count(), 1)
        self.assertRedirects(response, reverse('admin:core_batch_changelist'))

    def test_change_view_confirmed_saves_continue_edit_election_change(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': self._election1.id,
                '_continue': 'Save and continue editing',
                'save_confirmed': 'yes'
            },
            follow=True
        )

        self._batch0.refresh_from_db()

        self.assertEqual(self._batch0.year, 10)
        self.assertEqual(self._batch0.election.id, self._election1.id)
        self.assertEqual(Candidate.objects.all().count(), 1)
        self.assertRedirects(
            response,
            reverse('admin:core_batch_change', args=( self._batch0.id, ))
        )
        self.assertTemplateUsed(response, 'admin/change_form.html')

    def test_change_view_confirmed_saves_add_another_election_change(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': self._election1.id,
                '_addanother': 'Save and add another',
                'save_confirmed': 'yes'
            },
            follow=True
        )

        self._batch0.refresh_from_db()

        self.assertEqual(self._batch0.year, 10)
        self.assertEqual(self._batch0.election.id, self._election1.id)
        self.assertEqual(Candidate.objects.all().count(), 1)
        self.assertRedirects(response, reverse('admin:core_batch_add'))

    def test_change_view_post_non_existent_batch(self):
        response = self.client.post(
            reverse(
                'admin:core_batch_change',
                args=( 123456789, )  # Some non-existent batch.
            ),
            {
                'year': 10,
                'election': self._election1.id,
                '_save': 'Save'
            },
            follow=True
        )

        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRedirects(response, reverse('admin:core_batch_changelist'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Attempted to modify a non-existent batch.'
        )

    def test_change_view_post_non_existent_election(self):
        response = self.client.post(
            reverse('admin:core_batch_change', args=( self._batch0.id, )),
            {
                'year': self._batch0.year + 10,
                'election': 123456789,  # Some non-existent election.
                '_save': 'Save'
            },
            follow=True
        )

        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRedirects(
            response,
            reverse('admin:core_batch_change', args=( self._batch0.id, ))
        )

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Attempted to use a non-existent election.'
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


class VoterAdminChangeBatchTest(TestCase):
    """
    Tests changing the batch of a voter. This test is separated from the
    voter admin test for cleanliness reasons.
    """
    @classmethod
    def setUpTestData(cls):
        cls._election0 = Election.objects.create(name='Election 0')
        cls._election1 = Election.objects.create(name='Election 1')

        cls._batch0 = Batch.objects.create(year=0, election=cls._election0)
        cls._batch1 = Batch.objects.create(year=1, election=cls._election0)
        cls._batch2 = Batch.objects.create(year=2, election=cls._election1)

        cls._section0 = Section.objects.create(section_name='Section 0')
        cls._section1 = Section.objects.create(section_name='Section 1')
        cls._section2 = Section.objects.create(section_name='Section 2')
        cls._section3 = Section.objects.create(section_name='Section 3')
        cls._section4 = Section.objects.create(section_name='Section 4')
        cls._section5 = Section.objects.create(section_name='Section 5')

        cls._user0 = User.objects.create(
            username='pedro',
            type=UserType.VOTER
        )
        cls._user0.set_password('pendoko')
        cls._user0.save()

        cls._user1 = User.objects.create(
            username='pedro1',
            type=UserType.VOTER
        )
        cls._user1.set_password('pendoko1')
        cls._user1.save()

        cls._user2 = User.objects.create(
            username='pedro2',
            type=UserType.VOTER
        )
        cls._user2.set_password('pendoko2')
        cls._user2.save()

        cls._user3 = User.objects.create(
            username='pedro3',
            type=UserType.VOTER
        )
        cls._user3.set_password('pendoko3')
        cls._user3.save()

        cls._user4 = User.objects.create(
            username='pedro4',
            type=UserType.VOTER
        )
        cls._user4.set_password('pendoko4')
        cls._user4.save()

        cls._voter_profile0 = VoterProfile.objects.create(
            user=cls._user0,
            has_voted=True,
            batch=cls._batch0,
            section=cls._section0
        )
        VoterProfile.objects.create(
            user=cls._user1,
            has_voted=True,
            batch=cls._batch1,
            section=cls._section1
        )
        VoterProfile.objects.create(
            user=cls._user2,
            has_voted=True,
            batch=cls._batch2,
            section=cls._section2
        )
        VoterProfile.objects.create(
            user=cls._user3,
            has_voted=True,
            batch=cls._batch0,
            section=cls._section3
        )
        VoterProfile.objects.create(
            user=cls._user4,
            has_voted=True,
            batch=cls._batch2,
            section=cls._section5
        )

        _party0 = CandidateParty.objects.create(
            party_name='Awesome Party 0',
            election=cls._election0
        )
        _party1 = CandidateParty.objects.create(
            party_name='Awesome Party 1',
            election=cls._election1
        )

        _position0 = CandidatePosition.objects.create(
            position_name='Amazing Position 0',
            position_level=0,
            max_num_selected_candidates=2,
            election=cls._election0
        )
        _position1 = CandidatePosition.objects.create(
            position_name='Amazing Position 1',
            position_level=1,
            max_num_selected_candidates=1,
            election=cls._election1
        )

        _candidate0 = Candidate.objects.create(
            user=cls._user0,
            party=_party0,
            position=_position0,
            election=cls._election0
        )
        _candidate1 = Candidate.objects.create(
            user=cls._user1,
            party=_party0,
            position=_position0,
            election=cls._election0
        )
        _candidate2 = Candidate.objects.create(
            user=cls._user2,
            party=_party1,
            position=_position1,
            election=cls._election1
        )

        admin = User.objects.create(
            username='admin',
            type=UserType.ADMIN
        )
        admin.set_password('root')
        admin.save()

    def setUp(self):
        self.client.login(username='admin', password='root')

        self._user0.refresh_from_db()

        self.post_data = {
            'username': self._user0.username,
            'first_name': self._user0.first_name,
            'last_name': self._user0.last_name,
            'email': self._user0.email,
            'voter_profile-0-user': self._user0.voter_profile.user_id,
            'voter_profile-0-batch': self._user0.voter_profile.batch_id,
            'voter_profile-0-section': self._user0.voter_profile.section_id,
            'voter_profile-0-id': self._user0.voter_profile.id,
            'voter_profile-INITIAL_FORMS': '1',
            'voter_profile-MAX_NUM_FORMS': '1',
            'voter_profile-TOTAL_FORMS': '1',
            'voter_profile-MIN_NUM_FORMS': '0',
            'voter_profile-__prefix__-id': '',
            'voter_profile-__prefix__-user': self._user0.voter_profile.user_id,
            'voter_profile-__prefix__-batch': '',
            'voter_profile-__prefix__-section': '',
            # We're adding a CSRF token here, because the change form view
            # originally includes a CSRF token when performing form actions,
            # and the confirmation page then removes the included CSRF token.
            # So, we're including a fake token to reflect the actual behaviour
            # when a admin changes the batch of a voter to one that is under a
            # different election in the admin.
            'csrfmiddlewaretoken': 'random_token'
        }

    def test_change_view_denies_anonymous_users(self):
        self.client.logout()

        response = self.client.get(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_voter_change',
                    args=(self._user0.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_change_view_denies_voters(self):
        self.client.login(username='pedro', password='pendoko')

        response = self.client.get(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_voter_change',
                    args=(self._user0.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_change_view_post_denies_anonymous_users(self):
        self.client.logout()

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_voter_change',
                    args=(self._user0.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_change_view_post_denies_voters(self):
        self.client.login(username='pedro', password='pendoko')

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_voter_change',
                    args=(self._user0.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_change_view_shows_form(self):
        response = self.client.get(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            follow=True
        )

        self.assertTemplateUsed(response, 'admin/change_form.html')

    def test_change_view_voter_saves_no_batch_change(self):
        self.post_data['_save'] = 'Save'

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_changelist'))

    def test_change_view_voter_saves_continue_editing_no_batch_change(self):
        self.post_data['_continue'] = 'Save and continue editing'

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )

    def test_change_view_voter_saves_add_another_no_batch_change(self):
        self.post_data['_addanother'] = 'Save and add another'

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_add'))

    def test_change_view_voter_saves_batch_change(self):
        # This will save changes as usual. So, no need to check for the
        # presence of '_save' in 'post_data' of the response context.
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-batch'] = self._batch1.id
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 1)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_changelist'))

    def test_change_view_voter_saves_continue_editing_batch_change(self):
        # This will save changes as usual. So, no need to check for the
        # presence of '_continue' in 'post_data' of the response context.
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-batch'] = self._batch1.id
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 1)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )

    def test_change_view_voter_saves_add_another_batch_change(self):
        # This will save changes as usual. So, no need to check for the
        # presence of '_addanother' in 'post_data' of the response context.
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-batch'] = self._batch1.id
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 1)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_add'))

    def test_change_view_voter_saves_batch_change_elec(self):
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertTrue('_continue' in response.context['post_data'])
        self.assertIsNotNone(self._user0.candidate)
        self.assertTemplateUsed(
            response,
            'default/admin/save_voter_confirmation.html'
        )

    def test_change_view_voter_saves_continue_editing_batch_change_elec(self):
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertTrue('_continue' in response.context['post_data'])
        self.assertIsNotNone(self._user0.candidate)
        self.assertTemplateUsed(
            response,
            'default/admin/save_voter_confirmation.html'
        )

    def test_change_view_voter_saves_add_another_batch_change_elec(self):
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertTrue('_addanother' in response.context['post_data'])
        self.assertIsNotNone(self._user0.candidate)
        self.assertTemplateUsed(
            response,
            'default/admin/save_voter_confirmation.html'
        )

    def test_change_view_confirmed_saves_batch_change_elec(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 2)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election1.id
        )
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRaises(
            User.candidate.RelatedObjectDoesNotExist,
            lambda: self._user0.candidate
        )
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_changelist'))

    def test_change_view_confirmed_saves_continue_edit_batch_change_elec(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 2)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election1.id
        )
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRaises(
            User.candidate.RelatedObjectDoesNotExist,
            lambda: self._user0.candidate
        )
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        self.assertTemplateUsed(response, 'admin/change_form.html')     

    def test_change_view_confirmed_saves_add_another_batch_change_elec(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 2)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election1.id
        )
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRaises(
            User.candidate.RelatedObjectDoesNotExist,
            lambda: self._user0.candidate
        )
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_add'))

    def test_change_view_post_non_existent_voter(self):
        self.post_data['_save'] = 'Save'
        
        response = self.client.post(
            reverse(
                'admin:core_voter_change',
                args=( 123456789, )  # Some non-existent voter.
            ),
            self.post_data,
            follow=True
        )

        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertRedirects(response, reverse('admin:core_voter_changelist'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Attempted to modify a non-existent voter.'
        )

    def test_change_view_post_non_existent_batch(self):
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-batch'] = 123456789 # Some non-existent
                                                            # batch.
        
        response = self.client.post(
            reverse(
                'admin:core_voter_change',
                args=( self._user0.id, )
            ),
            self.post_data,
            follow=True
        )

        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, )))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Attempted to use a non-existent batch.'
        )

    def test_change_view_post_batch_no_section_change(self):
        # The save action type is not specified since we expect that an error
        # will be raised regardless of save action type. It will cause an error
        # because no two batches can have the same section.
        self.post_data['voter_profile-0-batch'] = self._batch2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_view_post_confirmed_save_batch_no_section_change(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-batch'] = self._batch2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_view_post_confirmed_continue_batch_no_section_change(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-batch'] = self._batch2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_view_post_confirmed_add_new_batch_no_section_change(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-batch'] = self._batch2.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_post_save_batch_section_to_allowed_section_chg_t0(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section5.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 2)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election1.id
        )
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRaises(
            User.candidate.RelatedObjectDoesNotExist,
            lambda: self._user0.candidate
        )
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_changelist'))

    def test_change_post_save_batch_section_to_allowed_section_chg_t1(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section4.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 2)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election1.id
        )
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRaises(
            User.candidate.RelatedObjectDoesNotExist,
            lambda: self._user0.candidate
        )
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_changelist'))

    def test_change_post_cont_batch_section_to_allowed_section_chg_t0(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section5.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 2)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election1.id
        )
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRaises(
            User.candidate.RelatedObjectDoesNotExist,
            lambda: self._user0.candidate
        )
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )

    def test_change_post_cont_batch_section_to_allowed_section_chg_t1(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section4.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 2)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election1.id
        )
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRaises(
            User.candidate.RelatedObjectDoesNotExist,
            lambda: self._user0.candidate
        )
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )

    def test_change_post_add_batch_section_to_allowed_section_chg_t0(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section5.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 2)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election1.id
        )
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRaises(
            User.candidate.RelatedObjectDoesNotExist,
            lambda: self._user0.candidate
        )
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_add'))

    def test_change_post_add_batch_section_to_allowed_section_chg_t1(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section4.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 2)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election1.id
        )
        self.assertEqual(Candidate.objects.all().count(), 2)
        self.assertRaises(
            User.candidate.RelatedObjectDoesNotExist,
            lambda: self._user0.candidate
        )
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_add'))

    def test_change_view_post_batch_section_to_disallowed_section_change(self):
        # The save action type is not specified since we expect that an error
        # will be raised regardless of save action type. It will cause an error
        # because no two batches can have the same section.
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_post_confirmed_save_batch_section_dis_section_change(self):
        # The save action type is not specified since we expect that an error
        # will be raised regardless of save action type. It will cause an error
        # because no two batches can have the same section.
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_post_confirmed_cont_batch_section_dis_section_change(self):
        # The save action type is not specified since we expect that an error
        # will be raised regardless of save action type. It will cause an error
        # because no two batches can have the same section.
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_post_confirmed_add_batch_section_dis_section_change(self):
        # The save action type is not specified since we expect that an error
        # will be raised regardless of save action type. It will cause an error
        # because no two batches can have the same section.
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-batch'] = self._batch2.id
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_post_save_no_batch_section_allowed_section_chg_t0(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-section'] = self._section3.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_changelist'))

    def test_change_post_save_no_batch_section_allowed_section_chg_t1(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-section'] = self._section4.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_changelist'))

    def test_change_post_cont_no_batch_section_allowed_section_chg_t0(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-section'] = self._section3.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )

    def test_change_post_cont_no_batch_section_allowed_section_chg_t1(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-section'] = self._section4.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )

    def test_change_post_add_no_batch_section_allowed_section_chg_t0(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-section'] = self._section3.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_add'))

    def test_change_post_add_no_batch_section_allowed_section_chg_t1(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-section'] = self._section4.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(response, reverse('admin:core_voter_add'))

    def test_change_view_post_no_batch_section_disallowed_section_change(self):
        # The save action type is not specified since we expect that an error
        # will be raised regardless of save action type. It will cause an error
        # because no two batches can have the same section.
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_post_confirmed_save_no_batch_section_dis_section_chg(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_save'] = 'Save'
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_post_confirmed_cont_no_batch_section_dis_section_chg(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_continue'] = 'Save and continue editing'
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )

    def test_change_post_confirmed_add_no_batch_section_dis_section_chg(self):
        self.post_data['save_confirmed'] = 'yes'
        self.post_data['_addanother'] = 'Save and add another'
        self.post_data['voter_profile-0-section'] = self._section1.id

        response = self.client.post(
            reverse('admin:core_voter_change', args=( self._user0.id, )),
            self.post_data,
            follow=True
        )

        self._user0.refresh_from_db()

        self.assertEqual(self._user0.voter_profile.batch.year, 0)
        self.assertEqual(
            self._user0.voter_profile.batch.election.id,
            self._election0.id
        )
        self.assertEqual(Candidate.objects.all().count(), 3)
        self.assertIsNotNone(self._user0.candidate)
        self.assertIsNotNone(self._user1.candidate)
        self.assertIsNotNone(self._user2.candidate)
        self.assertRedirects(
            response,
            reverse('admin:core_voter_change', args=( self._user0.id, ))
        )
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
        )


class ElectionAdminTest(TestCase):
    """
    Tests the election admin.
    """
    @classmethod
    def setUpTestData(cls):
        request_factory = RequestFactory()
        cls._request = request_factory.get('/admin')
        cls._request.user = MockSuperUser()

        _admin = User.objects.create(
            username='admin',
            type=UserType.ADMIN
        )
        _admin.set_password('root')
        _admin.save()

    def setUp(self):
        self.client.login(username='admin', password='root')

    def test_clear_election_action(self):
        _election0 = Election.objects.create(name='Election 0')

        _batch0 = Batch.objects.create(year=0, election=_election0)
        _section0 = Section.objects.create(section_name='Section 0')

        _voted_user0 = User.objects.create(
            username='pedro',
            type=UserType.VOTER
        )
        _voted_user0.set_password('pendoko')
        _voted_user0.save()

        VoterProfile.objects.create(
            user=_voted_user0,
            has_voted=True,
            batch=_batch0,
            section=_section0
        )

        _party0 = CandidateParty.objects.create(
            party_name='Awesome Party 0',
            election=_election0
        )
        _position0 = CandidatePosition.objects.create(
            position_name='Amazing Position 0',
            position_level=0,
            max_num_selected_candidates=2,
            election=_election0
        )
        _candidate0 = Candidate.objects.create(
            user=_voted_user0,
            party=_party0,
            position=_position0,
            election=_election0
        )

        Vote.objects.create(
            user=_voted_user0,
            candidate=_candidate0,
            election=_election0
        )

        _election1 = Election.objects.create(name='Election 1')

        _batch1 = Batch.objects.create(year=1, election=_election1)
        _section1 = Section.objects.create(section_name='Section 1')

        _voted_user1 = User.objects.create(
            username='pedro1',
            type=UserType.VOTER
        )
        _voted_user1.set_password('pendoko1')
        _voted_user1.save()

        VoterProfile.objects.create(
            user=_voted_user1,
            has_voted=True,
            batch=_batch1,
            section=_section1
        )

        _party1 = CandidateParty.objects.create(
            party_name='Awesome Party 1',
            election=_election1
        )
        _position1 = CandidatePosition.objects.create(
            position_name='Amazing Position 1',
            position_level=1,
            max_num_selected_candidates=1,
            election=_election1
        )
        _candidate1 = Candidate.objects.create(
            user=_voted_user1,
            party=_party1,
            position=_position1,
            election=_election1
        )

        Vote.objects.create(
            user=_voted_user1,
            candidate=_candidate1,
            election=_election1
        )

        self.assertEqual(Vote.objects.all().count(), 2)

        queryset = Election.objects.filter(name='Election 0')
        response = self.client.post(
            reverse('admin:core_election_changelist'),
            {
                'action': 'clear_election',
                ACTION_CHECKBOX_NAME: [ e.pk for e in queryset ]
            },
            follow=True
        )
        template_name = 'default/admin/clear_election_action.html'
        self.assertTemplateUsed(response, template_name)

        response = self.client.post(
            reverse('admin:core_election_changelist'),
            {
                'action': 'clear_election',
                'clear_elections': 'yes',
                ACTION_CHECKBOX_NAME: [ e.pk for e in queryset ]
            },
            follow=True
        )

        _voted_user0.refresh_from_db()
        _voted_user1.refresh_from_db()

        messages = list(response.context['messages'])

        self.assertEqual(Vote.objects.all().count(), 1)
        self.assertFalse(_voted_user0.voter_profile.has_voted)
        self.assertTrue(_voted_user1.voter_profile.has_voted)
        self.assertEqual(
            str(messages[0]),
            'Votes in 1 election were cleared successfully.'
        )

    def test_clear_election_action_multiple_elections(self):
        _election0 = Election.objects.create(name='Election 0')

        _batch0 = Batch.objects.create(year=0, election=_election0)
        _section0 = Section.objects.create(section_name='Section 0')

        _voted_user0 = User.objects.create(
            username='pedro',
            type=UserType.VOTER
        )
        _voted_user0.set_password('pendoko')
        _voted_user0.save()

        VoterProfile.objects.create(
            user=_voted_user0,
            has_voted=True,
            batch=_batch0,
            section=_section0
        )

        _party0 = CandidateParty.objects.create(
            party_name='Awesome Party 0',
            election=_election0
        )
        _position0 = CandidatePosition.objects.create(
            position_name='Amazing Position 0',
            position_level=0,
            max_num_selected_candidates=2,
            election=_election0
        )
        _candidate0 = Candidate.objects.create(
            user=_voted_user0,
            party=_party0,
            position=_position0,
            election=_election0
        )

        Vote.objects.create(
            user=_voted_user0,
            candidate=_candidate0,
            election=_election0
        )

        _election1 = Election.objects.create(name='Election 1')

        _batch1 = Batch.objects.create(year=1, election=_election1)
        _section1 = Section.objects.create(section_name='Section 1')

        _voted_user1 = User.objects.create(
            username='pedro1',
            type=UserType.VOTER
        )
        _voted_user1.set_password('pendoko1')
        _voted_user1.save()

        VoterProfile.objects.create(
            user=_voted_user1,
            has_voted=True,
            batch=_batch1,
            section=_section1
        )

        _party1 = CandidateParty.objects.create(
            party_name='Awesome Party 1',
            election=_election1
        )
        _position1 = CandidatePosition.objects.create(
            position_name='Amazing Position 1',
            position_level=1,
            max_num_selected_candidates=1,
            election=_election1
        )
        _candidate1 = Candidate.objects.create(
            user=_voted_user1,
            party=_party1,
            position=_position1,
            election=_election1
        )

        Vote.objects.create(
            user=_voted_user1,
            candidate=_candidate1,
            election=_election1
        )

        queryset = Election.objects.all()
        response = self.client.post(
            reverse('admin:core_election_changelist'),
            {
                'action': 'clear_election',
                ACTION_CHECKBOX_NAME: [ e.pk for e in queryset ]
            },
            follow=True
        )
        template_name = 'default/admin/clear_election_action.html'
        self.assertTemplateUsed(response, template_name)

        response = self.client.post(
            reverse('admin:core_election_changelist'),
            {
                'action': 'clear_election',
                'clear_elections': 'yes',
                ACTION_CHECKBOX_NAME: [ e.pk for e in queryset ]
            },
            follow=True
        )

        _voted_user0.refresh_from_db()
        _voted_user1.refresh_from_db()

        messages = list(response.context['messages'])

        self.assertEqual(Vote.objects.all().count(), 0)
        self.assertFalse(_voted_user0.voter_profile.has_voted)
        self.assertFalse(_voted_user1.voter_profile.has_voted)
        self.assertEqual(
            str(messages[0]),
            'Votes in 2 elections were cleared successfully.'
        )

    def test_election_clear_election_confirmation_view_rejects_anonymous(self):
        self.client.logout()

        _election = Election.objects.create(name='Election 0')

        response = self.client.get(
            reverse('admin:core_election_clear_votes', args=(_election.id,)),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_election_clear_votes',
                    args=(_election.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_election_clear_election_confirmation_view_rejects_voters(self):
        _election = Election.objects.create(name='Election 0')

        _batch0 = Batch.objects.create(year=0, election=_election)
        _section0 = Section.objects.create(section_name='Section 0')

        _voted_user0 = User.objects.create(
            username='pedro',
            type=UserType.VOTER
        )
        _voted_user0.set_password('pendoko')
        _voted_user0.save()

        VoterProfile.objects.create(
            user=_voted_user0,
            has_voted=True,
            batch=_batch0,
            section=_section0
        )

        self.client.login(username='pedro', password='pendoko')
        response = self.client.get(
            reverse('admin:core_election_clear_votes', args=(_election.id,)),
            follow=True
        )
        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_election_clear_votes',
                    args=(_election.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)    

    def test_election_clear_election_confirmation_view_get_template(self):
        _election = Election.objects.create(name='Election 0')

        response = self.client.get(
            reverse('admin:core_election_clear_votes', args=(_election.id,)),
            follow=True
        )

        template_name = 'default/admin/clear_election_action_confirmation.html'
        self.assertTemplateUsed(response, template_name)
        self.assertEqual(response.context['election'], _election)

    def test_election_clear_election_confirmation_view_get_invalid_id(self):
        response = self.client.get(
            reverse('admin:core_election_clear_votes', args=(1000,)),
            follow=True
        )

        messages = list(response.context['messages'])
        self.assertEqual(
            str(messages[0]),
            'Attempted to clear votes in a non-existent election.'
        )
        self.assertRedirects(
            response,
            reverse('admin:core_election_changelist')
        )

    def test_election_clear_election_confirmation_post_rejects_anonymous(self):
        self.client.logout()

        _election = Election.objects.create(name='Election 0')

        response = self.client.post(
            reverse('admin:core_election_clear_votes', args=(_election.id,)),
            follow=True
        )

        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_election_clear_votes',
                    args=(_election.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)

    def test_election_clear_election_confirmation_post_rejects_voters(self):
        _election = Election.objects.create(name='Election 0')

        _batch0 = Batch.objects.create(year=0, election=_election)
        _section0 = Section.objects.create(section_name='Section 0')

        _voted_user0 = User.objects.create(
            username='pedro',
            type=UserType.VOTER
        )
        _voted_user0.set_password('pendoko')
        _voted_user0.save()

        VoterProfile.objects.create(
            user=_voted_user0,
            has_voted=True,
            batch=_batch0,
            section=_section0
        )

        self.client.login(username='pedro', password='pendoko')
        response = self.client.get(
            reverse('admin:core_election_clear_votes', args=(_election.id,)),
            follow=True
        )
        index_url = urljoin(
            reverse('index'),
            '?next={}'.format(
                reverse(
                    'admin:core_election_clear_votes',
                    args=(_election.id,)
                )
            )
        )
        self.assertRedirects(response, index_url)      

    def test_election_clear_election_confirmation_view_post_valid_id(self):
        _election0 = Election.objects.create(name='Election 0')

        _batch0 = Batch.objects.create(year=0, election=_election0)
        _section0 = Section.objects.create(section_name='Section 0')

        _voted_user0 = User.objects.create(
            username='pedro',
            type=UserType.VOTER
        )
        _voted_user0.set_password('pendoko')
        _voted_user0.save()

        VoterProfile.objects.create(
            user=_voted_user0,
            has_voted=True,
            batch=_batch0,
            section=_section0
        )

        _party0 = CandidateParty.objects.create(
            party_name='Awesome Party 0',
            election=_election0
        )
        _position0 = CandidatePosition.objects.create(
            position_name='Amazing Position 0',
            position_level=0,
            max_num_selected_candidates=2,
            election=_election0
        )
        _candidate0 = Candidate.objects.create(
            user=_voted_user0,
            party=_party0,
            position=_position0,
            election=_election0
        )

        Vote.objects.create(
            user=_voted_user0,
            candidate=_candidate0,
            election=_election0
        )

        _election1 = Election.objects.create(name='Election 1')

        _batch1 = Batch.objects.create(year=1, election=_election1)
        _section1 = Section.objects.create(section_name='Section 1')

        _voted_user1 = User.objects.create(
            username='pedro1',
            type=UserType.VOTER
        )
        _voted_user1.set_password('pendoko1')
        _voted_user1.save()

        VoterProfile.objects.create(
            user=_voted_user1,
            has_voted=True,
            batch=_batch1,
            section=_section1
        )

        _party1 = CandidateParty.objects.create(
            party_name='Awesome Party 1',
            election=_election1
        )
        _position1 = CandidatePosition.objects.create(
            position_name='Amazing Position 1',
            position_level=1,
            max_num_selected_candidates=1,
            election=_election1
        )
        _candidate1 = Candidate.objects.create(
            user=_voted_user1,
            party=_party1,
            position=_position1,
            election=_election1
        )

        Vote.objects.create(
            user=_voted_user1,
            candidate=_candidate1,
            election=_election1
        )

        response = self.client.post(
            reverse('admin:core_election_clear_votes', args=(_election0.id,)),
            { 'clear_election': 'yes' },
            follow=True
        )

        _voted_user0.refresh_from_db()
        _voted_user1.refresh_from_db()

        self.assertEqual(Vote.objects.all().count(), 1)
        self.assertFalse(_voted_user0.voter_profile.has_voted)
        self.assertTrue(_voted_user1.voter_profile.has_voted)

        messages = list(response.context['messages'])
        self.assertEqual(
            str(messages[0]),
            'Votes in \'Election 0\' were cleared successfully.'
        )

        change_url = reverse(
            'admin:core_election_change',
            args=(_election0.id,)
        )
        self.assertRedirects(response, change_url)

    def test_election_clear_election_confirmation_view_post_invalid_id(self):
        response = self.client.post(
            reverse('admin:core_election_clear_votes', args=(10000000,)),
            { 'clear_election': 'yes' },
            follow=True
        )

        messages = list(response.context['messages'])
        self.assertEqual(
            str(messages[0]),
            'Attempted to clear votes in a non-existent election.'
        )
        self.assertRedirects(
            response,
            reverse('admin:core_election_changelist')
        )

    def test_election_clear_election_confirmation_view_post_no_yes(self):
        _election0 = Election.objects.create(name='Election 0')

        response = self.client.post(
            reverse('admin:core_election_clear_votes', args=(_election0.id,)),
            follow=True
        )

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 0)
        change_url = reverse(
            'admin:core_election_change',
            args=(_election0.id,)
        )
        self.assertRedirects(response, change_url)

    def test_election_admin_render_change_form_update(self):
        admin = ElectionAdmin(model=Election, admin_site=AdminSite())

        _election0 = Election.objects.create(name='Election 0')

        class ElectionForm(forms.ModelForm):
            class Meta:
                model = Election
                fields = ( '__all__' )

        class MockElectionForm():
            form = ElectionForm(initial={ 'name': 'Election 0' })

        mock_form = MockElectionForm()

        response = admin.render_change_form(
            request=self._request,
            context={
                'inline_admin_formsets': [],
                'adminform': mock_form
            },
            add=False,
            change=True,
            obj=_election0
        )
        self.assertTrue(response.context_data['show_save'])
        self.assertTrue(response.context_data['show_delete_link'])
        self.assertTrue(response.context_data['show_clear_election'])
        self.assertTrue(response.context_data['show_save_and_add_another'])
        self.assertTrue(response.context_data['show_save_and_continue'])
        self.assertEqual(response.context_data['election'], _election0)

    def test_election_admin_render_change_form_add(self):
        admin = ElectionAdmin(model=Election, admin_site=AdminSite())

        _election0 = Election.objects.create(name='Election 0')

        class ElectionForm(forms.ModelForm):
            class Meta:
                model = Election
                fields = ( '__all__' )

        class MockElectionForm():
            form = ElectionForm(initial={ 'name': 'Election 0' })

        mock_form = MockElectionForm()

        response = admin.render_change_form(
            request=self._request,
            context={
                'inline_admin_formsets': [],
                'adminform': mock_form,
            },
            add=True,
            change=False
        )
        self.assertTrue(response.context_data['show_save'])
        self.assertTrue(response.context_data['show_delete_link'])
        self.assertTrue(response.context_data['show_save_and_add_another'])
        self.assertTrue(response.context_data['show_save_and_continue'])
        self.assertFalse(response.context_data['show_clear_election'])
        self.assertIsNone(response.context_data['election'])


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
