from django.urls import path

from core.views.admin.election_settings import (
    CurrentTemplateView,
    ElectionSettingsIndexView,
    ElectionStateView
)

urlpatterns = [
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
    )
]