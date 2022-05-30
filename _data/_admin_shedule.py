from django.contrib import admin
from django import forms
from django.contrib.auth.models import User

from _data._data_schedule import Meeting, Campus


class UserCustomField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.last_name}  ({obj.first_name})'


class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        'meeting_id', 'semester',  'course', 'section', 'campus', 'department', 'teacher')
    list_filter = ('semester', 'campus', 'department')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'teacher':
            return UserCustomField(queryset=User.objects.all().order_by('last_name'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Meeting, MeetingAdmin)


class CampusAdmin(admin.ModelAdmin):
    list_display = (
        'campus_id', 'campus_name', 'campus_name_ar')


admin.site.register(Campus, CampusAdmin)
