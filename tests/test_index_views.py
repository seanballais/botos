from collections import OrderedDict
import json

from bs4 import BeautifulSoup

from django.test import TestCase
from django.urls import reverse

from core.models import (
    User, Batch, Section, Candidate, CandidateParty, CandidatePosition, Vote,
    UserType, Election, VoterProfile
)
from core.utils import AppSettings


class IndexViewTest(TestCase):
    """
    Tests the index view, in general. No specific subview is being tested here.
    """
    @classmethod
    def setUpTestData(cls):
        cls._election = Election.objects.create(name='Election')
        cls._batch = Batch.objects.create(year=0, election=cls._election)
        cls._section = Section.objects.create(section_name='Section')

        # Set up the users.
        _user1 = User.objects.create(username='juan', type=UserType.VOTER)
        _user1.set_password('sample')
        _user1.save()

        _user2 = User.objects.create(username='pedro', type=UserType.VOTER)
        _user2.set_password('sample')
        _user2.save()

        cls._user3 = User.objects.create(
            username='pasta',
            password='sample',
            type=UserType.VOTER
        )
        cls._user3.set_password('sample')
        cls._user3.save()

        VoterProfile.objects.create(
            user=cls._user3,
            batch=cls._batch,
            section=cls._section
        )

        _party = CandidateParty.objects.create(
            party_name='Awesome Party',
            election=cls._election
        )
        _position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0,
            election=cls._election
        )
        cls._candidate1 = Candidate.objects.create(
            user=_user1,
            party=_party,
            position=_position,
            election=cls._election
        )

    def test_anonymous_users_post_index(self):
        response = self.client.post(reverse('index'), follow=True)
        self.assertRedirects(response, reverse('index'))

    def test_logged_in_non_voted_users_post_index(self):
        self.client.login(username='pasta', password='sample')

        response = self.client.post(reverse('index'), follow=True)
        self.assertRedirects(response, reverse('index'))

    def test_logged_in_voted_users_post_index(self):
        Vote.objects.create(
            user=self._user3,
            candidate=self._candidate1,
            election=self._election
        )

        self.client.login(username='pasta', password='sample')

        response = self.client.post(reverse('index'), follow=True)
        self.assertRedirects(response, reverse('index'))


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
        self.assertTemplateUsed(response, 'default/index.html')

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
        _election0 = Election.objects.create(name='Election 0')
        _election1 = Election.objects.create(name='Election 1')

        # Set up the users.
        _batch0 = Batch.objects.create(year=0, election=_election0)
        _batch1 = Batch.objects.create(year=1, election=_election1)
        _section0 = Section.objects.create(section_name='Section 0')
        _section1 = Section.objects.create(section_name='Section 1')

        _user1 = User.objects.create(
            username='juan',
            first_name='Juan',
            last_name='Sample',
            type=UserType.VOTER
        )
        _user1.set_password('sample')
        _user1.save()

        _user2 = User.objects.create(
            username='pedro',
            first_name='Pedro',
            last_name='Sample',
            type=UserType.VOTER
        )
        _user2.set_password('sample')
        _user2.save()

        _user3 = User.objects.create(
            username='pasta',
            first_name='Pasta',
            last_name='Sample',
            type=UserType.VOTER
        )
        _user3.set_password('sample')
        _user3.save()

        _user4 = User.objects.create(
            username='hollow',
            first_name='Hollow',
            last_name='Knight',
            type=UserType.VOTER
        )
        _user4.set_password('knight')
        _user4.save()

        _user5 = User.objects.create(
            username='hollow1',
            first_name='Hollow 1',
            last_name='Knight',
            type=UserType.VOTER
        )
        _user5.set_password('knight')
        _user5.save()

        _user6 = User.objects.create(
            username='blabla',
            first_name='Blabla',
            last_name='Haha',
            type=UserType.VOTER
        )
        _user6.set_password('haha')
        _user6.save()

        VoterProfile.objects.create(
            user=_user3,
            batch=_batch0,
            section=_section0
        )

        VoterProfile.objects.create(
            user=_user4,
            batch=_batch1,
            section=_section1
        )

        _party0 = CandidateParty.objects.create(
            party_name='Awesome Party 0',
            election=_election0
        )
        _party1 = CandidateParty.objects.create(
            party_name='Awesome Party 1',
            election=_election1
        )
        _position0 = CandidatePosition.objects.create(
            position_name='Amazing Position 0',
            position_level=0,
            max_num_selected_candidates=2,
            election=_election0
        )
        _position1 = CandidatePosition.objects.create(
            position_name='Amazing Position 1',
            position_level=0,
            election=_election1
        )
        _position2 = CandidatePosition.objects.create(
            position_name='Amazing Position 2',
            position_level=1,
            election=_election0
        )
        _position3 = CandidatePosition.objects.create(
            position_name='Amazing Position 3',
            position_level=1,
            election=_election1
        )
        cls._candidate1 = Candidate.objects.create(
            user=_user1,
            party=_party0,
            position=_position0,
            election=_election0
        )
        cls._candidate2 = Candidate.objects.create(
            user=_user2,
            party=_party1,
            position=_position1,
            election=_election1
        )
        cls._candidate3 = Candidate.objects.create(
            user=_user3,
            party=_party0,
            position=_position0,
            election=_election0
        )
        cls._candidate4 = Candidate.objects.create(
            user=_user4,
            party=_party1,
            position=_position1,
            election=_election1
        )
        cls._candidate5 = Candidate.objects.create(
            user=_user5,
            party=_party0,
            position=_position2,
            election=_election0
        )
        cls._candidate6 = Candidate.objects.create(
            user=_user6,
            party=_party1,
            position=_position3,
            election=_election1
        )

    def setUp(self):
        self.client.login(username='pasta', password='sample')

    def test_logged_in_users_voting_subview(self):
        response = self.client.get('/')
        self.assertIsNotNone(self._get_voting_form(str(response.content)))

    def test_voting_subview_form_has_correct_action_URL(self):
        response = self.client.get('/')
        form = self._get_voting_form(str(response.content))
        self.assertEquals(form.get('action'), reverse('vote-processing'))

    def test_voting_subview_form_has_correct_method(self):
        response = self.client.get('/')
        form = self._get_voting_form(str(response.content))
        self.assertEquals(form.get('method').lower(), 'post')

    def test_index_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'default/index.html')

    def test_candidates_are_in_the_subview(self):
        response = self.client.get('/')
        view_html_soup = BeautifulSoup(str(response.content), 'html.parser')
        candidate_divs = view_html_soup.find_all(
            'div',
            { 'class': 'candidate' }
        )
        self.assertEquals(len(candidate_divs), 3)

    def test_candidate_in_election_0_correct(self):
        response = self.client.get('/', follow=True)
        candidates = response.context['candidates']

        # There should only be one candidate in the election the current user
        # is participating in.
        candidates_list = [
            c for i in list(candidates.values()) for c in i["candidates"]
        ]
        self.assertEqual(len(candidates_list), 3)
        self.assertEqual(
            candidates,
            OrderedDict([
                (
                    'Amazing Position 0',
                    {
                        "candidates": [ self._candidate1, self._candidate3 ],
                        "max_num_selected_candidates": 2
                    }
                ),
                (
                    'Amazing Position 2',
                    {
                        "candidates": [ self._candidate5 ],
                        "max_num_selected_candidates": 1
                    }
                )
            ])
        )

    def test_candidate_in_election_1_correct(self):
        # We still need to login to the 'hollow' account, since, by default,
        # we log in to the 'pasta' account.
        self.client.login(username='hollow', password='knight')
        response = self.client.get('/', follow=True)
        candidates = response.context['candidates']

        # There should only be one candidate in the election the current user
        # is participating in.
        candidates_list = [
            c for i in list(candidates.values()) for c in i["candidates"]
        ]
        self.assertEqual(len(candidates_list), 3)
        self.assertEqual(
            candidates,
            OrderedDict([
                (
                    'Amazing Position 1',
                    {
                        "candidates": [ self._candidate4, self._candidate2 ],
                        "max_num_selected_candidates": 1
                    }
                ),
                (
                    'Amazing Position 3',
                    {
                        "candidates": [ self._candidate6 ],
                        "max_num_selected_candidates": 1
                    }
                )
            ])
        )

    def _get_voting_form(self, view_html):
        view_html_soup = BeautifulSoup(view_html, 'html.parser')
        form = view_html_soup.find('form', id='voting')

        return form


