from core.utils import AppSettings


def get_template(request):
    return { 'template': AppSettings().get('template', 'default') }
