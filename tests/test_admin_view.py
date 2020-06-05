from abc import (
    ABC, abstractmethod
)
from distutils.dir_util import copy_tree
import json
import os
import shutil

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from core.models import (
    User, Batch, Section, Election, Candidate, CandidateParty,
    CandidatePosition, Vote, UserType
)
from core.views.admin.admin import (
    CandidatePartyAutoCompleteView, CandidatePositionAutoCompleteView
)
from core.utils import AppSettings


# Test views.
class BaseElectionSettingsViewTest(ABC):
    """
    This is the base class for the rest of the election settings view tests.
    """
    @classmethod
    def setUpTestData(cls):
        _election = Election.objects.create(name='Election')
        cls._batch = Batch.objects.create(year=2019, election=_election)
        cls._section = Section.objects.create(section_name='Section')

        user = User(
            username='admin',
            email='admin@admin.com',
            type=UserType.ADMIN
        )
        user.set_password('root')
        user.save()

        cls._view_url = ''

    def test_view_denies_anonymous_users(self):
        response = self.client.get(self._view_url, follow=True)
        self.assertRedirects(
            response,
            '/admin/login/?next=%2Fadmin%2Felection'
        )

        response = self.client.post(self._view_url, follow=True)
        self.assertRedirects(
            response,
            '/admin/login/?next=%2Fadmin%2Felection'
        )

    def test_view_denies_non_superusers(self):
        user = User(
            username='juan',
            email='juan@juan.com',
            type=UserType.VOTER
        )
        user.set_password('123')
        user.save()

        self.client.login(username='juan', password='123')

        response = self.client.get(self._view_url, follow=True)
        self.assertRedirects(
            response,
            '/admin/login/?next=%2Fadmin%2Felection'
        )

        response = self.client.post(self._view_url, follow=True)
        self.assertRedirects(
            response,
            '/admin/login/?next=%2Fadmin%2Felection'
        )

    @abstractmethod
    def test_view_accepts_superusers(self):
        pass


class ElectionSettingsViewTest(BaseElectionSettingsViewTest, TestCase):
    """
    Tests the election settings view in the admin.

    The election settings view can be accessed via `/admin/election/`.
    Anonymous and non-superuser users will be redirected to the admin index
    page.

    This view allows modifying the following settings:
        - Current Template
        - Open/Close State of the Elections
            - Note: When the elections are open, the results will give each
                    candidate names and have their avatars changed to the
                    default one, but with some colour changes. On the flip
                    side, when the elections are closed, the results will
                    show the candidates' actual names and avatars.
        - Creation/Modification of Public/Private Keys For Vote Encryption
            - Note: This setting will be disabled if there are vote set
                    already, or the elections are open.

    TODO: - Add a button for this view that will purge votes, essentially
            resetting the elections. However, candidates, parties, and
            positions will remain intact.
          - Create a TODO.md file where the TODO items will be found in.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        cls._view_url = '/admin/election'

    def test_view_accepts_superusers(self):
        self.client.login(username='admin', password='root')

        response = self.client.get(
            reverse('admin-election-index'),
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'default/admin/election.html'  # Default template is expected
                                           # since we did not set the template
                                           # in this test.
        )


# MBUI (Might Be Useful Info):
# (Jul. 23, 2019)
#     The classes below used to implement setUp(). The setUp() code logs in
#     an admin account in the test client. However, this is a bad idea since
#     the client will also log in with an admin account in tests that should
#     not have an admin logged in, including the tests in the base test class.


class ElectionSettingsCurrentTemplateViewTest(
        BaseElectionSettingsViewTest,
        TestCase):
    """
    Tests the election settings current template view.

    This view changes the current template being used. This will only accept
    POST requests. GET requests from superusers will result in a redirection
    to `/admin/election`, while non-superusers and anonymoous users to `/`.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls._view_url = reverse('admin-election-template')

    def test_view_accepts_superusers(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_properly_redirects_get_requests(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_with_invalid_post_requests(self):
        AppSettings().set('template', 'default')

        # Must return a success message to the view we'll be redirected to.
        self.client.login(username='admin', password='root')
        response = self.client.post(self._view_url, {}, follow=True)
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'Template field must not be empty nor have invalid data.'
        )
        self.assertEquals(AppSettings().get('template'), 'default')

    def test_view_with_valid_post_requests(self):
        AppSettings().set('template', 'default')

        # We have to create an actual my-little-pony template since I still do
        # not know how to mock a template in Django. Let's just copy the
        # default template and rename the copied folder as 'yes-or-yes'. This
        # will remove the need to create a unique template and make this test
        # simpler. We may do this since this test is just going to test whether
        # or not the correct template is being rendered by Botos. This test
        # does not require the creation of a *unique* template. Future
        # revisions of Botos may choose to redo this in favour of mocking
        # instead.
        template_dir = os.path.join(settings.BASE_DIR, 'botos/templates')
        default_template_dir = os.path.join(template_dir, 'default')
        new_template_dir = os.path.join(template_dir, 'my-little-pony')
        copy_tree(default_template_dir, new_template_dir)

        # Must return a success message to the view we'll be redirected to.
        self.client.login(username='admin', password='root')
        response = self.client.post(
            self._view_url,
            # 2019 Sean, seriously? My Little Pony? -2020 Sean
            { 'template_name': 'my-little-pony' },
            follow=True
        )
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'Current template changed successfully.'
        )
        self.assertEquals(AppSettings().get('template'), 'my-little-pony')

        # And, of course, we better clean up the mess we did and delete the
        # 'yes-or-yes' template we created.
        shutil.rmtree(new_template_dir)


