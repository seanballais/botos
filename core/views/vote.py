from functools import reduce
import json

from phe import paillier

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from core.decorators import login_required
from core.models import (
    User, Candidate, Vote
)
from core.utils import AppSettings


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(
    login_required(
        login_url='/',
        next=''
    ),
    name='dispatch'
)
class VoteProcessingView(View):
    """
    View that processes votes.

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
    def get(self, request):
        return redirect(reverse('index'))

    def post(self, request):
        # Improve this.
        user = self.request.user
        has_user_voted = Vote.objects.filter(user__id=user.id).exists()
        try:
            candidates_voted = request.POST['candidates_voted']
        except KeyError:
            if has_user_voted:
                messages.error(
                    request,
                    'You are no longer allowed to vote since you have voted '
                    'already. Additionally, the votes you were invalid too.'
                )
            else:
                messages.error(
                    request,
                    'The votes you sent were invalid. Please try voting again,'
                    ' and/or contact the system administrator.'
                )
        else:
            if has_user_voted:
                message.error(
                    request,
                    'You are no longer allowed to vote since you have voted '
                    'already.'
                )
            else:
                # No need for the private election key since we only need
                # to encrypt the votes. We only need the private key if we
                # need to decrypt votes.
                public_key = self._get_public_election_key()
                self._cast_votes(user, candidates_voted, public_key)

        return redirect(reverse('index'))

    def _get_public_election_key(self):
        public_election_key_str = AppSettings().get('public_election_key')
        if public_election_key_str is None:
            messages.error(
                request,
                'Election keys have not been generated yet.'
            )
        else:
            public_key_json = json.loads(public_election_key_str)

            return paillier.PaillierPublicKey(n=public_key_json.n)

    def _cast_votes(self, user, candidates_voted, public_key):
        candidates_voted = Candidate.objects.filter(
            reduce(
                lambda x, y: x | y,
                [ Q(id=candidate_id) for candidate_id in candidates_voted ]
            )
        )
        candidates = Candidate.objects.all()

        for candidate in candidates:
            vote_count = 0
            # We need to have a benchmark to confirm if calling to the database
            # to check if a candidate is part of the candidates voted takes
            # more time to perform than iterating through an evaluated list of
            # candidates voted. Right now, we're just going to do the latter
            # since there seems to be additional overhead when performing a
            # database call, and the evaluated list already acts as a cache of
            # the candidates voted.
            #
            # Note: QuerySets are lazily evaluated.
            if candidate in candidates_voted:
                vote_count = 1

            encrypted_vote = public_key.encrypt(vote_count)
            Vote.objects.create(
                user=user,
                candidate=candidate,
                vote_cipher=self._serialize_vote(encrypted_vote)
            )

    def _serialize_vote(self, encrypted_vote):
        return json.dumps({
            'ciphertext': encrypted_vote.ciphertext(),
            'exponent': encrypted_vote.exponent
        })
