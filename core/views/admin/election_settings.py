import json
from phe import paillier

from django.contrib import messages
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView

from core.decorators import (
    login_required, user_passes_test
)
from core.forms.admin import (
    ElectionSettingsCurrentTemplateForm, ElectionSettingsElectionStateForm
)
from core.models import (
    Vote, UserType
)
from core.utils import AppSettings


@method_decorator(
    login_required(
        login_url='/',
        next='/admin/election'
    ),
    name='dispatch',
)
@method_decorator(
    user_passes_test(
        lambda u: u.type == UserType.ADMIN,
        login_url='/',
        next='',
        redirect_field_name=None
    ),
    name='dispatch',
)
class ElectionSettingsIndexView(TemplateView):
    """
    This is the index view for the election settings. Only superusers are
    allowed to access this page.

    View URL: `/admin/election`
    Template: `{ current template }/admin/election.html`
    """
    _template_name = AppSettings().get('template', 'default')
    template_name = '{}/admin/election.html'.format(_template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_template_form = ElectionSettingsCurrentTemplateForm()
        context['current_template_form'] = current_template_form

        current_election_state_form = ElectionSettingsElectionStateForm()
        context['current_election_state_form'] = current_election_state_form

        election_state = AppSettings().get('election_state', 'closed')
        are_votes_present = Vote.objects.all().exists()
        context['elections_genkey_button_state'] = (
            'disabled' if election_state == 'open' or are_votes_present \
                       else ''
        )

        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(
    login_required(
        login_url='/',
        next='/admin/election'
    ),
    name='dispatch',
)
@method_decorator(
    user_passes_test(
        lambda u: u.type == UserType.ADMIN,
        login_url='/',
        next='',
        redirect_field_name=None
    ),
    name='dispatch',
)
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
        # Let's validate the data we got first.
        form = ElectionSettingsCurrentTemplateForm(request.POST)
        if form.is_valid():
            # Okay, good data. Process the data, then send the success message.
            AppSettings().set('template', request.POST['template_name'])
            messages.success(request, 'Current template changed successfully.')
        else:
            # Oh no, bad data. Do not process the data, and send an error
            # message.
            messages.error(
                request,
                'Template field must not be empty nor have invalid data.'
            )

        return redirect('/admin/election')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(
    login_required(
        login_url='/',
        next='/admin/election'
    ),
    name='dispatch',
)
@method_decorator(
    user_passes_test(
        lambda u: u.type == UserType.ADMIN,
        login_url='/',
        next='',
        redirect_field_name=None
    ),
    name='dispatch',
)
class ElectionStateView(View):
    """
    This view changes the state of the election from closed to open and vice
    versa. This will only accept POST requests. GET requests from superusers
    will result in a redirection to `/admin/election`, while non-superusers
    and anonymoous users to `/`.

    View URL: `/admin/election/state`
    """
    def get(self, request):
        return redirect('/admin/election')

    def post(self, request):
        # Let's validate the data we got first.
        form = ElectionSettingsElectionStateForm(request.POST)
        if form.is_valid():
            # Okay, good data. Now, process the data, then a success message.
            AppSettings().set('election_state', request.POST['state'])
            messages.success(request, 'Election state changed successfully.')
        else:
            # Oh no, bad data! Abort mission. Do not process the data. Just
            # send an error message back.
            messages.error(
                request,
                'You attempted to change the election state with invalid data.'
            )

        return redirect('/admin/election')
