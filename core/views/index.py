from collections import OrderedDict

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import TemplateView

from core.models import (
    Candidate, Vote
)
from core.utils import AppSettings


class IndexView(TemplateView):
    """
    The view for the index page. This view is subdivided into three sub-views:
    (1) login, (2) voting, and (3) voted. There is only one subview that is
    rendered at a time. The decision on which subview is to be rendered is
    based on whether the user has logged in our not and whether the user has
    voted alreaedy or not.

    Login Sub-View
        This subview will only appear to anonymous users. Logged-in users will
        be shown either the voting subview or the voted subview.

    Voting Sub-View
        This subview will only appear to logged-in users that have not yet
        voted. If they have already voted, they will be shown the voted
        subview. Anonymous users will be shown the login subview.

    Voted Sub-View
        This subview will only appear to logged-in users that have voted
        already. If they have not yet voted, they will be shown the voting
        subview. Anonymous users will be shown the login subview.
    """
    _template_name = AppSettings().get('template', default='default')
    template_name = '{}/index.html'.format(_template_name)

    def post(self, request):
        return redirect(reverse('index'))

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        if user.is_authenticated:
            # Show either the Voting or Voted sub-view.
            has_user_voted = user.voter_profile.has_voted
            if has_user_voted:
                context['subview'] = 'voted'
                # Remember to show the voter's vote ID in later revisions. This
                # is for the public bulletin board of vote IDs.
            else:
                context['subview'] = 'voting'

                election = user.voter_profile.batch.election
                batch = user.voter_profile.batch

                # Note: The desired ordering of candidates has already been
                #       defined in the ordering option Candidate's Meta class.
                #       So, no need to specify the ordering here.
                candidates = Candidate.objects.filter(
                    election__id=election.id
                )
                # TODO: Refactor this to use queries instead of looping through
                #       the candidate list.
                candidates_by_position = OrderedDict()
                for candidate in candidates:
                    position = candidate.position
                    if (position.target_batches.exists()
                            and batch not in position.target_batches.all()):
                        # The voter cannot vote for candidates running for this
                        # position.
                        continue

                    position_name = candidate.position.position_name
                    if position_name in candidates_by_position:
                        item = candidates_by_position[position_name]
                        item["candidates"].append(candidate)
                    else:
                        candidates_by_position[position_name] = {
                            "candidates": [ candidate ],
                            "max_num_selected_candidates": (
                                position.max_num_selected_candidates
                            )
                        }

                context['candidates'] = candidates_by_position
        else:
            context['subview'] = 'login'

        return context
