from django.test import (
    Client, TestCase
)
from django.urls import reverse

from core.models import (
    User, Batch, Section, Election, Candidate, CandidateParty,
    CandidatePosition, Vote, Setting, UserType, VoterProfile
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
        _election0 = Election.objects.create(name='Election 0')
        _election1 = Election.objects.create(name='Election 1')

        _batch0 = Batch.objects.create(year=0, election=_election0)
        _batch1 = Batch.objects.create(year=1, election=_election1)
        _section0 = Section.objects.create(section_name='Section 0')
        _section1 = Section.objects.create(section_name='Section 1')

        cls._admin = User.objects.create(username='admin', type=UserType.ADMIN)
        cls._admin.set_password('root')
        cls._admin.save()

        # Election 0 Entities.
        cls._user1 = User.objects.create(
            username='juan',
            first_name='Juan',
            last_name='Pepito',
            type=UserType.VOTER
        )
        cls._user1.set_password('pepito')
        cls._user1.save()

        cls._user2 = User.objects.create(username='pedro', type=UserType.VOTER)
        cls._user2.set_password('pendoko')
        cls._user2.save()

        cls._user3 = User.objects.create(
            username='emmanuel',
            type=UserType.VOTER
        )
        cls._user3.set_password('pedro')
        cls._user3.save()

        VoterProfile.objects.create(
            user=cls._user2,
            batch=_batch0,
            section=_section0
        )

        VoterProfile.objects.create(
            user=cls._user3,
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
            election=_election0
        )

        cls._candidate1 = Candidate.objects.create(
            user=cls._user1,
            party=_party0,
            position=_position0,
            election=_election0
        )
        cls._candidate2 = Candidate.objects.create(
            user=cls._user2,
            party=_party0,
            position=_position0,
            election=_election0
        )
        cls._candidate3 = Candidate.objects.create(
            user=cls._user3,
            party=_party0,
            position=_position0,
            election=_election0
        )

        # Election 1 Entities.
        cls._user4 = User.objects.create(
            username='juan1',
            first_name='Juan',
            last_name='Pepito',
            type=UserType.VOTER
        )
        cls._user4.set_password('pepito')
        cls._user4.save()

        cls._user5 = User.objects.create(
            username='pedro1',
            type=UserType.VOTER
        )
        cls._user5.set_password('pendoko')
        cls._user5.save()

        cls._user6 = User.objects.create(
            username='emmanuel1',
            type=UserType.VOTER
        )
        cls._user6.set_password('pedro')
        cls._user6.save()

        VoterProfile.objects.create(
            user=cls._user5,
            batch=_batch1,
            section=_section1
        )

        VoterProfile.objects.create(
            user=cls._user6,
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

        cls._candidate4 = Candidate.objects.create(
            user=cls._user4,
            party=_party1,
            position=_position1,
            election=_election1
        )
        cls._candidate5 = Candidate.objects.create(
            user=cls._user5,
            party=_party1,
            position=_position1,
            election=_election1
        )
        cls._candidate6 = Candidate.objects.create(
            user=cls._user6,
            party=_party1,
            position=_position1,
            election=_election1
        )

    def setUp(self):
        self.client.login(username='admin', password='root')

    def test_results_vote_count_no_votes(self):
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position 0'][0].total_votes, 0)
        self.assertEquals(results['Amazing Position 0'][1].total_votes, 0)
        self.assertEquals(results['Amazing Position 0'][2].total_votes, 0)

        self.assertEquals(results['Amazing Position 1'][0].total_votes, 0)
        self.assertEquals(results['Amazing Position 1'][1].total_votes, 0)
        self.assertEquals(results['Amazing Position 1'][2].total_votes, 0)

    def test_results_vote_count_with_votes(self):
        # For election 0
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

        # For election 1
        self.client.login(username='juan1', password='pepito')
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

        self.client.login(username='pedro1', password='pendoko')
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([
                    self._candidate4.id,
                    self._candidate5.id,
                    self._candidate6.id
                ])
            }
        )

        self.client.login(username='admin', password='root')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position 0'][0].total_votes, 2)
        self.assertEquals(results['Amazing Position 0'][1].total_votes, 2)
        self.assertEquals(results['Amazing Position 0'][2].total_votes, 2)

        self.assertEquals(results['Amazing Position 1'][0].total_votes, 2)
        self.assertEquals(results['Amazing Position 1'][1].total_votes, 2)
        self.assertEquals(results['Amazing Position 1'][2].total_votes, 2)

    def test_results_candidate_name_elections_open(self):
        AppSettings().set('election_state', 'open')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertNotEquals(
            results['Amazing Position 0'][0].name,
            'Pepito, Juan'
        )

        # Just making sure that the other election's candidates appear too.
        self.assertNotEquals(
            results['Amazing Position 1'][0].name,
            'Pepito, Juan'
        )

    def test_results_candidate_party_name_elections_open(self):
        AppSettings().set('election_state', 'open')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertNotEquals(
            results['Amazing Position 0'][0].party_name,
            'Awesome Party 0'
        )

        # Just making sure that the other election's candidates appear too.
        self.assertNotEquals(
            results['Amazing Position 1'][0].party_name,
            'Awesome Party 1'
        )

    def test_results_candidate_name_elections_closed(self):
        AppSettings().set('election_state', 'closed')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(
            results['Amazing Position 0'][0].name,
            'Pepito, Juan'
        )

        # Just making sure that the other election's candidates appear too.
        self.assertEquals(
            results['Amazing Position 1'][0].name,
            'Pepito, Juan'
        )

    def test_results_candidate_party_name_elections_closed(self):
        AppSettings().set('election_state', 'closed')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(
            results['Amazing Position 0'][0].party_name,
            'Awesome Party 0'
        )

        # Just making sure that the other election's candidates appear too.
        self.assertEquals(
            results['Amazing Position 1'][0].party_name,
            'Awesome Party 1'
        )
