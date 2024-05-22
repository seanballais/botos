from collections import (
    namedtuple, OrderedDict
)
import datetime
import random

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from core.decorators import (
    login_required
)
from core.models import (
    User, Candidate, Vote, UserType, Election
)
from core.utils import AppSettings


@method_decorator(
    login_required(
        login_url='/',
        next='/admin/results/'
    ),
    name='dispatch',
)
class ResultsView(TemplateView):
    """
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
    _template_name = AppSettings().get('template', default='default')
    template_name = '{}/results.html'.format(_template_name)

    def dispatch(self, request, *args, **kwargs):
        if request.user.type != UserType.ADMIN:
            messages.error(
                request,
                'You attempted to access a page you are not authorized '
                'to access.'
            )
            return redirect(reverse('index'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        election_id = self.request.GET.get('election', None)
        if election_id:
            election_id = int(election_id)

        context['results'] = self._get_vote_results(election_id)
        context['current_time'] = datetime \
            .datetime \
            .now(datetime.UTC) \
            .replace(tzinfo=datetime.timezone.utc)
        context['total_voters'] = User.objects.count()
        context['election_state'] = AppSettings().get(
            'election_state',
            'closed'
        )
        context['election_tab_links'] = self._get_election_tab_links()
        context['active_election'] = election_id

        return context

    def _get_vote_results(self, election_id=None):
        election_state = AppSettings().get('election_state', 'closed')
        CandidateResult = namedtuple(
            'CandidateResult',
            'name party_name avatar_url total_votes'
        )

        results = OrderedDict()

        if election_id:
            candidates = Candidate.objects.filter(election__id=election_id)
        else:
            candidates = Candidate.objects.all()

        for candidate in candidates:
            total_num_votes = Vote.objects.filter(candidate=candidate).count()

            position = str(candidate.position.position_name)
            if election_state == 'open':
                candidate_name = self._get_random_candidate_name()
                party_name = self._get_random_party_name()
                avatar_url = '{}{}'.format(
                    settings.MEDIA_URL,  # Assumes the URL is prefixed and
                    # suffixed with a forward slash.
                    'avatars/default.png'
                )
            else:
                candidate_name = '{}, {}'.format(
                    candidate.user.last_name,
                    candidate.user.first_name
                )
                party_name = candidate.party.party_name
                avatar_url = candidate.avatar.url
            try:
                results[position]
            except KeyError:
                results[position] = list()

            results[position].append(
                CandidateResult(
                    candidate_name,
                    party_name,
                    avatar_url,
                    total_num_votes
                )
            )

            # To ensure that it is hard to figure out who the actual candidate
            # is.
            if election_state == 'open':
                random.shuffle(results[position])

        return results

    def _get_election_tab_links(self):
        ElectionTabLink = namedtuple(
            'ElectionTabLink',
            'election_id title url'
        )

        tab_links = list()
        tab_links.append(ElectionTabLink(None, 'All', reverse('results')))

        elections = Election.objects.all().order_by('name')
        for election in elections:
            tab_links.append(
                ElectionTabLink(
                    election.id,
                    election.name,
                    reverse('results') + '?election={}'.format(election.id)
                )
            )

        return tab_links

    def _get_random_candidate_name(self):
        random_names = [
            'Sven',
            'Joergen #1',
            'Joergen #2',
            'Bernie',
            'IKEA BIRD #1',
            'IKEA BIRD #2',
            'Pee pee poo poo',
            'Water Cow',
            'Mushroom Cow',
            'Water Sheep',
            'Virgin Turtle',
            'Big Brain',
            'Dinnerbone',
            'Pig Army General',
            'Pee Pee 2 Poo',
            'Brad 1',
            'Brad 2',
            'Aloona :3',
            'Boris',
            'Stephano',
            'Rolph',
            'Black Joergen'
        ]
        return random_names[random.randint(0, len(random_names) - 1)]

    def _get_random_party_name(self):
        random_names = [
            'Bro Army',
            '9 Year Old Army',
            'Gamers',
            'Church of Water Sheep',
            'Tower of Llama'
        ]
        return random_names[random.randint(0, len(random_names) - 1)]