class VotingSubviewTargetBatchesTest(TestCase):
    """
    Tests the voting subview with candidates whose positions are only voteable
    by select batches (e.g. representatives for certain batches).

    Separating this test from the voting subview test allows for cleaner test
    code.
    """
    @classmethod
    def setUpTestData(cls):
        _election = Election.objects.create(name='Election')

        # Set up the users.
        _batch0 = Batch.objects.create(year=0, election=_election)
        _batch1 = Batch.objects.create(year=1, election=_election)
        _section0 = Section.objects.create(section_name='Section 0')
        _section1 = Section.objects.create(section_name='Section 1')

        _user1 = User.objects.create(
            username='juan',
            first_name='Juan',
            last_name='Sample',
            type=UserType.VOTER
        )
        _user1.set_password('sample')
        _user1.save()

        _user2 = User.objects.create(
            username='pedro',
            first_name='Pedro',
            last_name='Sample',
            type=UserType.VOTER
        )
        _user2.set_password('sample')
        _user2.save()

        _user3 = User.objects.create(
            username='pendoko',
            first_name='Pedro',
            last_name='Sample',
            type=UserType.VOTER
        )

        VoterProfile.objects.create(
            user=_user1,
            batch=_batch0,
            section=_section0
        )

        VoterProfile.objects.create(
            user=_user2,
            batch=_batch1,
            section=_section1
        )

        VoterProfile.objects.create(
            user=_user3,
            batch=_batch1,
            section=_section1
        )

        _party0 = CandidateParty.objects.create(
            party_name='Awesome Party 0',
            election=_election
        )
        _party1 = CandidateParty.objects.create(
            party_name='Awesome Party 1',
            election=_election
        )

        _position0 = CandidatePosition.objects.create(
            position_name='Amazing Position 0',
            position_level=0,
            election=_election
        )
        _position0.target_batches.add(_batch0)

        _position1 = CandidatePosition.objects.create(
            position_name='Amazing Position 1',
            position_level=0,
            election=_election
        )
        _position0.target_batches.add(_batch1)

        _position2 = CandidatePosition.objects.create(
            position_name='Amazing Position 2',
            position_level=0,
            election=_election
        )

        cls._candidate1 = Candidate.objects.create(
            user=_user1,
            party=_party0,
            position=_position0,
            election=_election
        )

        cls._candidate2 = Candidate.objects.create(
            user=_user2,
            party=_party1,
            position=_position1,
            election=_election
        )

        cls._candidate3 = Candidate.objects.create(
            user=_user3,
            party=_party1,
            position=_position1,
            election=_election
        )

    def test_correct_candidates_appear_for_voters(self):
        self.client.login(username='juan', password='sample')
        response = self.client.get('/', follow=True)
        candidates = response.context['candidates']

        # There should only be one candidate in the election the current user
        # is participating in.
        candidates_list = [
            c for i in list(candidates.values()) for c in i["candidates"]
        ]
        self.assertEqual(len(candidates_list), 2)
        self.assertEqual(
            candidates,
            OrderedDict([
                (
                    'Amazing Position 0',
                    {
                        "candidates": [ self._candidate1.id ],
                        "max_num_selected_candidates": 1
                    },
                ),
                (
                    'Amazing Position 2',
                    {
                        "candidates": [ self._candidate3.id ],
                        "max_num_selected_candidates": 1
                    }
                )
            ])
        )

        self.client.login(username='pedro', password='sample')
        response = self.client.get('/', follow=True)
        candidates = response.context['candidates']

        # There should only be one candidate in the election the current user
        # is participating in.
        candidates_list = [
            c for i in list(candidates.values()) for c in i["candidates"]
        ]
        self.assertEqual(len(candidates_list), 1)
        self.assertEqual(
            candidates,
            OrderedDict([
                (
                    'Amazing Position 1',
                    {
                        "candidates": [ self._candidate2.id ],
                        "max_num_selected_candidates": 1
                    },
                ),
                (
                    'Amazing Position 2',
                    {
                        "candidates": [ self._candidate3.id ],
                        "max_num_selected_candidates": 1
                    }
                )
            ])
        )


