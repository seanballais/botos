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

    def test_election_admin_render_change_form(self):
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
            obj=_election0
        )
        self.assertTrue(response.context_data['show_save'])
        self.assertTrue(response.context_data['show_delete_link'])
        self.assertTrue(response.context_data['show_clear_election'])
        self.assertTrue(response.context_data['show_save_and_add_another'])
        self.assertTrue(response.context_data['show_save_and_continue'])
        self.assertEqual(response.context_data['election'], _election0)


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
