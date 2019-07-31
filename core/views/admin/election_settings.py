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
from core.models import Vote
from core.utils import AppSettings


@method_decorator(
    login_required(
        login_url='/admin/login',
        next='/admin/election'
    ),
    name='dispatch',
)
@method_decorator(
    user_passes_test(
        lambda u: u.is_superuser,
        login_url='/admin/login',
        next='/admin/election'
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
        login_url='/admin/login',
        next='/admin/election'
    ),
    name='dispatch',
)
@method_decorator(
    user_passes_test(
        lambda u: u.is_superuser,
        login_url='/admin/login',
        next='/admin/election'
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
        login_url='/admin/login',
        next='/admin/election'
    ),
    name='dispatch',
)
@method_decorator(
    user_passes_test(
        lambda u: u.is_superuser,
        login_url='/admin/login',
        next='/admin/election'
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


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(
    login_required(
        login_url='/admin/login',
        next='/admin/election'
    ),
    name='dispatch',
)
@method_decorator(
    user_passes_test(
        lambda u: u.is_superuser,
        login_url='/admin/login',
        next='/admin/election'
    ),
    name='dispatch',
)
class ElectionPubPrivKeysView(View):
    """
    Calling this view will immediately invoke Botos to generate a new set of
    public and private election keys. The keys will be used to encrypt and
    decrypt votes. However, if there are votes already or the elections are
    open, then calling this view will just simply send back a message that the
    operation cannot be performed due to the aformentioned conditions.

    This will only accept POST requests. GET requests from superusers
    will result in a redirection to `/admin/election`, while non-superusers
    and anonymoous users to `/`.

    View URL: `/admin/election/keys`
    """
    def get(self, request):
        return redirect('/admin/election')

    def post(self, request):
        # No POST data will be used. So, we'll just ignore any POST data we get
        # In future revisions, we *might* decide to return an error message
        # when POST data is sent along with the request.
        election_state = AppSettings().get('election_state', 'closed')
        are_votes_present = Vote.objects.all().exists()
        if election_state == 'closed' and not are_votes_present:
            # Okay, we have the clear to generate the election keys.
            public_key, private_key = paillier.generate_paillier_keypair()

            # According to the python-paillier docs, "g will always be
            # n + 1". We can just skip serializing g, but let's still
            # serialize it for the sake of a more readable code.
            serialized_public_key = json.dumps({
                'g': public_key.g,
                'n': public_key.n
            })
            serialized_private_key = json.dumps({
                'p': private_key.p,
                'q': private_key.q
            })

            AppSettings().set('public_election_key', serialized_public_key)
            AppSettings().set('private_election_key', serialized_private_key)

            messages.success(
                request,
                'New public and private election keys generated successfully.'
            )
        else:
            # TODO: Send an error message.
            messages.error(
                request,
                'Cannot generate public and private election keys since'
                + ' elections are open or votes have already been cast.'
            )

        return redirect('/admin/election')
