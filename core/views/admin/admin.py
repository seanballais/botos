from urllib.parse import urljoin

from django.contrib import messages
from django.db import models
from django.db.models.functions import (
    Cast, Concat
)
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.utils.decorators import method_decorator

from dal import autocomplete

from core.decorators import (
    login_required, user_passes_test
)

from core.models import (
    User, Batch, Election, CandidateParty, CandidatePosition,
    UserType, Vote, VoterProfile
)


class CandidateUserAutoCompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Only admins should be able to access this view.
        if (not self.request.user.is_authenticated
                or self.request.user.type == UserType.VOTER):
            return []

        qs = User.objects.filter(candidate__isnull=True)
        election = self.forwarded.get('election', None)
        if not election:
            return []
        else:
            qs = qs.filter(
                voter_profile__batch__election__id=election,
                type=UserType.VOTER
            )

        if self.q:
            qs = qs.annotate(
                name=Concat('last_name', models.Value(', '), 'first_name')
            )
            qs = qs.filter(name__istartswith=self.q)

        return qs


class CandidatePartyAutoCompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Only admins should be able to access this view.
        if (not self.request.user.is_authenticated
                or self.request.user.type == UserType.VOTER):
            return []

        qs = CandidateParty.objects.all()
        election = self.forwarded.get('election', None)
        if not election:
            return []
        else:
            qs = qs.filter(election__id=election)

        if self.q:
            qs = qs.filter(party_name__istartswith=self.q)

        return qs


class CandidatePositionAutoCompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Only admins should be able to access this view.
        if (not self.request.user.is_authenticated
                or self.request.user.type == UserType.VOTER):
            return []

        qs = CandidatePosition.objects.all()
        election = self.forwarded.get('election', None)
        if not election:
            return []
        else:
            qs = qs.filter(election__id=election)

        if self.q:
            qs = qs.filter(position_name__istartswith=self.q)

        return qs


class ElectionBatchesAutoCompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Only admins should be able to access this view.
        if (not self.request.user.is_authenticated
                or self.request.user.type == UserType.VOTER):
            return []

        qs = Batch.objects.all()
        election = self.forwarded.get('election', None)
        if not election:
            return []
        else:
            qs = qs.filter(election__id=election)

        if self.q:
            qs = qs.annotate(
                year_as_char=Cast(
                    'year', output_field=models.CharField(max_length=32)
                )
            )
            qs = qs.filter(year_as_char__istartswith=int(self.q))

        return qs


@method_decorator(csrf_protect, name='dispatch')
class ClearElectionConfirmationView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous or request.user.type == UserType.VOTER:
            index_url = urljoin(
                reverse('index'),
                '?next={}'.format(request.path)
            )
            return HttpResponseRedirect(index_url)

        # At this point, we can assume that the election ID parameter will
        # always be an integer. Django will complain if the user enters a
        # non-integer value.
        election_id = int(kwargs['election_id'])
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            messages.error(
                request,
                'Attempted to clear votes in a non-existent election.'
            )
            return HttpResponseRedirect(
                reverse('admin:core_election_changelist')
            )

        opts = Election._meta
        context = {
            'site_header': 'Botos Administration',
            'title': 'Are you sure?',
            'opts': opts,
            'election': election
        }

        template_name = 'default/admin/clear_election_action_confirmation.html'
        return TemplateResponse(
            request,
            template_name,
            context
        )

    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous or request.user.type == UserType.VOTER:
            index_url = urljoin(
                reverse('index'),
                '?next={}'.format(request.path)
            )
            return HttpResponseRedirect(index_url)

        # At this point, we can assume that the election ID parameter will
        # always be an integer. Django will complain if the user enters a
        # non-integer value.
        election_id = int(kwargs['election_id'])
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            messages.error(
                request,
                'Attempted to clear votes in a non-existent election.'
            )
            return HttpResponseRedirect(
                reverse('admin:core_election_changelist')
            )

        if 'clear_election' in request.POST:
            Vote.objects.filter(election=election).delete()
            voter_profiles = VoterProfile.objects.filter(
                batch__election=election
            )
            voter_profiles.update(has_voted=False)

            messages.success(
                request,
                'Votes in \'{}\' were cleared successfully.'.format(
                    election.name
                )
            )

        return HttpResponseRedirect(
            reverse('admin:core_election_change', args=(election_id,))
        )
