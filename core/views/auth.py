import os

from django.contrib import messages
from django.contrib.auth import (
    authenticate, login, logout
)
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from core.decorators import (
    login_required, user_passes_test
)
from core.models import (
    User, UserType
)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(
    user_passes_test(
        lambda u: u.is_anonymous,
        login_url='/',  # This should probably be redirect_url.
        next='',
        redirect_field_name=None
    ),
    name='dispatch'
)
class LoginView(View):
    """
    View for logging users in.

    This view should only accept POST requests from anonymous users. GET
    requests and logged in users will be redirected to `/`. After logging in,
    users will be redirected to `/`.

    View URL: `/auth/login`
    """
    def get(self, request):
        return redirect(reverse('index'))

    def post(self, request):
        next_url = None
        try:
            username = request.POST['username']
            password = request.POST['password']
            next_url = request.POST.get('next', None)
        except KeyError:
            messages.error(
                request,
                'Invalid data submitted for authentication.'
            )
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if (user.type == UserType.VOTER
                        and not hasattr(user, 'voter_profile')):
                    messages.error(
                        request,
                        'Voter account is incompletely configured. Please '
                        'contact the system administrator.'
                    )
                else:
                    # Login success! Yey!
                    login(request, user)
                    return redirect(next_url or reverse('index'))
            else:
                messages.error(
                    request,
                    'Wrong username/password combination.'
                )

        if next_url:
            return redirect('{}?next={}'.format(reverse('index'), next_url))
        else:
            return redirect(reverse('index'))


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(
    login_required(
        login_url='/',
        next='',
        redirect_field_name=None
    ),
    name='dispatch',
)
class LogoutView(View):
    """
    View for logging users out.

    This view should only accept POST requests from logged in users. GET
    requests and anonymous users will be immediately redirected to `/`. After
    logging out, users will be redirected to `/`.

    Logout views must not accept GET requests because:
       1) It can be abused and have the user unknowingly get logged out of
          their session, which can be done by setting an image tag's src to the
          logout URL of a website, for example [1].
       2) Browsers pre-fetch websites that they think you will visit next. This
          pre-fetching may cause you to logout from the website you're
          currently visiting [2].

       References:
        [1] https://stackoverflow.com/a/3522013/1116098
        [2] https://stackoverflow.com/a/14587231/1116098

    View URL: `/auth/logout`
    """
    def get(self, request):
        return redirect(reverse('index'))

    def post(self, request):
        logout(request)

        messages.success(request, 'Logged out successfully.')

        return redirect(reverse('index'))
