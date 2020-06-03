from dal import autocomplete

from core.models import (
    CandidateParty, CandidatePosition, UserType
)


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