class ElectionSettingsElectionsStateViewTest(
        BaseElectionSettingsViewTest,
        TestCase):
    """
    Tests the election settings election state view.

    This view changes the election state being used. An election state can
    either be open or closed. When the state is open, voters will be allowed to
    vote, and realtime results will show candidates with random names. This
    will only accept POST requests. GET requests from superusers will result in
    a redirection to `/admin/election`, while non-superusers and anonymoous
    users to `/`.

    This view must only accept a value that is either a True or False.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls._view_url = reverse('admin-election-state')

    def test_view_accepts_superusers(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_properly_redirects_get_requests(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_with_invalid_post_requests(self):
        AppSettings().set('election_state', 'open')

        # Must return a success message to the view we'll be redirected to.
        self.client.login(username='admin', password='root')
        response = self.client.post(self._view_url, {}, follow=True)
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'You attempted to change the election state with invalid data.'
        )
        self.assertEquals(AppSettings().get('election_state'), 'open')

    def test_view_with_valid_post_requests(self):
        AppSettings().set('election_state', 'open')

        # Must return a success message to the view we'll be redirected to.
        self.client.login(username='admin', password='root')
        response = self.client.post(
            self._view_url,
            { 'state': 'closed' },
            follow=True
        )
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'Election state changed successfully.'
        )
        self.assertEquals(AppSettings().get('election_state'), 'closed')


class CandidatePartyAutoCompleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.voter = User.objects.create(
            username='voter',
            type=UserType.VOTER
        )
        cls.voter.set_password('voter_password')
        cls.voter.save()

        cls.admin = User.objects.create(
            username='admin',
            type=UserType.ADMIN
        )
        cls.admin.set_password('admin(root)')
        cls.admin.save()

        cls.election = Election.objects.create(name='Election')
        cls.party = CandidateParty.objects.create(
            party_name='Awesome Party',
            election=cls.election
        )

        cls.other_election = Election.objects.create(name='Other Election')
        cls.other_party = CandidateParty.objects.create(
            party_name='Other Awesome Party',
            election=cls.other_election
        )

    def test_anonymous_users_get_an_empty_message(self):
        response = self.client.get(
            reverse('admin-candidate-party-autocomplete'),
            follow=True
        )

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            len(json_response['results']),
            0
        )

    def test_voters_get_an_empty_message(self):
        self.client.login(username='voter', password='voter_password')
        response = self.client.get(
            reverse('admin-candidate-party-autocomplete'),
            follow=True
        )

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            len(json_response['results']),
            0
        )

    def test_admin_election_is_none(self):
        self.client.login(username='admin', password='admin(root)')
        response = self.client.get(
            reverse('admin-candidate-party-autocomplete'),
            follow=True
        )

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            len(json_response['results']),
            0
        )

    def test_admin_election_is_not_none(self):
        self.client.login(username='admin', password='admin(root)')

        response = self.client.get(
            reverse('admin-candidate-party-autocomplete'),
            { 'forward': '{{ "election": "{}" }}'.format(self.election.id) },
            follow=True
        )
        results = json.loads(response.content.decode('utf-8'))['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'Awesome Party')
        self.assertEqual(int(results[0]['id']), self.party.id)

    def test_admin_election_with_query_substring(self):
        self.client.login(username='admin', password='admin(root)')

        response = self.client.get(
            reverse('admin-candidate-party-autocomplete'),
            {
                'forward': '{{ "election": "{}" }}'.format(self.election.id),
                'q': 'A'
            },
            follow=True
        )
        results = json.loads(response.content.decode('utf-8'))['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'Awesome Party')
        self.assertEqual(int(results[0]['id']), self.party.id)


class CandidatePositionAutoCompleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.voter = User.objects.create(
            username='voter',
            type=UserType.VOTER
        )
        cls.voter.set_password('voter_password')
        cls.voter.save()

        cls.admin = User.objects.create(
            username='admin',
            type=UserType.ADMIN
        )
        cls.admin.set_password('admin(root)')
        cls.admin.save()

        cls.election = Election.objects.create(name='Election')
        cls.position = CandidatePosition.objects.create(
            position_name='Awesome Position',
            position_level=0,
            election=cls.election
        )

        cls.other_election = Election.objects.create(name='Other Election')
        cls.other_position = CandidatePosition.objects.create(
            position_name='Other Awesome Position',
            position_level=0,
            election=cls.other_election
        )

    def test_anonymous_users_get_an_empty_message(self):
        response = self.client.get(
            reverse('admin-candidate-position-autocomplete'),
            follow=True
        )

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            len(json_response['results']),
            0
        )

    def test_voters_get_an_empty_message(self):
        self.client.login(username='voter', password='voter_password')
        response = self.client.get(
            reverse('admin-candidate-position-autocomplete'),
            follow=True
        )

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            len(json_response['results']),
            0
        )

    def test_admin_election_is_none(self):
        self.client.login(username='admin', password='admin(root)')
        response = self.client.get(
            reverse('admin-candidate-position-autocomplete'),
            follow=True
        )

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            len(json_response['results']),
            0
        )

    def test_admin_election_is_not_none(self):
        self.client.login(username='admin', password='admin(root)')

        response = self.client.get(
            reverse('admin-candidate-position-autocomplete'),
            { 'forward': '{{ "election": "{}" }}'.format(self.election.id) },
            follow=True
        )

        results = json.loads(response.content.decode('utf-8'))['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'Awesome Position')
        self.assertEqual(int(results[0]['id']), self.position.id)

    def test_admin_election_with_query_substring(self):
        self.client.login(username='admin', password='admin(root)')

        response = self.client.get(
            reverse('admin-candidate-position-autocomplete'),
            {
                'forward': '{{ "election": "{}" }}'.format(self.election.id),
                'q': 'A'
            },
            follow=True
        )
        results = json.loads(response.content.decode('utf-8'))['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'Awesome Position')
        self.assertEqual(int(results[0]['id']), self.position.id)
