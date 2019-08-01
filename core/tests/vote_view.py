import json

from django.test import TestCase
from django.urls import reverse

from core.models import (
    User, Batch, Section, Candidate, CandidateParty, CandidatePosition, Vote
)


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
    """
    @classmethod
    def setUpTestData(cls):
        # Set up the test users, candidate, and vote.
        _batch = Batch.objects.create(year=2020)
        _section = Section.objects.create(section_name='Emerald')
        cls._non_voted_user = User.objects.create(
            username='juan',
            password='pepito',
            batch=_batch,
            section=_section
        )

        cls._voted_user = User.objects.create(
            username='pedro',
            password='pendoko',
            batch=_batch,
            section=_section
        )

        _party = CandidateParty.objects.create(party_name='Awesome Party')
        _position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        cls._candidate = Candidate.objects.create(
            user=_non_voted_user,
            party=_party,
            position=_position
        )

        Vote.objects.create(
            user=_voted_user,
            candidate=cls._candidate,
            vote_cipher=json.dumps(dict())
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
        # (July 27, 2019)
        # Why haven't I thought of logging in the test user this way before?
        self.client.login(
            username=self._non_voted_user.username,
            password=self._non_voted_user.password
        )

        # Generate the election keys first.
        self.client.post(reverse('admin-election-keys'), follow=True)

        response = self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': [ _candidate.id ]
            },
            follow=True
        )

        # Let's make sure the right vote got casted.
        try:
            Vote.objects.get(
                user__id=self._non_voted_user.id,
                candidate__id=self._candidate.id
            )
        except Vote.DoesNotExist:
            self.fail('Vote for test candidate was not casted successfully.')

        self.assertRedirects(response, reverse('index'))

    def test_non_voted_logged_in_post_requests_with_invalid_data(self):
        self.client.login(
            username=self._non_voted_user.username,
            password=self._non_voted_user.password
        )

        response = self.client.post(
            reverse('vote-processing'),
            {},
            follow=True
        )
        response_messages = list(response.context['messages'])
        self.assertEquals(
            response_messages[0],
            'The votes you sent were invalid. Please try voting again, and/or '
            'contact the system administrator.'
        )

        # Note: We should not test if we get the correct subview, i.e. the
        #       voted sub-view, since testing it is the responsibility of the
        #       index view. The test must be written in VotedSubViewTest
        #       (located in core/tests/index_views.py).
        self.assertRedirects(response, reverse('index'))

    def test_voted_logged_in_post_requests_with_valid_data(self):
        self.client.login(
            username=self._voted_user.username,
            password=self._voted_user.password
        )

        response = self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': [ _candidate.id ]
            },
            follow=True
        )
        response_messages = list(response.context['messages'])
        self.assertEquals(
            response_messages[0],
            'You are no longer allowed to vote since you have voted already.'
        )

        self.assertRedirects(response, reverse('index'))


    def test_voted_logged_in_post_requests_with_invalid_data(self):
        self.client.login(
            username=self._voted_user.username,
            password=self._voted_user.password
        )

        response = self.client.post(
            reverse('vote-processing'),
            {},
            follow=True
        )
        response_messages = list(response.context['messages'])
        self.assertEquals(
            response_messages[0],
            'You are no longer allowed to vote since you have voted already.'
            ' Additionally, the votes you were invalid too.'
        )

        self.assertRedirects(response, reverse('index'))