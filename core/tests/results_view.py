from django.test import TestCase
from django.urls import reverse

from core.models import (
    User, Batch, Section, Candidate, CandidateParty, CandidatePosition, Vote
)
from core.utils import AppSettings


class ResultsView(TestCase):
    """
    Tests the results view.

    The results view can be accessed by anyone --even anonymous users. It will
    not accept POST requests. But maybe in the future, it may accept POST
    requests and return a JSONified results.

    The format of the results must be this way:
        {
            'results': {
                '<position>': [
                    [ <candidate name>, <candidate party>, <number of votes> ]
                    ...
                ]
            }
        }

    The candidates and parties will be given a random name if the elections are
    open.

    View URL: `/results
    """
    @classmethod
    def setUpTestData(cls):
        # Set up the test users, candidate, and vote.
        _batch = Batch.objects.create(year=2020)
        _section = Section.objects.create(section_name='Emerald')
        cls._user1 = User.objects.create(
            username='juan',
            password='pepito',
            first_name='Juan',
            last_name='Pepito',
            batch=_batch,
            section=_section
        )
        cls._user2 = User.objects.create(
            username='pedro',
            password='pendoko',
            batch=_batch,
            section=_section
        )
        cls._user3 = User.objects.create(
            username='emmanuel',
            password='pedro',
            batch=_batch,
            section=_section
        )
        cls._admin = User.objects.create(
            username='admin',
            password='root',
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
        cls._candidate3 = Candidate.objects.create(
            user=_user3,
            party=_party,
            position=_position
        )

    def setUp(self):
        self.client.login(username='admin', password='root')
        self.client.post(reverse('admin-election-keys'))

    def test_results_vote_count_no_votes(self):
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position'][0][2], 0)
        self.assertEquals(results['Amazing Position'][1][2], 0)
        self.assertEquals(results['Amazing Position'][2][2], 0)

    def test_results_vote_count_with_votes(self):
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_votes': [
                    self._candidate1.id,
                    self._candidate2.id,
                    self._candidate3.id
                ]
            }
        )

        self.client.login(username='juan', password='pepito')
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_votes': [
                    self._candidate1.id,
                    self._candidate2.id,
                    self._candidate3.id
                ]
            }
        )

        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position'][0][2], 2)
        self.assertEquals(results['Amazing Position'][1][2], 2)
        self.assertEquals(results['Amazing Position'][2][2], 2)

    def test_results_candidate_name_elections_open(self):
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertNotEquals(results['Amazing Position'][0][0], 'Pepito, Juan')

    def test_results_candidate_party_name_elections_open(self):
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertNotEquals(
            results['Amazing Position'][0][1],
            'Awesome Party'
        )

    def test_results_candidate_name_elections_closed(self):
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position'][0][0], 'Pepito, Juan')

    def test_results_candidate_party_name_elections_open(self):
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position'][0][1], 'Awesome Party')
