from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
from .models import (
    Party, County, Constituency, Ward,
    PollingCenter, PollingStation, Position,
    Candidate, Voter, Vote
)


class RemoveButtonAdminMixin:
    def remove_button(self, obj):
        delete_url = reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_delete',
            args=[obj.pk],
        )
        return format_html('<a class="button" href="{}">Remove</a>', delete_url)

    remove_button.short_description = 'Remove'


class PartyAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'remove_button')
    search_fields = ('name',)
    actions = ('delete_selected',)


class CountyAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'code', 'remove_button')
    search_fields = ('name', 'code')
    actions = ('delete_selected',)


class ConstituencyAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'county', 'code', 'remove_button')
    list_filter = ('county',)
    search_fields = ('name', 'code', 'county__name')
    actions = ('delete_selected',)


class WardAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'constituency', 'code',
                    'registered_voters_2022', 'polling_centers', 'polling_stations', 'remove_button')
    list_filter = ('constituency__county', 'constituency')
    search_fields = ('name', 'code', 'constituency__name')
    readonly_fields = ('registered_voters_2022', 'polling_centers',
                       'polling_stations', 'avg_voters_per_center', 'avg_voters_per_station')
    actions = ('delete_selected',)


class PollingCenterAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'ward', 'code',
                    'registered_voters', 'get_stations_count', 'remove_button')
    list_filter = ('ward__constituency__county', 'ward__constituency', 'ward')
    search_fields = ('name', 'code', 'ward__name')
    readonly_fields = ('registered_voters', 'get_stations_count')
    actions = ('delete_selected',)

    def get_stations_count(self, obj):
        return obj.polling_stations.count()
    get_stations_count.short_description = 'Polling Stations'


class PollingStationAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'center', 'code',
                    'registered_voters', 'remove_button')
    list_filter = ('center__ward__constituency__county',
                   'center__ward__constituency', 'center__ward', 'center')
    search_fields = ('name', 'code', 'center__name')
    readonly_fields = ('registered_voters',)
    actions = ('delete_selected',)
    list_select_related = (
        'center',
        'center__ward',
        'center__ward__constituency',
        'center__ward__constituency__county',
    )
    list_per_page = 50
    show_full_result_count = False


class PositionAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'remove_button')
    search_fields = ('name',)
    actions = ('delete_selected',)


class CandidateAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    class CandidateAdminForm(forms.ModelForm):
        county = forms.ModelChoiceField(
            queryset=County.objects.order_by('name'),
            required=False
        )
        constituency = forms.ModelChoiceField(
            queryset=Constituency.objects.select_related(
                'county').order_by('county__name', 'name'),
            required=False
        )
        ward = forms.ModelChoiceField(
            queryset=Ward.objects.select_related(
                'constituency', 'constituency__county'
            ).order_by('constituency__county__name', 'constituency__name', 'name'),
            required=False
        )

        class Meta:
            model = Candidate
            fields = '__all__'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            county_id = self.data.get('county') or getattr(
                getattr(self.instance, 'county', None), 'id', None)
            constituency_id = self.data.get('constituency') or getattr(
                getattr(self.instance, 'constituency', None), 'id', None)

            if county_id:
                self.fields['constituency'].queryset = Constituency.objects.filter(
                    county_id=county_id
                ).order_by('name')

            if constituency_id:
                self.fields['ward'].queryset = Ward.objects.filter(
                    constituency_id=constituency_id
                ).order_by('name')

        def clean(self):
            cleaned_data = super().clean()
            position = cleaned_data.get('position')
            county = cleaned_data.get('county')
            constituency = cleaned_data.get('constituency')
            ward = cleaned_data.get('ward')

            if constituency and county and constituency.county_id != county.id:
                raise ValidationError(
                    'Selected constituency does not belong to the selected county.')

            if ward and constituency and ward.constituency_id != constituency.id:
                raise ValidationError(
                    'Selected ward does not belong to the selected constituency.')

            if not position:
                return cleaned_data

            if position.name in ['GOVERNOR', 'SENATOR', 'WOMEN_REP'] and not county:
                raise ValidationError(
                    'County is required for Governor, Senator, and Women Representative candidates.')

            if position.name == 'MP':
                if not county:
                    raise ValidationError(
                        'County is required for MP candidates.')
                if not constituency:
                    raise ValidationError(
                        'Constituency is required for MP candidates.')

            if position.name == 'MCA':
                if not county:
                    raise ValidationError(
                        'County is required for MCA candidates.')
                if not constituency:
                    raise ValidationError(
                        'Constituency is required for MCA candidates.')
                if not ward:
                    raise ValidationError(
                        'Ward is required for MCA candidates.')

            return cleaned_data

    form = CandidateAdminForm
    list_display = ('first_name', 'last_name',
                    'id_number', 'party', 'position', 'remove_button')
    list_filter = ('party', 'position', 'county', 'constituency', 'ward')
    search_fields = ('first_name', 'last_name', 'id_number')
    actions = ('delete_selected',)


class VoterAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    class VoterAdminForm(forms.ModelForm):
        constituency = forms.ModelChoiceField(
            queryset=Constituency.objects.none()
        )
        ward = forms.ModelChoiceField(
            queryset=Ward.objects.none()
        )
        polling_center = forms.ModelChoiceField(
            queryset=PollingCenter.objects.none()
        )
        polling_station = forms.ModelChoiceField(
            queryset=PollingStation.objects.none()
        )

        class Meta:
            model = Voter
            fields = '__all__'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            county_id = self.data.get('county') or getattr(
                getattr(self.instance, 'county', None), 'id', None)
            constituency_id = self.data.get('constituency') or getattr(
                getattr(self.instance, 'constituency', None), 'id', None)
            ward_id = self.data.get('ward') or getattr(
                getattr(self.instance, 'ward', None), 'id', None)
            polling_center_id = self.data.get('polling_center') or getattr(
                getattr(self.instance, 'polling_center', None), 'id', None)

            if county_id:
                self.fields['constituency'].queryset = Constituency.objects.filter(
                    county_id=county_id
                ).order_by('name')

            if constituency_id:
                self.fields['ward'].queryset = Ward.objects.filter(
                    constituency_id=constituency_id
                ).order_by('name')

            if ward_id:
                self.fields['polling_center'].queryset = PollingCenter.objects.filter(
                    ward_id=ward_id
                ).order_by('name')

            if polling_center_id:
                self.fields['polling_station'].queryset = PollingStation.objects.filter(
                    center_id=polling_center_id
                ).order_by('name')

        def clean(self):
            cleaned_data = super().clean()
            county = cleaned_data.get('county')
            constituency = cleaned_data.get('constituency')
            ward = cleaned_data.get('ward')
            polling_center = cleaned_data.get('polling_center')
            polling_station = cleaned_data.get('polling_station')

            if constituency and county and constituency.county_id != county.id:
                raise ValidationError(
                    'Selected constituency does not belong to the selected county.')

            if ward and constituency and ward.constituency_id != constituency.id:
                raise ValidationError(
                    'Selected ward does not belong to the selected constituency.')

            if polling_center and ward and polling_center.ward_id != ward.id:
                raise ValidationError(
                    'Selected polling center does not belong to the selected ward.')

            if polling_station and polling_center and polling_station.center_id != polling_center.id:
                raise ValidationError(
                    'Selected polling station does not belong to the selected polling center.')

            return cleaned_data

    form = VoterAdminForm
    list_display = ('get_full_name', 'id_number',
                    'phone_number', 'county', 'is_verified', 'remove_button')
    list_filter = ('is_verified', 'county', 'constituency',
                   'ward', 'polling_center')
    search_fields = ('user__first_name', 'user__last_name',
                     'id_number', 'phone_number')
    readonly_fields = ('registration_date',)
    actions = ('delete_selected',)
    list_select_related = (
        'user',
        'county',
        'constituency',
        'ward',
        'polling_center',
        'polling_station',
    )
    list_per_page = 50
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user',
            'county',
            'constituency',
            'ward',
            'polling_center',
            'polling_station',
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('user', 'registration_date')
        return ('registration_date',)

    def get_full_name(self, obj):
        return obj.get_display_name()
    get_full_name.short_description = 'Full Name'

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['is_verified'] = True
        return initial

    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_verified = True
        super().save_model(request, obj, form, change)


class VoteAdmin(RemoveButtonAdminMixin, admin.ModelAdmin):
    list_display = ('voter', 'position', 'candidate',
                    'timestamp', 'remove_button')
    list_filter = ('position', 'candidate__party', 'timestamp')
    search_fields = ('voter__user__first_name',
                     'voter__user__last_name', 'voter__id_number')
    readonly_fields = ('voter', 'position', 'candidate', 'timestamp')
    actions = ('delete_selected',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Party, PartyAdmin)
admin.site.register(County, CountyAdmin)
admin.site.register(Constituency, ConstituencyAdmin)
admin.site.register(Ward, WardAdmin)
admin.site.register(PollingCenter, PollingCenterAdmin)
admin.site.register(PollingStation, PollingStationAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Voter, VoterAdmin)
admin.site.register(Vote, VoteAdmin)
