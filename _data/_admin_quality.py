from django.contrib import admin

from _data._data_quality import Course_CFI, ReviewerAffectations, QualityExportFile


class Course_CFIAdmin(admin.ModelAdmin):
    list_display = (
        'course_cfi_id', 'campus', 'courseFullName', 'department', 'section',
        'teacher', 'semester')
    list_filter = ('gradeFile__semester', )
    search_fields = ('gradeFile__section_code',)


admin.site.register(Course_CFI, Course_CFIAdmin)


class ReviewerAffectationsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'reviewer',)
    list_filter = ('semester',)
    # search_fields = ('course_name',)


admin.site.register(ReviewerAffectations, ReviewerAffectationsAdmin)


class QualityExportFileAdmin(admin.ModelAdmin):
    list_display = (
        'quality_export_file_id', 'teacher', 'submission_time', 'state', 'elapsedTime', 'exec_trace', 'export_file')
    list_filter = ('semester', 'state')
    # search_fields = ('course_name',)


admin.site.register(QualityExportFile, QualityExportFileAdmin)
