import json

from django.test import (
    Client, TestCase
)
from django.urls import reverse

from core.models import (
    User, Batch, Section, Election, Candidate, CandidateParty,
    CandidatePosition, Vote, VoterProfile, Setting, UserType
)
from core.utils import AppSettings


class VoteProcessingView(TestCase):
    """
    Tests the vote processing view.

    This subview may only process requests from users that are
    logged in and have not voted yet. Users that have voted already and
    anonymous users will be redirected to `/`.

    The data format for any POST requests is:
        {
            'candidates_voted': [
                <id of candidate voted>,
                <id of another candidate voted>,
                ...
            ]
        }

    Receiving invalid data from a user whom have not voted yet will cause the
    view to return an error message. If any data, valid or not, is received
    from a user who has voted already, a message will be returned saying that
    the user has voted already.

    View URL: `/vote`

    TODO: Add tests here to test support for multiple elections.
          - Must make sure that the candidates that a voter will be casting
            votes for is the same as belong to the same election as the voter's.

    """
    @classmethod
    def setUpTestData(cls):
        # Election 0 has a candidate position that allows for voting two
        # candidates running for the position. Election 1, on the other hand,
        # has a candidate position that allows for voting only one candidate
        # running for the position.
        _election0 = Election.objects.create(name='Election 0')
        _election1 = Election.objects.create(name='Election 1')

        _batch0 = Batch.objects.create(year=0, election=_election0)
        _batch1 = Batch.objects.create(year=1, election=_election1)
        _section0 = Section.objects.create(section_name='Section 0')
        _section1 = Section.objects.create(section_name='Section 1')

        cls._admin = User.objects.create(
            username='admin',
            type=UserType.ADMIN
        )
        cls._admin.set_password('root')
        cls._admin.save()

        # Set up the test users, candidate, and vote for the first election.
        cls._non_voted_user0 = User.objects.create(
            username='juan',
            type=UserType.VOTER
        )
        cls._non_voted_user0.set_password('pepito')
        cls._non_voted_user0.save()

        cls._voted_user0 = User.objects.create(
            username='pedro',
            type=UserType.VOTER
        )
        cls._voted_user0.set_password('pendoko')
        cls._voted_user0.save()

        VoterProfile.objects.create(
            user=cls._non_voted_user0,
            batch=_batch0,
            section=_section0
        )

        VoterProfile.objects.create(
            user=cls._voted_user0,
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
        cls._candidate0 = Candidate.objects.create(
            user=cls._non_voted_user0,
            party=_party0,
            position=_position0,
            election=_election0
        )
        cls._candidate2 = Candidate.objects.create(
            user=cls._voted_user0,
            party=_party0,
            position=_position0,
            election=_election0
        )

        Vote.objects.create(
            user=cls._voted_user0,
            candidate=cls._candidate0,
            election=_election0
        )

        # Set up the test users, candidate, and vote for the second election.
        cls._non_voted_user1 = User.objects.create(
            username='juan1',
            type=UserType.VOTER
        )
        cls._non_voted_user1.set_password('pepito')
        cls._non_voted_user1.save()

        cls._voted_user1 = User.objects.create(
            username='pedro1',
            type=UserType.VOTER
        )
        cls._voted_user1.set_password('pendoko')
        cls._voted_user1.save()

        VoterProfile.objects.create(
            user=cls._non_voted_user1,
            batch=_batch1,
            section=_section1
        )

        VoterProfile.objects.create(
            user=cls._voted_user1,
            batch=_batch1,
            section=_section1
        )

        _party1 = CandidateParty.objects.create(
            party_name='Awesome Party 1',
            election=_election1
        )
        _position1 = CandidatePosition.objects.create(
            position_name='Amazing Position 1',
            position_level=0,
            election=_election1
        )
        cls._candidate1 = Candidate.objects.create(
            user=cls._non_voted_user1,
            party=_party1,
            position=_position1,
            election=_election1
        )
        cls._candidate3 = Candidate.objects.create(
            user=cls._voted_user1,
            party=_party1,
            position=_position1,
            election=_election1
        )

        Vote.objects.create(
            user=cls._voted_user1,
            candidate=cls._candidate1,
            election=_election1
        )

    def test_anonymous_get_requests_redirected_to_index(self):
        response = self.client.get(reverse('vote-processing'), follow=True)
        self.assertRedirects(response, reverse('index'))

    def test_logged_in_get_requests_redirected_to_index(self):
        self.client.login(username='juan', password='pepito')

        self.test_anonymous_get_requests_redirected_to_index()

    def test_anonymous_post_requests_redirected_to_index(self):
        response = self.client.post(
            reverse('vote-processing'),
            {},
            follow=True
        )
        self.assertRedirects(response, reverse('index'))

    def test_non_voted_logged_in_post_requests_with_valid_data(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([ self._candidate0.id ])
            },
            follow=True
        )

        # Let's make sure the right vote got casted.
        try:
            Vote.objects.get(
                user=self._non_voted_user0,
                candidate=self._candidate0
            )
        except Vote.DoesNotExist:
            self.fail('Vote for test candidate was not casted successfully.')

        self.assertRedirects(response, reverse('index'))

    def test_non_voted_logged_in_post_requests_with_invalid_data(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.post(
            reverse('vote-processing'),
            {},
            follow=True
        )
        response_messages = list(response.context['messages'])
        self.assertEquals(
            response_messages[0].message,
            'The votes you sent were invalid. Please try voting again, and/or '
            'contact the system administrator.'
        )

        # Note: We should not test if we get the correct subview, i.e. the
        #       voted sub-view, since testing it is the responsibility of the
        #       index view. The test must be written in VotedSubViewTest
        #       (located in core/tests/index_views.py).
        self.assertRedirects(response, reverse('index'))

    def test_voted_logged_in_post_requests_with_valid_data(self):
        self.client.login(username='pedro', password='pendoko')

        response = self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([ self._candidate0.id ])
            },
            follow=True
        )
        response_messages = list(response.context['messages'])
        self.assertEquals(
            response_messages[0].message,
            'You are no longer allowed to vote since you have voted already.'
        )

        self.assertRedirects(response, reverse('index'))


    def test_voted_logged_in_post_requests_with_invalid_data(self):
        self.client.login(username='pedro', password='pendoko')

        response = self.client.post(
            reverse('vote-processing'),
            {},
            follow=True
        )
        response_messages = list(response.context['messages'])
        self.assertEquals(
            response_messages[0].message,
            'You are no longer allowed to vote since you have voted already.'
            ' Additionally, the votes you were invalid too.'
        )

        self.assertRedirects(response, reverse('index'))

    def test_voted_logged_in_post_requests_with_nonlist_data(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.post(
            reverse('vote-processing'),
            { 'candidates_voted': str({}) },
            follow=True
        )
        response_messages = list(response.context['messages'])
        self.assertEquals(
            response_messages[0].message,
            'The votes you sent were invalid. Please try voting '
            'again, and/or contact the system administrator.'
        )

        self.assertRedirects(response, reverse('index'))

    def test_casting_no_votes(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.post(
            reverse('vote-processing'),
            { 'candidates_voted': str([]) },
            follow=True
        )

        # Let's make sure no vote got casted.
        try:
            Vote.objects.get(user=self._non_voted_user0)
            self.fail('Vote was casted.')
        except Vote.DoesNotExist:
            pass

        self.assertRedirects(response, reverse('index'))

    def test_casting_with_duplicate_votes(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.post(
            reverse('vote-processing'),
            # No candidate with id of 1000.
            { 
                'candidates_voted': str([
                    self._candidate0.id, self._candidate0.id
                ])
            },
            follow=True
        )

        response_messages = list(response.context['messages'])
        self.assertEquals(
            response_messages[0].message,
            'The votes you sent were invalid. Please try voting '
            'again, and/or contact the system administrator.'
        )

        # Let's make sure no vote got casted.
        try:
            Vote.objects.get(user=self._non_voted_user0)
            self.fail('Vote was casted.')
        except Vote.DoesNotExist:
            pass

        self.assertRedirects(response, reverse('index'))

    def test_casting_votes_for_non_existent_candidates(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.post(
            reverse('vote-processing'),
            # No candidate with id of 1000.
            { 'candidates_voted': str([ 1000 ])},
            follow=True
        )

        response_messages = list(response.context['messages'])
        self.assertEquals(
            response_messages[0].message,
            'The votes you sent were invalid. Please try voting '
            'again, and/or contact the system administrator.'
        )

        # Let's make sure no vote got casted.
        try:
            Vote.objects.get(user=self._non_voted_user0)
            self.fail('Vote was casted.')
        except Vote.DoesNotExist:
            pass

        self.assertRedirects(response, reverse('index'))

    def test_casting_votes_for_a_candidate_in_a_different_election(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.post(
            reverse('vote-processing'),
            # Candidate is from a different election.
            { 'candidates_voted': str([ self._candidate1.id ]) },
            follow=True
        )

        response_messages = list(response.context['messages'])
        self.assertEqual(
            response_messages[0].message,
            'The votes you sent were invalid. Please try voting '
            'again, and/or contact the system administrator.'
        )

        # Let's make sure no vote got casted.
        try:
            Vote.objects.get(user=self._non_voted_user0)
            self.fail('Vote was casted.')
        except Vote.DoesNotExist:
            pass

        self.assertRedirects(response, reverse('index'))

    def test_casting_votes_two_candidates_same_position_max_2_cands(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.post(
            reverse('vote-processing'),
            # Candidate is from a different election.
            {
                'candidates_voted': str([
                    self._candidate0.id, self._candidate2.id
                ])
            },
            follow=True
        )

        try:
            Vote.objects.get(
                user=self._non_voted_user0,
                candidate=self._candidate0
            )
            Vote.objects.get(
                user=self._non_voted_user0,
                candidate=self._candidate2
            )
        except Vote.DoesNotExist:
            self.fail(
                'Vote for all election 0 candidates were not '
                'casted successfully.'
            )

        self.assertRedirects(response, reverse('index'))

    def test_casting_votes_two_candidates_same_position_max_1_cand(self):
        self.client.login(username='juan1', password='pepito')

        response = self.client.post(
            reverse('vote-processing'),
            # Candidate is from a different election.
            {
                'candidates_voted': str([
                    self._candidate1.id, self._candidate3.id
                ])
            },
            follow=True
        )

        response_messages = list(response.context['messages'])
        self.assertEqual(
            response_messages[0].message,
            'The votes you sent were invalid. Please try voting '
            'again, and/or contact the system administrator.'
        )

        # Let's make sure no vote got casted.
        try:
            Vote.objects.get(user=self._non_voted_user1)
            self.fail('Vote was casted.')
        except Vote.DoesNotExist:
            pass

        self.assertRedirects(response, reverse('index'))


class VoteProcessingTargetBatchesTest(TestCase):
    """
    Tests the vote processing for voting candidates whose positions are only
    voteable by select batches.

    Separating this test from the vote processing test allows for cleaner test
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

        cls._user1 = User.objects.create(
            username='juan',
            first_name='Juan',
            last_name='Sample',
            type=UserType.VOTER
        )
        cls._user1.set_password('sample')
        cls._user1.save()

        cls._user2 = User.objects.create(
            username='pedro',
            first_name='Pedro',
            last_name='Sample',
            type=UserType.VOTER
        )
        cls._user2.set_password('sample')
        cls._user2.save()

        VoterProfile.objects.create(
            user=cls._user1,
            batch=_batch0,
            section=_section0
        )

        VoterProfile.objects.create(
            user=cls._user2,
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

        cls._candidate1 = Candidate.objects.create(
            user=cls._user1,
            party=_party0,
            position=_position0,
            election=_election
        )

        cls._candidate2 = Candidate.objects.create(
            user=cls._user2,
            party=_party1,
            position=_position1,
            election=_election
        )

    def test_voting_for_candidate_for_voter_batch(self):
        self.client.login(username='juan', password='sample')

        response = self.client.post(
            reverse('vote-processing'),
            # Candidate is from a different election.
            {
                'candidates_voted': str([
                    self._candidate1.id
                ])
            },
            follow=True
        )

        # Let's make sure the right vote got casted.
        try:
            Vote.objects.get(
                user=self._user1,
                candidate=self._candidate1
            )
        except Vote.DoesNotExist:
            self.fail(
                'Vote for candidate that can be voted by user was not '
                'casted successfully.'
            )

        self.assertRedirects(response, reverse('index'))

    def test_voting_for_candidate_not_for_voter_batch(self):
        self.client.login(username='juan', password='sample')

        response = self.client.post(
            reverse('vote-processing'),
            # Candidate is from a different election.
            {
                'candidates_voted': str([
                    self._candidate2.id
                ])
            },
            follow=True
        )

        response_messages = list(response.context['messages'])
        self.assertEqual(
            response_messages[0].message,
            'The votes you sent were invalid. Please try voting '
            'again, and/or contact the system administrator.'
        )

        # Let's make sure the right vote got casted.
        try:
            Vote.objects.get(
                user=self._user1,
                candidate=self._candidate2
            )
            self.fail(
                'Vote for candidate that cannot be voted by user was casted.'
            )
        except Vote.DoesNotExist:
            pass

        self.assertRedirects(response, reverse('index'))
