from django.urls import path

from core.views.admin.election_settings import (
    CurrentTemplateView,
    ElectionPubPrivKeysView,
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
        'admin/election/keys',
        ElectionPubPrivKeysView.as_view(),
        name='admin-election-keys'
    )
]