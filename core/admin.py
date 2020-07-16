import urllib

from django import forms
from django.contrib import (
    admin, messages
)
from django.contrib.admin.utils import model_ngettext
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import F
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import (
    path, reverse
)
from django.utils.translation import ngettext

from core.forms.admin import (
    AdminChangeForm, AdminCreationForm, VoterChangeForm,
    VoterCreationForm, CandidateForm, CandidatePositionForm,
    VoterProfileInlineForm
)
from core.models import (
    User, Batch, Section, VoterProfile, Candidate, CandidateParty,
    CandidatePosition, UserType, Election, Vote
)
from core.views.admin.admin import ClearElectionConfirmationView


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


class VoterProfileInline(admin.StackedInline):
    model = VoterProfile
    form = VoterProfileInlineForm

    # We gotta use this, since Django Admin (in v2.2) still uses the plural
    # verbose name of VoterProfile for some reason, despite it having a
    # one-to-one relationship with the user model.
    verbose_name_plural = 'voter profile'


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


class AdminUserAdmin(BaseUserAdmin):
    form = AdminChangeForm
    add_form = AdminCreationForm
    list_display = ( 'username', 'first_name', 'last_name', 'email', )
    list_filter = ( 'email', )

    def get_queryset(self, request):
        return self.model.objects.filter(type=UserType.ADMIN)

    def save_model(self, request, obj, form, change):
        obj.type = UserType.ADMIN
        obj.is_staff = True
        obj.is_superuser = True

        super().save_model(request, obj, form, change)


class VoterAdmin(BaseUserAdmin):
    form = VoterChangeForm
    add_form = VoterCreationForm
    inlines = [ VoterProfileInline ]
    list_display = (
        'username', 'first_name', 'last_name', 'batch', 'section', 'election',
    )
    list_filter = (
        'voter_profile__batch__election', 'voter_profile__batch',
        'voter_profile__section',
    )

    def batch(self, obj):
        return obj.voter_profile.batch.year

    batch.short_description = 'Batch'
    batch.admin_order_field = 'batch'

    def section(self, obj):
        return obj.voter_profile.section.section_name

    section.short_description = 'Section'
    section.admin_order_field = 'section'

    def election(self, obj):
        return obj.voter_profile.batch.election.name

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


class BatchAdmin(admin.ModelAdmin):
    list_display = ( 'year', 'election', )
    list_filter = ( 'election', )


class CandidateAdmin(admin.ModelAdmin):
    form = CandidateForm
    list_display = ( 'user', 'party', 'position','election', )
    list_filter = ( 'party', 'position', 'election', )


class CandidateInline(admin.TabularInline):
    model = Candidate
    form = CandidateForm
    extra = 0


class CandidatePartyAdmin(admin.ModelAdmin):
    list_display = ( 'party_name', 'election', )
    list_filter = ( 'election', )
    inlines = [ CandidateInline ]


class CandidatePositionAdmin(admin.ModelAdmin):
    form = CandidatePositionForm
    list_display = (
        'position_name', 'position_level', 'max_num_selected_candidates',
        'election',
    )
    list_filter = (
        'position_level', 'max_num_selected_candidates', 'election',
    )


class BatchInline(admin.TabularInline):
    model = Batch
    extra = 0


class CandidatePartyInline(admin.TabularInline):
    model = CandidateParty
    extra = 0


class CandidatePositionInline(admin.TabularInline):
    model = CandidatePosition
    form = CandidatePositionForm
    extra = 0


class ElectionAdmin(admin.ModelAdmin):
    actions = [ 'clear_election' ]
    inlines = [
        BatchInline, CandidatePartyInline,
        CandidatePositionInline, CandidateInline
    ]
    change_form_template = 'default/admin/election_change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path(
                '<int:election_id>/clear_votes',
                ClearElectionConfirmationView.as_view(),
                name="core_election_clear_votes"
            )
        ]

        return urls

    def clear_election(self, request, queryset):
        # This is partially based on:
        #     https://github.com/django/django/blob/
        #             958c7b301ead79974db8edd5b9c6588a10a28ae7/
        #             django/contrib/admin/actions.py
        if request.method == 'POST' and 'clear_elections' in request.POST:
            num_elections = queryset.count()
            for election in queryset:
                Vote.objects.filter(election=election).delete()
                voter_profiles = VoterProfile.objects.filter(
                    batch__election=election
                )
                voter_profiles.update(has_voted=False)

            messages.success(
                request,
                ngettext(
                    'Votes in %d election were cleared successfully.',
                    'Votes in %d elections were cleared successfully.',
                    num_elections
                ) % num_elections
            )
        else:
            opts = Election._meta
            objects_name = model_ngettext(queryset)

            context = {
                **self.admin_site.each_context(request),
                'title': 'Are you sure?',
                'objects_name': str(objects_name),
                'queryset': queryset,
                'opts': opts,
                'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
                'media': self.media,
            }

            template_name = 'default/admin/clear_election_action.html'
            return TemplateResponse(
                request,
                template_name,
                context
            )

    clear_election.short_description = "Clear votes in selected elections"

    def render_change_form(self, request, context, *args, **kwargs):
        context.update({
            'show_save': True,
            'show_delete_link': True,
            'show_save_and_add_another': True,
            'show_save_and_continue': True
        })

        if 'add' in kwargs and kwargs['add']:
            context['show_clear_election'] = False
            context['election'] = None
        elif 'change' in kwargs and kwargs['change']:
            context['show_clear_election'] = True
            context['election'] = kwargs['obj']

        return super().render_change_form(request, context, *args, **kwargs)


admin.site.register(AdminUser, AdminUserAdmin)
admin.site.register(Voter, VoterAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Section)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(CandidateParty, CandidatePartyAdmin)
admin.site.register(CandidatePosition, CandidatePositionAdmin)
admin.site.register(Election, ElectionAdmin )
admin.site.unregister(Group)  # We don't need this at the moment.

# Customize admin texts.
admin.site.site_title = 'Botos Admin'
admin.site.site_header = 'Botos Administration'
