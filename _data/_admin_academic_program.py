from django.contrib import admin

from ._data_academic_program import Specialization, Program, Course


class SpecializationAdmin(admin.ModelAdmin):
    list_display = (
        'specialization_id', 'specialization_code', 'specialization_name', 'specialization_name_ar')
    search_fields = ('specialization_name', 'specialization_name_ar', 'specialization_code')


admin.site.register(Specialization, SpecializationAdmin)


class ProgramAdmin(admin.ModelAdmin):
    list_display = (
        'program_id', 'program_code', 'program_name', 'program_name_ar', 'program_version')
    list_filter = ('specialization',)
    search_fields = ('course_name',)


admin.site.register(Program, ProgramAdmin)


class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'course_id', 'course_level', 'course_code', 'course_code_ar', 'course_name', 'course_name_ar', 'program')
    list_filter = ('program', 'course_level')
    search_fields = ('course_code', 'course_code_ar', 'course_name', 'course_name_ar')


admin.site.register(Course, CourseAdmin)
