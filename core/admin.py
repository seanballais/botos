from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from core.forms.admin import (
    AdminChangeForm, AdminCreationForm, VoterChangeForm,
    VoterCreationForm, CandidateForm, CandidatePositionForm
)
from core.models import (
    User, Batch, Section, VoterProfile, Candidate, CandidateParty,
    CandidatePosition, UserType, Election
)


# TODO: Add a list filter to the admin instances.
# Resource: https://medium.com/elements/
#               getting-the-most-out-of-django-admin-filters-2aecbb539c9a


class BaseUserAdmin(UserAdmin):
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
                )
            } 
        ),
    )
    list_filter = ()
    filter_horizontal = ()


class AdminUserAdmin(BaseUserAdmin):
    form = AdminChangeForm
    add_form = AdminCreationForm
    list_display = ('username', 'first_name', 'last_name',)

    def get_queryset(self, request):
        return self.model.objects.filter(type=UserType.ADMIN)

    def save_model(self, request, obj, form, change):
        obj.type = UserType.ADMIN

        super().save_model(request, obj, form, change)


class VoterProfileInline(admin.StackedInline):
    model = VoterProfile


class VoterAdmin(BaseUserAdmin):
    form = VoterChangeForm
    add_form = VoterCreationForm
    inlines = [ VoterProfileInline ]
    list_display = ('username', 'first_name', 'last_name',)

    def get_queryset(self, request):
        return self.model.objects.filter(type=UserType.VOTER)

    def save_model(self, request, obj, form, change):
        obj.type = UserType.VOTER

        super().save_model(request, obj, form, change)


class AdminUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Admin'

    def save(self, *args, **kwargs):
        self.type = UserType.ADMIN
        super().save(*args, **kwargs)


class Voter(User):
    class Meta:
        proxy = True
        verbose_name = 'Voter'

    def save(self, *args, **kwargs):
        self.type = UserType.VOTER
        super().save(*args, **kwargs)


class CandidateAdmin(admin.ModelAdmin):
    form = CandidateForm


class CandidatePositionAdmin(admin.ModelAdmin):
    form = CandidatePositionForm


admin.site.register(AdminUser, AdminUserAdmin)
admin.site.register(Voter, VoterAdmin)
admin.site.register(Batch)
admin.site.register(Section)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(CandidateParty)
admin.site.register(CandidatePosition, CandidatePositionAdmin)
admin.site.register(Election)
admin.site.unregister(Group)  # We don't need this at the moment.
