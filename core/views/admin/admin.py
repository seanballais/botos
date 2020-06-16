from django.db import models
from django.db.models.functions import (
    Cast, Concat
)

from dal import autocomplete

from core.decorators import (
    login_required, user_passes_test
)

from core.models import (
    User, Batch, CandidateParty, CandidatePosition, UserType
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
