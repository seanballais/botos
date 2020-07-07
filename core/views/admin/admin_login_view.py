from django.shortcuts import redirect
from django.urls import reverse
from django.views import View


class AdminLoginView(View):
    """
    View that redirects `/admin/login/` to the custom login view.

    View URL: `/admin/login/`
    """
    def get(self, request, *args, **kwargs):
        next_url = request.GET.get('next', None)
        if next_url:
            return redirect('{}?next={}'.format(reverse('index'), next_url))
        else:
            return redirect(reverse('index'))

