from bs4 import BeautifulSoup

from django.test import TestCase
from django.urls import reverse

from core.models import (
    User, Batch, Section, Candidate, CandidateParty, CandidatePosition, Vote
)
from core.utils import AppSettings


class LoginSubviewTest(TestCase):
    """
    Tests the login sub-view in the index view (accessed via `/`).

    This subview will only appear to anonymous users. Logged-in users will be
    shown either the voting subview or the voted subview.

    It should be noted that user authentication will be handled by
    `django.contrib.auth`. Thus, no tests will be needed for the authentication
    implementation.

    TODO: Make more integration tests to make sure that the login form does
          log in the user, if the correct credentials are given, and returns an
          error message if otherwise.
    """
    def test_anonymous_users_login_subview(self):
        response = self.client.get('/')
        self.assertIsNotNone(self._get_login_form(str(response.content)))

    def test_login_subview_form_has_correct_action_URL(self):
        response = self.client.get('/')
        form = self._get_login_form(str(response.content))
        self.assertEquals(form.get('action'), reverse('auth-login'))

    def test_login_subview_form_has_correct_method(self):
        response = self.client.get('/')
        form = self._get_login_form(str(response.content))
        self.assertEquals(form.get('method').lower(), 'post')

    def test_index_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplatedUsed(response, 'default/index.html')

    def _get_login_form(self, view_html):
        view_html_soup = BeautifulSoup(view_html, 'html.parser')
        form = view_html_soup.find('form', id='login')

        return form


# MBUI (Might Be Useful Information)
# (July 26, 2019)
#    - We can get away with setting the password during user instantiation
#      since we do not need to hash the passwords. Using `set_password()`
#      hashes the password string, which is not necessary in our tests at the
#      moment. However, we should never ever use this method of setting a
#      user's password in non-tests due to obvious security reasons.


class VotingSubviewTest(TestCase):
    """
    Tests the voting sub-view in the index view (accessed via `/`).

    This subview will only appear to logged-in users that have not yet voted.
    If they have already voted, they will be shown the voted subview. Anonymous
    users will be shown the login subview.

    TODO: Add integration tests to make sure that the candidates are properly
          shown in this subview and can be properly voted for.
    """
    @classmethod
    def setUpTestData(cls):
        # Set up the users.
        _batch = Batch.objects.create(year=2020)
        _section = Section.objects.create(section_name='Emerald')
        _user1 = User.objects.create(
            username='juan',
            password='sample',
            batch=_batch,
            section=_section
        )
        _user2 = User.objects.create(
            username='pedro',
            password='sample',
            batch=_batch,
            section=_section
        )
        _user3 = User.objects.create(
            username='pasta',
            password='sample',
            batch=_batch,
            section=_section
        )

        _party = CandidateParty.objects.create(party_name='Awesome Party')
        _position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        cls._candidate1 = Candidate.objects.create(
            user=_user1,
            party=_party,
            position=_position
        )
        cls._candidate2 = Candidate.objects.create(
            user=_user2,
            party=_party,
            position=_position
        )

        cls.client.login(username='pasta', password='sample')

    def test_logged_in_users_voting_subview(self):
        response = self.client.get('/')
        self.assertIsNotNone(self._get_voting_form(str(response.content)))

    def test_voting_subview_form_has_correct_action_URL(self):
        response = self.client.get('/')
        form = self._get_login_form(str(response.content))
        self.assertEquals(form.get('action'), reverse('auth-login'))

    def test_voting_subview_form_has_correct_method(self):
        response = self.client.get('/')
        form = self._get_login_form(str(response.content))
        self.assertEquals(form.get('method').lower(), 'post')

    def test_index_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplatedUsed(response, 'default/index.html')

    def test_candidates_are_in_the_subview(self):
        response = self.client.get('/')
        view_html_soup = BeautifulSoup(str(response.content), 'html.parser')
        candidate_divs = view_html_soup.find_all(
            'div',
            { 'class': 'candidate' }
        )
        self.assertEquals(len(candidate_divs), 2)

    def _get_voting_form(self, view_html):
        view_html_soup = BeautifulSoup(view_html, 'html.parser')
        form = view_html_soup.find('form', id='voting')

        return form


class VotedSubviewTest(TestCase):
    """
    Tests the voted sub-view in the index view (accessed via `/`).

    This subview will only appear to logged-in users that have voted already.
    If they have not yet voted, they will be shown the voting subview.
    Anonymous users will be shown the login subview.
    """
    @classmethod
    def setUpTestData(cls):
        # Set up the users.
        _batch = Batch.objects.create(year=2020)
        _section = Section.objects.create(section_name='Emerald')
        _user1 = User.objects.create(
            username='juan',
            password='sample',
            batch=_batch,
            section=_section
        )
        _user2 = User.objects.create(
            username='pedro',
            password='sample',
            batch=_batch,
            section=_section
        )
        _user3 = User.objects.create(
            username='pasta',
            password='sample',
            batch=_batch,
            section=_section
        )

        _party = CandidateParty.objects.create(party_name='Awesome Party')
        _position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        cls._candidate1 = Candidate.objects.create(
            user=_user1,
            party=_party,
            position=_position
        )
        cls._candidate2 = Candidate.objects.create(
            user=_user2,
            party=_party,
            position=_position
        )

        Vote.objects.create(
            user=_user3,
            candidate=_candidate1,
            vote_cipher=json.dumps(dict())
        )

    def test_logged_in_users_voted_subview(self):
        self.client.login(username='pasta', password='sample')

        response = self.client.get('/')
        self.assertIsNotNone(self._get_logout_form(str(response.content)))

    def test_voted_subview_form_has_correct_action_URL(self):
        response = self.client.get('/')
        form = self._get_login_form(str(response.content))
        self.assertEquals(form.get('action'), reverse('auth-logout'))

    def test_voted_subview_form_has_correct_method(self):
        response = self.client.get('/')
        form = self._get_login_form(str(response.content))
        self.assertEquals(form.get('method').lower(), 'post')

    def test_index_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplatedUsed(response, 'default/index.html')

    def _get_logout_form(self, view_html):
        view_html_soup = BeautifulSoup(view_html, 'html.parser')
        form = view_html_soup.find('form', id='logout')

        return form
