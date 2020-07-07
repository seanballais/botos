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
        cls._election0 = Election.objects.create(name='Election 0')
        cls._election1 = Election.objects.create(name='Election 1')

        _batch0 = Batch.objects.create(year=0, election=cls._election0)
        _batch1 = Batch.objects.create(year=1, election=cls._election1)
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

        cls._user2 = User.objects.create(
            username='pedro',
            first_name='Pedro',
            last_name='Pendoko',
            type=UserType.VOTER)
        cls._user2.set_password('pendoko')
        cls._user2.save()

        cls._user3 = User.objects.create(
            username='emmanuel',
            first_name='Emmanuel',
            last_name='Pedro',
            type=UserType.VOTER
        )
        cls._user3.set_password('pedro')
        cls._user3.save()

        VoterProfile.objects.create(
            user=cls._user1,
            batch=_batch0,
            section=_section0
        )

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
            election=cls._election0
        )
        _position0 = CandidatePosition.objects.create(
            position_name='Amazing Position 0',
            position_level=0,
            election=cls._election0
        )

        cls._candidate1 = Candidate.objects.create(
            user=cls._user1,
            party=_party0,
            position=_position0,
            election=cls._election0
        )
        cls._candidate2 = Candidate.objects.create(
            user=cls._user2,
            party=_party0,
            position=_position0,
            election=cls._election0
        )
        cls._candidate3 = Candidate.objects.create(
            user=cls._user3,
            party=_party0,
            position=_position0,
            election=cls._election0
        )

        # Election 1 Entities.
        cls._user4 = User.objects.create(
            username='juan1',
            first_name='Juan 1',
            last_name='Pepito',
            type=UserType.VOTER
        )
        cls._user4.set_password('pepito')
        cls._user4.save()

        cls._user5 = User.objects.create(
            username='pedro1',
            first_name='Pedro 1',
            last_name='Pendoko',
            type=UserType.VOTER
        )
        cls._user5.set_password('pendoko')
        cls._user5.save()

        cls._user6 = User.objects.create(
            username='emmanuel1',
            first_name='Emmanuel 1',
            last_name='Pedro',
            type=UserType.VOTER
        )
        cls._user6.set_password('pedro')
        cls._user6.save()

        VoterProfile.objects.create(
            user=cls._user4,
            batch=_batch1,
            section=_section1
        )

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
            election=cls._election1
        )
        _position1 = CandidatePosition.objects.create(
            position_name='Amazing Position 1',
            position_level=0,
            election=cls._election1
        )

        cls._candidate4 = Candidate.objects.create(
            user=cls._user4,
            party=_party1,
            position=_position1,
            election=cls._election1
        )
        cls._candidate5 = Candidate.objects.create(
            user=cls._user5,
            party=_party1,
            position=_position1,
            election=cls._election1
        )
        cls._candidate6 = Candidate.objects.create(
            user=cls._user6,
            party=_party1,
            position=_position1,
            election=cls._election1
        )

    def setUp(self):
        self.client.login(username='admin', password='root')

    def test_anonymous_redirected_to_admin_login(self):
        self.client.logout()
        response = self.client.get(reverse('results'), follow=True)
        self.assertRedirects(
            response,
            '{}?next={}'.format(reverse('index'), reverse('results'))
        )

    def test_non_admin_redirected_to_index(self):
        self.client.login(username='juan', password='pepito')
        response = self.client.get(reverse('results'), follow=True)
        self.assertRedirects(response, '/')

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
                'candidates_voted': str([ self._candidate1.id ])
            }
        )

        self.client.login(username='pedro', password='pendoko')
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([ self._candidate1.id ])
            }
        )

        self.client.login(username='emmanuel', password='pedro')
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([ self._candidate2.id ])
            }
        )

        # For election 1
        self.client.login(username='juan1', password='pepito')
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([ self._candidate4.id ])
            },
        )

        self.client.login(username='pedro1', password='pendoko')
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([ self._candidate4.id ])
            }
        )

        self.client.login(username='emmanuel1', password='pedro')
        self.client.post(
            reverse('vote-processing'),
            {
                'candidates_voted': str([ self._candidate6.id ])
            }
        )

        self.client.login(username='admin', password='root')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertEquals(results['Amazing Position 0'][0].total_votes, 0)
        self.assertEquals(results['Amazing Position 0'][1].total_votes, 1)
        self.assertEquals(results['Amazing Position 0'][2].total_votes, 2)

        self.assertEquals(results['Amazing Position 1'][0].total_votes, 1)
        self.assertEquals(results['Amazing Position 1'][1].total_votes, 0)
        self.assertEquals(results['Amazing Position 1'][2].total_votes, 2)

    def test_results_candidate_name_elections_open(self):
        AppSettings().set('election_state', 'open')
        response = self.client.get(reverse('results'))
        results = response.context['results']

        self.assertNotEquals(
            results['Amazing Position 0'][0].name,
            'Pedro, Emmanuel'
        )
        self.assertNotEquals(
            results['Amazing Position 0'][1].name,
            'Pendoko, Pedro'
        )
        self.assertNotEquals(
            results['Amazing Position 0'][2].name,
            'Pepito, Juan'
        )

        # Just making sure that the other election's candidates appear too.
        self.assertNotEquals(
            results['Amazing Position 1'][0].name,
            'Pedro, Emmanuel 1'
        )
        self.assertNotEquals(
            results['Amazing Position 1'][1].name,
            'Pendoko, Pedro 1'
        )
        self.assertNotEquals(
            results['Amazing Position 1'][2].name,
            'Pepito, Juan 1'
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
            'Pedro, Emmanuel'
        )
        self.assertEquals(
            results['Amazing Position 0'][1].name,
            'Pendoko, Pedro'
        )
        self.assertEquals(
            results['Amazing Position 0'][2].name,
            'Pepito, Juan'
        )

        # Just making sure that the other election's candidates appear too.
        self.assertEquals(
            results['Amazing Position 1'][0].name,
            'Pedro, Emmanuel 1'
        )
        self.assertEquals(
            results['Amazing Position 1'][1].name,
            'Pendoko, Pedro 1'
        )
        self.assertEquals(
            results['Amazing Position 1'][2].name,
            'Pepito, Juan 1'
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

    def test_results_with_election_0_only(self):
        response = self.client.get(
            reverse('results'),
            { 'election': str(self._election0.id) }
        )
        results = response.context['results']

        self.assertEqual(
            results['Amazing Position 0'][0].name,
            'Pedro, Emmanuel'
        )
        self.assertEqual(
            results['Amazing Position 0'][1].name,
            'Pendoko, Pedro'
        )
        self.assertEqual(
            results['Amazing Position 0'][2].name,
            'Pepito, Juan'
        )
        self.assertEqual(len(results), 1)

    def test_results_view_election_tabs(self):
        response = self.client.get(reverse('results'))
        tab_links = response.context['election_tab_links']

        self.assertEqual(tab_links[0].election_id, None)
        self.assertEqual(tab_links[1].election_id, self._election0.id)
        self.assertEqual(tab_links[2].election_id, self._election1.id)

        self.assertEqual(tab_links[0].title, 'All')
        self.assertEqual(tab_links[1].title, 'Election 0')
        self.assertEqual(tab_links[2].title, 'Election 1')

        self.assertEqual(tab_links[0].url, reverse('results'))
        self.assertEqual(
            tab_links[1].url,
            '{}?election={}'.format(reverse('results'), self._election0.id)
        )
        self.assertEqual(
            tab_links[2].url,
            '{}?election={}'.format(reverse('results'), self._election1.id)
        )

        self.assertEqual(len(tab_links), 3)

    def test_results_view_active_election_no_selection(self):
        response = self.client.get(reverse('results'))
        active_election = response.context['active_election']

        self.assertEqual(active_election, None)

    def test_results_view_active_election_select_1(self):
        response = self.client.get(
            reverse('results'),
            { 'election': str(self._election0.id) }
        )
        active_election = response.context['active_election']

        self.assertEqual(active_election, self._election0.id)
