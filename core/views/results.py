from collections import (
    namedtuple, OrderedDict
)
import datetime
import json
import random

from phe import paillier

from django.conf import settings
from django.contrib import messages
from django.utils.timezone import utc
from django.views.generic.base import TemplateView

from core.models import (
    User, Candidate, Vote
)
from core.utils import AppSettings


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = self._get_vote_results()
        context['current_time'] = datetime    \
                                    .datetime \
                                    .utcnow() \
                                    .replace(tzinfo=utc)
        context['total_voters'] = User.objects.count()
        context['election_state'] = AppSettings().get(
            'election_state',
            'closed'
        )

        return context

    def _get_vote_results(self):
        election_state = AppSettings().get('election_state', 'closed')
        CandidateResult = namedtuple(
            'CandidateResult',
            'name party_name avatar_url total_votes'
        )

        results = OrderedDict()
        public_key = self._get_public_election_key()
        private_key = self._get_private_election_key()
        candidates = Candidate.objects.all()
        for candidate in candidates:
            votes = Vote.objects.filter(candidate=candidate)
            total_encrypted_votes = public_key.encrypt(0)
            for vote in votes:
                total_encrypted_votes += self._create_encrypted_vote_object(
                    public_key,
                    vote
                )
            total_votes = private_key.decrypt(total_encrypted_votes)

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
                    total_votes
                )
            )

            # To ensure that it is hard to figure out who the actual candidate
            # is.
            if election_state == 'open':
                random.shuffle(results[position])

        return results

    def _create_encrypted_vote_object(self, public_key, vote):
        if type(vote.vote_cipher) is str:
            vote_cipher_data = json.loads(vote.vote_cipher)
        else:
            # Just copy the JSON to another variable to make things cleaner, 
            # more consistent, and with fewer duplicate code.
            vote_cipher_data = vote.vote_cipher
        vote_cipher = vote_cipher_data['ciphertext']
        vote_cipher_exponent = vote_cipher_data['exponent']

        encrypted_vote = paillier.EncryptedNumber(
            public_key,
            ciphertext=vote_cipher,
            exponent=vote_cipher_exponent
        )

        return encrypted_vote

    def _get_private_election_key(self):
        private_election_key_str = AppSettings().get('private_election_key')
        if private_election_key_str is None:
            messages.error(
                self.request,
                'Private election key has not been generated yet.'
            )
        else:
            private_key_json = json.loads(private_election_key_str)
            public_key = self._get_public_election_key()

            return paillier.PaillierPrivateKey(
                public_key,
                p=private_key_json['p'],
                q=private_key_json['q']
            )

    def _get_public_election_key(self):
        public_election_key_str = AppSettings().get('public_election_key')
        if public_election_key_str is None:
            messages.error(
                self.request,
                'Election keys have not been generated yet.'
            )
        else:
            public_key_json = json.loads(public_election_key_str)

            return paillier.PaillierPublicKey(n=public_key_json['n'])

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
