from django.contrib import admin

from _control._Measurement.Measurement_tools import Section_Measurment
from _data._data_measurement import GradesFile, CourseFile, Department, DepartmentFile, MeasurementReviewerAffectations, \
    MeasurementExportFile


class GradesFileAdmin(admin.ModelAdmin):
    list_display = ('grades_file_id', 'campus_name', 'section_code', 'course_name', 'course_code', 'section_courseObj',
                    'submission_time')
    list_filter = ('submission_time', 'campus_name', 'section_department', 'semester')
    search_fields = ('course_name',)

    def make_published(self, request, queryset):
        _list = GradesFile.objects.all()
        _counter = 0
        for _section_report in _list:
            _tool = Section_Measurment(report_obj=_section_report)
            if _section_report.teacher_analysis == None or _section_report.teacher_analysis == '':
                print('Analysis missing for the section ' + str(_section_report.section_code))
                _section_report.teacher_analysis = _section_report.stat_analysis
                _section_report.save()
            if _tool.generate_report():
                # _course_report.report_state = ReportState.SUBMITTED.value
                _section_report.save()
                _counter += 1
                print('Report update for the section ' + str(_section_report.section_code))
            else:
                print('Error for the report of the section ' + str(_section_report.section_code))
        print('####' + str(_counter) + ' reports were updated.')

    make_published.short_description = "Re-generate reports"
    actions = [make_published, ]


admin.site.register(GradesFile, GradesFileAdmin)


class CourseFileAdmin(admin.ModelAdmin):
    list_display = ('campus_name', 'section_codes', 'course_name', 'course_code', 'submission_time')
    list_filter = ('submission_time', 'course_name', 'campus_name', 'course_department', 'semester')
    search_fields = ('course_name',)


admin.site.register(CourseFile, CourseFileAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_id', 'department_name',)
    search_fields = ('department_name',)


admin.site.register(Department, DepartmentAdmin)


class DepartmentFileAdmin(admin.ModelAdmin):
    list_display = ('department', 'semester',)
    search_fields = ('department',)
    list_filter = ('semester',)


admin.site.register(DepartmentFile, DepartmentFileAdmin)


class MeasurementReviewerAffectationsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'reviewer',)
    list_filter = ('semester',)
    # search_fields = ('course_name',)


admin.site.register(MeasurementReviewerAffectations, MeasurementReviewerAffectationsAdmin)


class MeasurementExportFileAdmin(admin.ModelAdmin):
    list_display = ('measurement_export_file_id', 'teacher', 'submission_time', 'state', 'elapsedTime')
    list_filter = ('semester', 'state')
    # search_fields = ('course_name',)


admin.site.register(MeasurementExportFile, MeasurementExportFileAdmin)
