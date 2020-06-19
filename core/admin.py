from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import F

from core.forms.admin import (
    AdminChangeForm, AdminCreationForm, VoterChangeForm,
    VoterCreationForm, CandidateForm, CandidatePositionForm,
    VoterProfileInlineForm
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
        obj.is_staff = True
        obj.is_superuser = True

        super().save_model(request, obj, form, change)


class VoterProfileInline(admin.StackedInline):
    model = VoterProfile
    form = VoterProfileInlineForm

    # We gotta use this, since Django Admin (in v2.2) still uses the plural
    # verbose name of VoterProfile for some reason, despite it having a
    # one-to-one relationship with the user model.
    verbose_name_plural = 'voter profile'


class VoterAdmin(BaseUserAdmin):
    form = VoterChangeForm
    add_form = VoterCreationForm
    inlines = [ VoterProfileInline ]
    list_display = (
        'username', 'first_name', 'last_name','batch', 'section',
    )
    list_filter = (
        'voter_profile__batch', 'voter_profile__section',
    )

    def batch(self, obj):
        return obj.voter_profile.batch.year

    batch.short_description = 'Batch'
    batch.admin_order_field = 'batch'

    def section(self, obj):
        return obj.voter_profile.section.section_name

    section.short_description = 'Section'
    section.admin_order_field = 'section'

    # TODO: Fix error when sorting by batch. This error may also occur when
    #       sorting by section.

    def get_queryset(self, request):
        return self.model.objects \
                         .filter(type=UserType.VOTER) \
                         .select_related('voter_profile') \
                         .annotate(
                            batch=F('voter_profile__batch'),
                            section=F('voter_profile__section')
                          )

    def save_model(self, request, obj, form, change):
        obj.type = UserType.VOTER
        obj.is_staff = False
        obj.is_superuser = False

        super().save_model(request, obj, form, change)


class AdminUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Admin'

    def save(self, *args, **kwargs):
        self.type = UserType.ADMIN
        self.is_staff = True
        self.is_superuser = True
        super().save(*args, **kwargs)


class Voter(User):
    class Meta:
        proxy = True
        verbose_name = 'Voter'

    def save(self, *args, **kwargs):
        self.type = UserType.VOTER
        self.is_staff = False
        self.is_superuser = False
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
