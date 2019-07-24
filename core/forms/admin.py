import os

from django import forms
from django.conf import settings

from core.utils import AppSettings


class ElectionSettingsCurrentTemplateForm(forms.Form):
    """
    Form for the current template setting.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the list of templates.
        # The admin folder in the templates is not intended to be a template.
        # Rather, it stores the static files of Django Admin. As such, we must
        # skip it. This must be done since the admin static files must be
        # stored inside `botos/templates`, sincee STATIC_ROOT points to that
        # directory.
        template_dir = os.path.join(settings.BASE_DIR, 'botos/templates')
        templates = [
            tuple([ content ] * 2) for content in os.listdir(template_dir) \
                                   if os.path.isdir(
                                          os.path.join(template_dir, content)
                                      ) \
                                      and content != 'admin'
        ]

        self.fields['template_name'] = forms.ChoiceField(
            choices=templates,
            initial=AppSettings().get('template', 'default')
        )


class ElectionSettingsElectionStateForm(forms.Form):
    """
    Form for toggling between the open and close state of the election.
    """
    state = forms.ChoiceField(
        choices=[
            ('open', 'Open'),
            ('closed', 'Closed')
        ],
        widget=forms.RadioSelect
    )
