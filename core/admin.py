from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import (
    UserChangeForm, UserCreationForm
)
from django.contrib.auth.models import Group
from django import forms

from core.models import (
    User, Batch, Section, Candidate, CandidateParty, CandidatePosition
)


# The following classes are based on the code by @kdh454 from:
#    https://stackoverflow.com/a/17496836/1116098
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise forms.ValidationError('Username already used.')


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = (
        (
            None,
            { 
                'fields': (
                    'username',
                    'password',
                    'first_name',
                    'last_name',
                    'email',
                    'batch',
                    'section',
                )
            } 
        ),
    )
    add_fieldsets = (
        (
            None,
            { 
                'fields': (
                    'username',
                    'password1',
                    'password2',
                    'first_name',
                    'last_name',
                    'email',
                    'batch',
                    'section',
                )
            } 
        ),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Batch)
admin.site.register(Section)
admin.site.register(Candidate)
admin.site.register(CandidateParty)
admin.site.register(CandidatePosition)
admin.site.unregister(Group)  # We don't need this at the moment.
