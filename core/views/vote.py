from functools import reduce
import json

from phe import paillier

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from core.decorators import login_required
from core.models import (
    User, Candidate, Vote
)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(
    login_required(
        login_url='/',
        next='',
        redirect_field_name=None
    ),
    name='dispatch',
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
            # `candidates_voted` is expected to be a JSON-stringified array.
            candidates_voted = json.loads(request.POST['candidates_voted'])
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
                messages.error(
                    request,
                    'You are no longer allowed to vote since you have voted '
                    'already.'
                )
            else:
                if type(candidates_voted) is list:
                    try:
                        self._cast_votes(user, candidates_voted)
                    except ValueError:
                        messages.error(
                            request,
                            'The votes you sent were invalid. Please try '
                            'voting again, and/or contact the system '
                            'administrator.'
                        )
                else:
                    messages.error(
                        request,
                        'The votes you sent were invalid. Please try voting '
                        'again, and/or contact the system administrator.'
                    )

        return redirect(reverse('index'))

    def _cast_votes(self, user, candidates_voted):
        # Ensure that there are no duplicate candidates.
        encountered_candidate_ids = set()
        voted_candidates = list()
        for candidate_id in candidates_voted:
            # Check that there are no duplicate votes and that the candidate
            # IDs passed exist.
            if candidate_id not in encountered_candidate_ids:
                encountered_candidate_ids.add(candidate_id)

                try:
                    candidate = Candidate.objects.get(id=candidate_id)
                except Candidate.DoesNotExist:
                    raise ValueError('Voted candidate does not exist.')
                else:
                    voted_candidates.append(candidate)
            else:
                raise ValueError('Duplicate candidates IDs submitted.')

        # Alright, things have gone well.
        for candidate in voted_candidates:
            Vote.objects.create(user=user, candidate=candidate)
