from django.urls import path

from core.views.admin.election_settings import (
    CurrentTemplateView,
    ElectionSettingsIndexView
)

urlpatterns = [
    path('admin/election', ElectionSettingsIndexView.as_view()),
    path('admin/election/template', CurrentTemplateView.as_view())
]