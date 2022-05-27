# -*- coding: utf-8 -*-

from django.contrib import admin
from import_export.admin import ImportExportMixin
from django.contrib.auth.models import User

from ._data_periods import AcademicYear
from ._data_periods import Semester


class AcademicYearAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('academic_year_name', "academic_year_date_start", 'academic_year_date_end', 'is_actual')
    # list_filter = ('academic_year_name',)
    search_fields = ('academic_year_name',)

    def is_actual(self, object_):
        return object_.isActualAcademicYear

    is_actual.short_description = u'Actual Academic Year'
    is_actual.boolean = True


admin.site.register(AcademicYear, AcademicYearAdmin)


class SemesterAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        'semester_name', 'semester_academic_year', 'semester_date_start', 'semester_date_end', 'is_actual',
        'semester_isInUse')
    list_filter = ('semester_academic_year__academic_year_name', 'semester_name',)
    search_fields = ('semester_academic_year__academic_year_name', 'semester_name',)

    def is_actual(self, object_):
        return object_.isActualSemester

    is_actual.short_description = u'Actual Semester'
    is_actual.boolean = True

    def Make_Semester_In_Use(self, request, queryset):
        for __semester in Semester.objects.all():
            if __semester.semester_isInUse:
                print(__semester.semester_name + "----> to false")
                __semester.semester_isInUse = False
                __semester.save()

        for __semester in queryset:
            print(__semester.semester_name + "----> to true")
            __semester.semester_isInUse = True
            __semester.save()
            break  # only the first one

        from django.contrib import messages
        messages.info(request, 'A new Semester in use is selected ')

    Make_Semester_In_Use.short_description = 'Make a semester as In use'

    actions = [Make_Semester_In_Use, ]


admin.site.register(Semester, SemesterAdmin)