class VotedSubviewTest(TestCase):
    """
    Tests the voted sub-view in the index view (accessed via `/`).

    This subview will only appear to logged-in users that have voted already.
    If they have not yet voted, they will be shown the voting subview.
    Anonymous users will be shown the login subview.
    """
    @classmethod
    def setUpTestData(cls):
        _election = Election.objects.create(name='Election')

        # Set up the users.
        _batch = Batch.objects.create(year=0, election=_election)
        _section = Section.objects.create(section_name='Section')

        _user1 = User.objects.create(username='juan', type=UserType.VOTER)
        _user1.set_password('sample')
        _user1.save()

        _user3 = User.objects.create(username='pasta', type=UserType.VOTER)
        _user3.set_password('sample')
        _user3.save()

        VoterProfile.objects.create(
            user=_user3,
            batch=_batch,
            section=_section
        )

        _party = CandidateParty.objects.create(
            party_name='Awesome Party',
            election=_election
        )
        _position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0,
            election=_election
        )
        cls._candidate1 = Candidate.objects.create(
            user=_user1,
            party=_party,
            position=_position,
            election=_election
        )

        Vote.objects.create(
            user=_user3,
            candidate=cls._candidate1,
            election=_election
        )

    def setUp(self):
        self.client.login(username='pasta', password='sample')

    def test_logged_in_users_voted_subview(self):
        response = self.client.get('/')
        self.assertIsNotNone(self._get_logout_button(str(response.content)))

    def test_index_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'default/index.html')

    def _get_logout_button(self, view_html):
        view_html_soup = BeautifulSoup(view_html, 'html.parser')
        button = view_html_soup.find('button', class_='logout-btn')

        return button
