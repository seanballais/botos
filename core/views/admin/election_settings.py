from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required, user_passes_test
)
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.views import View
from django.views.generic.base import TemplateView

from core.forms.admin import (
    ElectionSettingsCurrentTemplateForm, ElectionSettingsElectionStateForm
)
from core.utils import AppSettings


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ElectionSettingsIndexView(TemplateView):
    """
    This is the index view for the election settings. Only superusers are
    allowed to access this page.

    View URL: `/admin/election`
    Template: `{ current template }/admin/election.html`
    """
    _template_dir = AppSettings().get('template', 'default')
    template_name = '{}/admin/election.html'.format(_template_dir)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class CurrentTemplateView(View):
    """
    This view changes the current template being used. This will only accept
    POST requests. GET requests from superusers will result in a redirection
    to `/admin/election`, while non-superusers and anonymoous users to `/`.

    View URL: `/admin/election/template`
    """
    def get(self, request):
        return redirect('/admin/election')

    def post(self, request):
        # Only accept POST requests but we must validate first.
        form = ElectionSettingsCurrentTemplateForm(request.POST)
        if form.is_valid():
            # Okay, good data. Process the data, then send the success message.
            messages.success(request, 'Current template changed successfully.')
        else:
            # Oh no, bad data. Do not process the data, and send an error
            # message.
            messages.error(
                request,
                'Template field must not be empty nor have invalid data.'
            )

        return redirect('/admin/election')
