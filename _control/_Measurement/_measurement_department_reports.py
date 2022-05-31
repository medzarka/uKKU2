# -*- coding: utf-8 -*-
import os
import statistics
import sys
import tempfile
import json

from django.contrib.auth.models import User, Group
from django.conf import settings

from _control.AbstractPage import Abstract_UI_Page
from _control._Measurement.Measurement_FS import Measurement_FS
from _control._Measurement.Measurement_tools import Section_Measurment, Course_Measurment, Department_Measurment, \
    MEASUREMENT_Common
from _data._data_measurement import GradesFile, ReportState, Department, DepartmentFile
from _data._data_periods import Semester
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_text_element, UI_TEXT_COLOR_Enum, UI_TEXT_BG_Enum, \
    UI_Text_BADGE_Type, UI_TEXT_ALIGNMENT_Enum, UI_Text_Alert_Type, UI_TEXT_HEADING_Enum, ui_list_element, \
    ui_table_element, UI_Row_Cell_Class_Enum, table_row, table_cell, UI_IMAGE_ALIGNMENT_Enum, ui_image_element

from _web.UI.UI_FORM_Element import ui_form_block, form_field, FormInputTypeEnum, ButtonClassEnum


class _page_generate_department_reports(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Measurement :: Department Reports', link=link,
                         request_obj=request)

    def statWork_dep(self, departmentObj, semesterObj):
        __department_name = departmentObj.department_name
        __department_id = departmentObj.department_id

        _doc_filename = os.path.join(settings.DATA_DIR, 'media/', Measurement_FS.REPORTS.value,
                                     'Department_report_' + str(__department_name) + '.docx')

        ___courses = []
        ___files = []
        for _report in GradesFile.objects.filter(semester=semesterObj):

            if _report.course_code not in ___courses:
                ___courses.append(_report.course_name)

        print('Working with department ' + __department_name)
        _means = {}
        _grades = {}
        ___compuses = []
        _nbr_courses = 0
        for _course in ___courses:

            # print('\tWorking with the course ' + _course)
            __reports_for_course = GradesFile.objects.filter(semester=semesterObj,
                                                             section_department=departmentObj, course_name=_course)
            for _report in __reports_for_course:
                if _report.campus_name not in ___compuses:
                    ___compuses.append(_report.campus_name)

            _tool = Course_Measurment(_grades_files_objs=__reports_for_course, course_name=_course,
                                      course_file_obj=_course,
                                      department=__department_name)

            fused_grades, _ = _tool.extractGrades()
            if len(fused_grades['totals']) > 0:
                _means[_course] = float("{0:.4f}".format(statistics.mean(fused_grades['totals'])))
                _grades[_course] = fused_grades['totals']
                _nbr_courses += 1

        _campuses_str = ''
        for _campus in ___compuses:
            if _campuses_str == '':
                _campuses_str += _campus
            else:
                _campuses_str += ', ' + _campus

        __tool2 = Department_Measurment(_grades, _means)
        _stat = __tool2.compute_statistics()
        _stat['department'] = __department_name
        _stat['campus'] = _campuses_str
        _stat['nbr_courses'] = str(_nbr_courses)
        __tool3 = MEASUREMENT_Common()
        __tool3.generate_department_docx_report(_stat, '', _doc_filename)
        return _stat, _grades, _means

    def CreateBlocks(self, _blocks_list=None):
        _actual_semester = Semester.objects.get(semester_id=self.request_obj.session['selected_semester'])
        _actual_user = User.objects.get(id=self.request_obj.user.id)
        _tool2 = MEASUREMENT_Common()
        res = []

        permission = False
        _admin_group_name = 'MEASUREMENT'

        try:
            _permission_group = Group.objects.get(name=_admin_group_name)
            if _permission_group in _actual_user.groups.all():
                permission = True
        except Group.DoesNotExist:
            pass

        if permission:

            ###################################################################################
            ###################################################################################
            ###################################################################################
            ###################################################################################
            ###################################################################################
            ###################################################################################

            _do_analysis_update = False
            _do_measurement = False

            if self.request_obj.method == 'POST' and 'action' in self.request_obj.POST:

                if self.request_obj.POST['action'] == 'update_measurement':
                    _do_measurement = True

                if self.request_obj.POST['action'] == 'update_analysis':
                    try:
                        _department_report = DepartmentFile.objects.get(
                            department_file_id=int(self.request_obj.POST['id']))
                        _department_report.teacher_analysis = self.request_obj.POST['analysis']
                        _department_report.save()

                        _ui_basic_block = ui_basic_block(block_title='Analysis Update')
                        _text1 = ui_text_element(
                            text=f'The analysis was updated for the department report with id {self.request_obj.POST["id"]}.',
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS,
                            background=UI_TEXT_BG_Enum.NONE,
                            heading=UI_TEXT_HEADING_Enum.H4)

                        _ui_basic_block.addBasicElement(_text1)
                        _do_analysis_update = True


                    except:

                        _ui_basic_block = ui_basic_block(block_title='Analysis Update')
                        _text1 = ui_text_element(
                            text=f'An error was occurred to update the analysis of the document with id {self.request_obj.POST["id"]}.',
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                            background=UI_TEXT_BG_Enum.NONE,
                            heading=UI_TEXT_HEADING_Enum.H4)

                        _ui_basic_block.addBasicElement(_text1)

            ## display the information

            _ui_form_block = ui_form_block(
                block_title=f'Update Department Statistical measurement (It consumes CPU and Memory).',
                form_action=self.link, form_id='update_data', form_method='POST')

            _action = form_field('action', 'action', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                 input_value='update_measurement', is_required=True)
            _submit_field = form_field('Compute Measurement for Department', 'Compute Measurement for Department',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_WARNING)
            _ui_form_block.addFormField(_action)
            _ui_form_block.addFormField(_submit_field)
            res.append(_ui_form_block)

            _departments = Department.objects.all()
            for _department in _departments:
                _stats_page = ui_basic_block(block_title=_department.department_name + '  ::  Statistic Results')
                _steps = []
                try:

                    try:
                        _department_report = DepartmentFile.objects.get(department=_department,
                                                                        semester=_actual_semester)
                        _the_analysis = _department_report.teacher_analysis
                    except DepartmentFile.DoesNotExist:
                        _department_report = DepartmentFile()
                        _department_report.semester = _actual_semester
                        _department_report.department = _department
                        _department_report.save()
                        _do_measurement = True
                        _the_analysis = ''

                    if _do_measurement:
                        _stats, _grades, _means = self.statWork_dep(_department, _actual_semester)
                        filename = Department_Measurment(_grades, _means, _stats).generate_report(
                            _department_report.department_file_id, analysis=_the_analysis)

                        year_txt = _actual_semester.semester_academic_year.academic_year_name
                        term_txt = _actual_semester.semester_name

                        _department_report.report_file.save(
                            f'{_department_report.department.department_name}__{year_txt}__{term_txt}.docx',
                            open(filename, 'rb'))

                        temp1 = tempfile.NamedTemporaryFile(prefix="measurement_histogram_", suffix=".png")
                        temp2 = tempfile.NamedTemporaryFile(prefix="measurement_histogram_", suffix=".png")

                        low_file, high_file = _tool2.generate_low_high_images(_stats, temp1, temp2)
                        _department_report.stat_histogram_low.save(
                            'department_low_hostogram' + str(_department_report.department_file_id) + '.png',
                            open(low_file.name, 'rb'))

                        _department_report.stat_histogram_high.save(
                            'department_high_hostogram' + str(_department_report.department_file_id) + '.png',
                            open(high_file.name, 'rb'))
                        _department_report.number_of_courses = f'{_stats["nbr_courses"]}'
                        _department_report.stat_anova_value = f'{_stats["annova_value"]}'
                        _department_report.stat_anova_sig = f'{_stats["annova_sig"]}'
                        _department_report.stat_eta_value = f'{_stats["eta"]}'
                        _department_report.stat_eta_sig = f'{_stats["eta_sig"]}'
                        _department_report.teacher_analysis = _the_analysis
                        _department_report.means_high = json.dumps(_stats['high_means'])
                        _department_report.means_low = json.dumps(_stats['low_means'])

                        _department_report.save()

                        __nbr_courses = _stats['nbr_courses']
                        __low_means_courses = _stats['low_means']
                        __High_means_courses = _stats['high_means']
                        __annova_val = _stats['annova_value']
                        __annova_sig = _stats['annova_sig']
                        __eta_val = _stats['eta']
                        __eta_sig = _stats['eta_sig']
                        __analysis = _department_report.teacher_analysis
                    else:
                        _department_report = DepartmentFile.objects.get(department=_department,
                                                                        semester=_actual_semester)
                        __nbr_courses = _department_report.number_of_courses
                        __low_means_courses = json.loads(_department_report.means_low)
                        __High_means_courses = json.loads(_department_report.means_high)
                        __annova_val = _department_report.stat_anova_value
                        __annova_sig = _department_report.stat_anova_sig
                        __eta_val = _department_report.stat_eta_value
                        __eta_sig = _department_report.stat_eta_sig
                        __analysis = _department_report.teacher_analysis

                    _highList = []
                    _lowList = []

                    for _key, value in __low_means_courses.items():
                        _lowList.append(ui_text_element(
                            text=_key + ' \t \t \t' + str(value),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))

                    for _key, value in __High_means_courses.items():
                        _highList.append(ui_text_element(
                            text=_key + ' \t \t \t ' + str(value),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))

                    _Hlist = ui_list_element(_highList, ordered=True)
                    _Llist = ui_list_element(_lowList, ordered=True)

                    _steps.append(ui_text_element(
                        text='Annova (value): \t ' + str(__annova_val),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Annova (Sig.):\t' + str(__annova_sig),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Eta Test (value): \t' + str(__eta_val),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Eta Test (Sig.) : \t' + str(__eta_sig),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))

                    _steps.append(ui_text_element(
                        text='Number of courses : \t' + str(__nbr_courses),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))

                    _steps.append(ui_text_element(
                        text='Generated report', link_url=_department_report.report_file.url,
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))

                    _steps.append(ui_text_element(
                        text='Courses with Low Scores Inflation:',
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DANGER))
                    _steps.append(_Llist)

                    _h1 = ui_text_element(
                        text='Low Scores Inflation Histogram',
                        alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                        color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS)
                    _steps.append(_h1)

                    _hist = ui_image_element(image_url=_department_report.stat_histogram_low.url,
                                             image_alt='Low Scores Inflation Histogram',
                                             image_width='500', image_height='500',
                                             image_alignment=UI_IMAGE_ALIGNMENT_Enum.MIDDLE)
                    _steps.append(_hist)

                    _steps.append(ui_text_element(
                        text='Courses with High Scores Inflation:',
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DANGER))
                    _steps.append(_Hlist)
                    _h1 = ui_text_element(
                        text='High Scores Inflation Histogram',
                        alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                        color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS)
                    _steps.append(_h1)

                    _hist = ui_image_element(image_url=_department_report.stat_histogram_high.url,
                                             image_alt='High Scores Inflation Histogram',
                                             image_width='500', image_height='500',
                                             image_alignment=UI_IMAGE_ALIGNMENT_Enum.MIDDLE)
                    _steps.append(_hist)

                    _ui_form_block = ui_form_block(
                        block_title=f'{_department_report.department.department_name} HOD Analysis',
                        form_action=self.link, form_id='test', form_method='POST')

                    try:
                        _analysis = form_field('Analysis', 'analysis', input_type=FormInputTypeEnum.TEXTAREA_INPUT,
                                               input_value=_the_analysis, size=100,
                                               maxlength=2048,
                                               placeholder='Type here your analysis',
                                               is_required=True, is_readonly=False, isArabic=True)
                    except:
                        _analysis = form_field('Analysis', 'analysis', input_type=FormInputTypeEnum.TEXTAREA_INPUT,
                                               input_value="", size=100,
                                               maxlength=2048,
                                               placeholder='Type here your analysis',
                                               is_required=True, is_readonly=False, isArabic=True)

                    _doc_id = form_field('id', 'id', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                         input_value=str(_department_report.department_file_id), is_required=True)
                    _action = form_field('action', 'action', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                         input_value='update_analysis', is_required=True)

                    _submit_field = form_field('Save Analysis', 'Save Analysis',
                                               input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                               button_class=ButtonClassEnum.BTN_SUCCESS)
                    _cancel_field = form_field('Reset', 'Reset',
                                               input_type=FormInputTypeEnum.RESET_INPUT,
                                               button_class=ButtonClassEnum.BTN_SECONDARY)

                    _ui_form_block.addFormField(_analysis)
                    _ui_form_block.addFormField(_doc_id)
                    _ui_form_block.addFormField(_action)
                    _ui_form_block.addFormField(_submit_field)
                    _ui_form_block.addFormField(_cancel_field)

                    res.append(_ui_form_block)





                except Exception as e:
                    _steps.append(ui_text_element(
                        text='error : \t' + str(sys.exc_info()),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DANGER))

                _list = ui_list_element(_steps, ordered=False)
                _stats_page.addBasicElement(_list)
                res.append(_stats_page)


        else:

            ###################################################################################
            ###################################################################################
            ###################################################################################
            ###################################################################################
            #################

            _ui_basic_block = ui_basic_block(block_title='Access Denied')
            _text1 = ui_text_element(
                text='The actual page is only for Measurement and Evaluation Stuff.',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                background=UI_TEXT_BG_Enum.NONE,
                heading=UI_TEXT_HEADING_Enum.H4)

            _ui_basic_block.addBasicElement(_text1)

            res.append(_ui_basic_block)

        return res
