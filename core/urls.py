from django.urls import path

from core.views.admin.admin import (
    CandidatePartyAutoCompleteView,
    CandidatePositionAutoCompleteView,
    ElectionBatchesAutoCompleteView
)
from core.views.admin.election_settings import (
    CurrentTemplateView,
    ElectionSettingsIndexView,
    ElectionStateView
)
from core.views.auth import (
    LoginView, LogoutView
)
from core.views.index import IndexView
from core.views.results import ResultsView
from core.views.vote import VoteProcessingView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('vote', VoteProcessingView.as_view(), name='vote-processing'),
    path('results', ResultsView.as_view(), name='results'),
    path('auth/login', LoginView.as_view(), name='auth-login'),
    path('auth/logout', LogoutView.as_view(), name='auth-logout'),
    path(
        'admin/election',
        ElectionSettingsIndexView.as_view(),
        name='admin-election-index'
    ),
    path(
        'admin/election/template',
        CurrentTemplateView.as_view(),
        name='admin-election-template'
    ),
    path(
        'admin/election/state',
        ElectionStateView.as_view(),
        name='admin-election-state'
    ),
    path(
        'admin/autocomplete/candidate-party',
        CandidatePartyAutoCompleteView.as_view(),
        name='admin-candidate-party-autocomplete'
    ),
    path(
        'admin/autocomplete/candidate-position',
        CandidatePositionAutoCompleteView.as_view(),
        name='admin-candidate-position-autocomplete'
    ),
    path(
        'admin/autocomplete/election-batches',
        ElectionBatchesAutoCompleteView.as_view(),
        name='admin-election-batches-autocomplete'
    )
]