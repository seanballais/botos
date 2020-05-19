from django.test import (
    Client, TestCase
)
from django.urls import reverse

from core.models import (
    User, Batch, Section, Candidate, CandidateParty, CandidatePosition, Vote,
    Setting
)
from core.utils import AppSettings


class ResultsViewTest(TestCase):
    """
    Tests the results view.

    The results view can be accessed by anyone --even anonymous users. It will
    not accept POST requests. But maybe in the future, it may accept POST
    requests and return a JSONified results.

    The format of the results must be this way:
        {
            'results': {
                '<position>': [ <candidate>, ... ],
            }
        }

    <candidate> is a named tuple with the following properties:
        - name
        - party name
        - avatar URL
        - total votes

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
            first_name='Juan',
            last_name='Pepito',
            batch=_batch,
            section=_section
        )
        cls._user1.set_password('pepito')
        cls._user1.save()

        cls._user2 = User.objects.create(
            username='pedro',
            batch=_batch,
            section=_section
        )
        cls._user2.set_password('pendoko')
        cls._user2.save()

        cls._user3 = User.objects.create(
            username='emmanuel',
            batch=_batch,
            section=_section
        )
        cls._user3.set_password('pedro')
        cls._user3.save()

        cls._admin = User.objects.create(
            username='admin',
            batch=_batch,
            section=_section,
            is_staff=True,
            is_superuser=True
        )
        cls._admin.set_password('root')
        cls._admin.save()

        _party = CandidateParty.objects.create(party_name='Awesome Party')
        _position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        cls._candidate1 = Candidate.objects.create(
            user=cls._user1,
            party=_party,
            position=_position
        )
        cls._candidate2 = Candidate.objects.create(
            user=cls._user2,
            party=_party,
            position=_position
        )
        cls._candidate3 = Candidate.objects.create(
            user=cls._user3,
            party=_party,
            position=_position
        )

        # The keys should only be generated once.
        client = Client()
        client.login(username='admin', password='root')
        client.post(reverse('admin-election-keys'), follow=True)

    def setUp(self):
        self.client.login(username='admin', password='root')

    def test_results_vote_count_no_votes(self):
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position'][0].total_votes, 0)
        self.assertEquals(results['Amazing Position'][1].total_votes, 0)
        self.assertEquals(results['Amazing Position'][2].total_votes, 0)

    def test_results_vote_count_with_votes(self):
        self.client.login(username='juan', password='pepito')
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([
                    self._candidate1.id,
                    self._candidate2.id,
                    self._candidate3.id
                ])
            },
        )

        self.client.login(username='pedro', password='pendoko')
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([
                    self._candidate1.id,
                    self._candidate2.id,
                    self._candidate3.id
                ])
            }
        )

        self.client.login(username='admin', password='root')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position'][0].total_votes, 2)
        self.assertEquals(results['Amazing Position'][1].total_votes, 2)
        self.assertEquals(results['Amazing Position'][2].total_votes, 2)

    def test_results_candidate_name_elections_open(self):
        AppSettings().set('election_state', 'open')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertNotEquals(
            results['Amazing Position'][0].name,
            'Pepito, Juan'
        )

    def test_results_candidate_party_name_elections_open(self):
        AppSettings().set('election_state', 'open')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertNotEquals(
            results['Amazing Position'][0].party_name,
            'Awesome Party'
        )

    def test_results_candidate_name_elections_closed(self):
        AppSettings().set('election_state', 'closed')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position'][0].name, 'Pepito, Juan')

    def test_results_candidate_party_name_elections_closed(self):
        AppSettings().set('election_state', 'closed')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(
            results['Amazing Position'][0].party_name,
            'Awesome Party'
        )

    def test_no_public_key_generated_yet(self):
        Setting.objects.get(key='public_election_key').delete()

        response = self.client.get(reverse('results'))
        results = response.context['results']
        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Election keys have not been generated yet.'
        )
        self.assertEqual(results, {})

    def test_no_private_key_generated_yet(self):
        Setting.objects.get(key='private_election_key').delete()

        response = self.client.get(reverse('results'))
        results = response.context['results']
        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Private election key has not been generated yet.'
        )
        self.assertEqual(results, {})
