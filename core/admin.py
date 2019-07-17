from django.contrib import admin

from core.models import (
    User, Batch, Section, Candidate, CandidateParty,
    CandidatePosition, Setting
)

admin.site.register(User)
admin.site.register(Batch)
admin.site.register(Section)
admin.site.register(Candidate)
admin.site.register(CandidateParty)
admin.site.register(CandidatePosition)
