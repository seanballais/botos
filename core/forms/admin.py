import os

from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    UserChangeForm, UserCreationForm
)

from dal import autocomplete

from core.models import (
    User, Batch, Section, VoterProfile, Candidate, CandidateParty,
    CandidatePosition, UserType, Election
)
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
    Form for toggling between the open and close state of the election. The
    elections are closed by default.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'] = forms.ChoiceField(
            choices=[
                ('open', 'Open'),
                ('closed', 'Closed')
            ],
            widget=forms.RadioSelect,
            initial=AppSettings().get('election_state', 'closed')
        )


# The following classes are based on the code by @kdh454 from:
#    https://stackoverflow.com/a/17496836/1116098
# and on the code by @adrianoviedo from:
#    https://stackoverflow.com/a/48405520/1116098
class BaseForm(forms.ModelForm):
    class Meta:
        exclude = ('is_staff', 'is_superuser', 'is_active', 'type',)


class BaseCreateForm(BaseForm):
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise forms.ValidationError('Username already used.')


class AdminChangeForm(BaseForm, UserChangeForm):
    class Meta(BaseForm.Meta):
        model = User


class AdminCreationForm(BaseCreateForm, UserCreationForm):
    class Meta(BaseForm.Meta):
        model = User


class VoterChangeForm(BaseForm, UserChangeForm):
    class Meta(BaseForm.Meta):
        model = User


class VoterCreationForm(BaseCreateForm, UserCreationForm):
    class Meta(BaseForm.Meta):
        model = User


class CandidateForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='admin-candidate-user-autocomplete',
            forward=['election']
        )
    )
    election = forms.ModelChoiceField(
        queryset=Election.objects.all()
    )
    party = forms.ModelChoiceField(
        queryset=CandidateParty.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='admin-candidate-party-autocomplete',
            forward=['election']
        )
    )
    position = forms.ModelChoiceField(
        queryset=CandidatePosition.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='admin-candidate-position-autocomplete',
            forward=['election']
        )
    )

    class Meta:
        model = Candidate
        fields = ( '__all__' )


class CandidatePositionForm(forms.ModelForm):
    election = forms.ModelChoiceField(queryset=Election.objects.all())
    target_batches = forms.ModelMultipleChoiceField(
        queryset=Batch.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
            url='admin-election-batches-autocomplete',
            forward=['election']
        )
    )

    class Meta:
        model = CandidatePosition
        fields = ( '__all__' )

class VoterProfileInlineForm(forms.ModelForm):
    class Meta:
        model = VoterProfile
        fields = ( 'batch', 'section', )
