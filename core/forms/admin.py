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
        template_dir = os.path.join(settings.BASE_DIR, ('botos/templates'))
        templates = [
            tuple([ content ] * 2) for content in os.listdir(template_dir) \
                                   if os.path.isdir(content) \
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
