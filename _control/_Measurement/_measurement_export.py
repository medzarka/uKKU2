# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group

from _control.AbstractPage import Abstract_UI_Page
from _data._data_academic_program import Course
from _data._data_measurement import GradesFile, ReportState, CourseFile, MeasurementExportFile
from _data._data_periods import Semester
from _data._data_schedule import Meeting
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_text_element, UI_TEXT_COLOR_Enum, UI_TEXT_BG_Enum, \
    UI_Text_BADGE_Type, UI_TEXT_ALIGNMENT_Enum, UI_Text_Alert_Type, UI_TEXT_HEADING_Enum, ui_list_element, \
    ui_table_element, UI_Row_Cell_Class_Enum, table_row, table_cell, UI_IMAGE_ALIGNMENT_Enum, ui_image_element
from _web.UI.UI_FORM_Element import ui_form_block, form_field, FormInputTypeEnum, ButtonClassEnum

from _data._data_quality import Course_CFI, ReviewerAffectations


class _page_measuerement_export(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Measurement :: Report statistics and Export', link=link,
                         request_obj=request)

    def CreateBlocks(self, _blocks_list=None):

        _admin_group_name = 'QUALITY_HEAD'
        _reviewers_group_name = 'QUALITY'
        _actual_semester = Semester.objects.get(semester_id=self.request_obj.session['selected_semester'])
        _actual_user = User.objects.get(id=self.request_obj.user.id)

        page_permission = False
        __reviewMode = False
        try:
            _permission_group = Group.objects.get(name=_admin_group_name)
            if _permission_group in _actual_user.groups.all():
                page_permission = True
        except Group.DoesNotExist:
            pass

        res = []
        if page_permission:

            res = []

            ###################################################################################
            ###################################################################################
            #################   STEP 2 - Handle Affectation Update

            if self.request_obj.method == 'POST' and 'selected_action' not in self.request_obj.POST.keys() and 'action' not in self.request_obj.POST.keys():
                _user_id = int(self.request_obj.POST['user'])
                _reviewer_id = int(self.request_obj.POST['reviewer'])
                _user = User.objects.get(id=_user_id)
                _reviewer = User.objects.get(id=_reviewer_id)
                _tmp = ReviewerAffectations.objects.get(user=_user, semester=_actual_semester)
                _tmp.reviewer = _reviewer
                _tmp.save()

            if self.request_obj.method == 'GET' and 'action' in self.request_obj.GET.keys():
                _export_file_id = int(self.request_obj.GET['id'])
                if self.request_obj.GET['action'] == 'delete_export_file':
                    try:
                        _export_file = MeasurementExportFile.objects.get(measurement_export_file_id=_export_file_id)
                        _export_file.delete()
                    except MeasurementExportFile.DoesNotExist as e:
                        print(e)

            ###################################################################################
            ###################################################################################
            #################   STEP 2 - List of stored Section Reports

            _list = GradesFile.objects.filter(semester=_actual_semester)

            _number_created = 0
            _number_submitted = 0
            _number_need_review = 0
            _number_accepted = 0
            _number_not_uploaded = 0

            #################################################################################################

            # We print the course list and we check if the section report is well submitted

            _list = Meeting.objects.filter(semester=_actual_semester)

            _ui_table_block = ui_basic_block(
                block_title='Measurement Section Reports')

            if len(_list) == 0:
                _text1 = ui_text_element(
                    text='There is no Available Measurement Section Reports.',
                    alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                    color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                    background=UI_TEXT_BG_Enum.NONE,
                    heading=UI_TEXT_HEADING_Enum.H4)

                _ui_table_block.addBasicElement(_text1)

                res.append(_ui_table_block)

            else:

                _rows = []

                _tt = []
                tt_counter = 0

                for _section in _list:

                    # here we have a meeting --> we look for the corresponding grade file

                    try:

                        _rep1 = GradesFile.objects.filter(semester=_actual_semester, section_code=_section.section,
                                                          teacher=_section.teacher,
                                                          section_courseObj=_section.course)

                        _tt.append(
                            f'{tt_counter} --> working with meeting {_section.meeting_id} that has {len(_rep1)}')
                        if len(_rep1) > 1:
                            for _rap in _rep1:
                                _tt.append(f'{tt_counter} --> we have gradefile #{_rap.grades_file_id}')

                        tt_counter += 1

                        _rep = GradesFile.objects.get(semester=_actual_semester, section_code=_section.section,
                                                      teacher=_section.teacher,
                                                      section_courseObj=_section.course)

                        if _rep.is_validated():
                            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
                            _number_accepted += 1
                        elif _rep.is_refused():
                            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_WARNING)
                            _number_need_review += 1
                        elif _rep.is_submitted():
                            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
                            _number_submitted += 1
                        else:
                            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SECONDARY)
                            _number_created += 1
                        _textToAdd = _rep.getReviewstate()

                    except GradesFile.DoesNotExist:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                        _textToAdd = 'Not yet Uploaded'
                        _number_not_uploaded += 1

                    _text1 = ui_text_element(text=str(_section.meeting_id),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_section.campus.campus_name),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_section.department.department_name),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=_section.teacher.last_name,
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_section.section),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=f'{_section.course.course_code} ---- {_section.course.course_name}',
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=_textToAdd,
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _rows.append(_row)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=['Id', 'Campus', 'Department', 'Faculty', 'section', 'Course',
                                                        'Status'],
                                          table_has_footer=False,
                                          table_is_striped=True,
                                          table_is_hover=True, table_is_bordered=True)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

            ###################################################################################
            ###################################################################################
            #################   STEP 2 - The Statistics

            _ui_basic_block = ui_basic_block(block_title='Section Reports Statistics')

            _rows = []

            ###############
            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
            _text1 = ui_text_element(text='Total Number of Section Reports',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)

            _text1 = ui_text_element(
                text=f'{_number_created + _number_submitted + _number_need_review + _number_accepted + _number_not_uploaded}',
                color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)

            _rows.append(_row)

            ###############
            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
            _text1 = ui_text_element(text='Accepted',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _text1 = ui_text_element(
                text=f'{_number_accepted}',
                color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _rows.append(_row)

            ###############
            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_WARNING)
            _text1 = ui_text_element(text='Need Review',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _text1 = ui_text_element(
                text=f'{_number_need_review}',
                color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _rows.append(_row)

            ###############
            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
            _text1 = ui_text_element(text='Under Review',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _text1 = ui_text_element(
                text=f'{_number_submitted}',
                color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _rows.append(_row)

            ###############
            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SECONDARY)
            _text1 = ui_text_element(text='Draft',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _text1 = ui_text_element(
                text=f'{_number_created}',
                color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _rows.append(_row)

            ###############
            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
            _text1 = ui_text_element(text='Not yet Uploaded',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _text1 = ui_text_element(
                text=f'{_number_not_uploaded}',
                color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)
            _rows.append(_row)

            _table = ui_table_element(table_rows=_rows,
                                      table_header=[],
                                      table_has_footer=False,
                                      table_is_striped=False,
                                      table_is_hover=False, table_is_bordered=True)

            _ui_basic_block.addBasicElement(_table)
            res.append(_ui_basic_block)

            ###################################################################################
            ###################################################################################
            #################   STEP 4 - List of stored Course Reports

            __list_GradesFiles = []
            __list_courses_with_more_than_two_sections = {}
            _work_withCourses = False

            __list_courses = Course.objects.all()
            for _course in __list_courses:
                __list_meetings = Meeting.objects.filter(semester=_actual_semester, course=_course)
                if len(__list_meetings) > 1:
                    _tmp = {}
                    _tmp['speciality'] = _course.program.specialization.specialization_name
                    _tmp['program'] = f'{_course.program.program_name} ({_course.program.program_version})'
                    _tmp['course'] = f'({_course.course_code}) --  {_course.course_name}'
                    _tmp['department'] = []
                    _tmp['sections'] = []
                    _tmp['campus'] = []
                    _tmp['teacher'] = []

                    _total_sections = len(__list_meetings)
                    for _meeting in __list_meetings:
                        _section_code = _meeting.section
                        _section_campus = _meeting.campus.campus_name_ar
                        _tmp['teacher'].append(_meeting.teacher.last_name)
                        _tmp['sections'].append(_meeting.section)
                        _tmp['department'].append(_meeting.department.department_name)
                        _tmp['campus'].append(_meeting.campus.campus_name)

                        __list_Section_Reports = GradesFile.objects.filter(semester=_actual_semester,
                                                                           section_code=_section_code,
                                                                           campus_name=_section_campus)

                        _total_section_reports = len(__list_Section_Reports)
                        _total_accepted_section_reports = 0
                        for _report in __list_Section_Reports:
                            if _report.is_validated():
                                _total_accepted_section_reports += 1

                        __list_Course_Reports = CourseFile.objects.filter(semester=_actual_semester,
                                                                          course_name=_course.course_code_ar,
                                                                          campus_name=_section_campus)

                    if _total_accepted_section_reports == _total_section_reports and _total_section_reports == _total_sections:
                        _tmp['status'] = 'Done'
                    else:
                        _tmp['status'] = 'In progress'

                    __list_courses_with_more_than_two_sections[_course] = _tmp

            _list = CourseFile.objects.filter(semester=_actual_semester)
            _number_created = 0
            _number_submitted = 0
            _number_need_review = 0
            _number_accpted = 0

            _ui_table_block = ui_basic_block(
                block_title='Measurement Course Reports')

            if len(__list_courses_with_more_than_two_sections) == 0:
                _text1 = ui_text_element(
                    text='There is no Course Reports Needed.',
                    alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                    color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                    background=UI_TEXT_BG_Enum.NONE,
                    heading=UI_TEXT_HEADING_Enum.H4)

                _ui_table_block.addBasicElement(_text1)

                res.append(_ui_table_block)

            else:

                _rows = []

                for _obj, _course in __list_courses_with_more_than_two_sections.items():

                    if _course['status'] == 'Done':
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)

                    else:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_WARNING)

                    _text1 = ui_text_element(text=_course['speciality'], color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=_course['program'], color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=self.List2text(_course['campus']), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=self.List2text(_course['department']),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=_course['course'], color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=self.List2text(_course['sections']),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=self.List2text(_course['teacher']),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=_course['status'], color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _rows.append(_row)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=['Speciality', 'Program', 'Campus', 'Department', 'Course',
                                                        'Sections',
                                                        'Faculties', 'Status'],
                                          table_has_footer=False,
                                          table_is_striped=True,
                                          table_is_hover=True, table_is_bordered=True)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

            ###################################################################################
            ###################################################################################
            #################   STEP 2 - The Statistics

            #### Reports

            _ui_form_block = ui_form_block(block_title='',
                                           form_action='generate_section_report_list', form_id='test',
                                           form_method='POST')

            _selected_semester = form_field(input_label='', input_name='selected_semester',
                                            input_value=str(_actual_semester.semester_id),
                                            input_type=FormInputTypeEnum.HIDDEN_INPUT)
            _selected_action = form_field(input_label='', input_name='selected_action', input_value='report',
                                          input_type=FormInputTypeEnum.HIDDEN_INPUT)

            _submit_field = form_field('Generate Section Report List', 'Generate Section Report List',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_SUCCESS)

            _ui_form_block.addFormField(_selected_semester)
            _ui_form_block.addFormField(_selected_action)
            _ui_form_block.addFormField(_submit_field)
            # res.append(_ui_form_block)

            _ui_form_block = ui_form_block(block_title='',
                                           form_action='generate_section_excel_list', form_id='test',
                                           form_method='POST')

            _selected_semester = form_field(input_label='', input_name='selected_semester',
                                            input_value=str(_actual_semester.semester_id),
                                            input_type=FormInputTypeEnum.HIDDEN_INPUT)
            _selected_action = form_field(input_label='', input_name='selected_action', input_value='report',
                                          input_type=FormInputTypeEnum.HIDDEN_INPUT)

            _submit_field = form_field('Generate Section Excel List', 'Generate Section Excel List',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_SUCCESS)

            _ui_form_block.addFormField(_selected_semester)
            _ui_form_block.addFormField(_selected_action)
            _ui_form_block.addFormField(_submit_field)
            # res.append(_ui_form_block)

            #################################################################################################
            _ui_form_block = ui_form_block(block_title='',
                                           form_action='generate_department_excel_list', form_id='test',
                                           form_method='POST')

            _selected_semester = form_field(input_label='', input_name='selected_semester',
                                            input_value=str(_actual_semester.semester_id),
                                            input_type=FormInputTypeEnum.HIDDEN_INPUT)
            _selected_action = form_field(input_label='', input_name='selected_action', input_value='report',
                                          input_type=FormInputTypeEnum.HIDDEN_INPUT)

            _submit_field = form_field('Generate Department Excel List', 'Generate Department Excel List',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_SUCCESS)

            _ui_form_block.addFormField(_selected_semester)
            _ui_form_block.addFormField(_selected_action)
            _ui_form_block.addFormField(_submit_field)
            # res.append(_ui_form_block)
            #################################################################################################
            #################################################################################################
            _ui_form_block = ui_form_block(block_title='Generate Excel file for all the Grades',
                                           form_action='generate_grades_excel_list', form_id='test',
                                           form_method='POST')

            _selected_semester = form_field(input_label='', input_name='selected_semester',
                                            input_value=str(_actual_semester.semester_id),
                                            input_type=FormInputTypeEnum.HIDDEN_INPUT)
            _selected_action = form_field(input_label='', input_name='selected_action', input_value='report',
                                          input_type=FormInputTypeEnum.HIDDEN_INPUT)

            _submit_field = form_field('Generate grades Excel List', 'Generate Grades Excel List',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_DANGER)

            _ui_form_block.addFormField(_selected_semester)
            _ui_form_block.addFormField(_selected_action)
            _ui_form_block.addFormField(_submit_field)
            res.append(_ui_form_block)
            #################################################################################################
            #################################################################################################
            #################################################################################################

            _list = MeasurementExportFile.objects.filter(semester=_actual_semester)

            _ui_table_block = ui_basic_block(
                block_title='List of Measurement Work Export')

            if len(_list) == 0:
                _text1 = ui_text_element(
                    text='There is not Export Work Stored.',
                    alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                    color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                    background=UI_TEXT_BG_Enum.NONE,
                    heading=UI_TEXT_HEADING_Enum.H4)

                _ui_table_block.addBasicElement(_text1)

                res.append(_ui_table_block)

            else:

                _rows = []

                for _doc in _list:

                    if _doc.state == 1:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
                        _textToAdd = 'Finished'
                    elif _doc.state == 0:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
                        _textToAdd = 'In Progress'
                    elif _doc.state == -1:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                        _textToAdd = 'Error'

                    _text1 = ui_text_element(text=str(_doc.measurement_export_file_id),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_textToAdd),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=_doc.teacher.last_name,
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=_doc.submission_time.strftime("%m/%d/%Y, %H:%M:%S"),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text='{}'.format(_doc.elapsedTime),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    try:
                        _size = _doc.export_file.size / 1024 / 1024
                        _text1 = ui_text_element(text=f'{"%.3f" % _size} Mb',
                                                 color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                        _text1 = ui_text_element(text='Download',
                                                 color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                                 link_url=_doc.export_file.url,
                                                 alert=UI_Text_Alert_Type.ALERT_INFO)
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)


                    except ValueError:
                        _text1 = ui_text_element(text='')
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)
                        _text1 = ui_text_element(text='Not ready')
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                    if _doc.state == 1 or _doc.state == -1:
                        _params = {}
                        _params['id'] = _doc.measurement_export_file_id
                        _params['action'] = 'delete_export_file'
                        _text20 = ui_text_element(text='Delete', alert=UI_Text_Alert_Type.ALERT_DANGER,
                                                  link_url=self.link, link_parameter=_params)
                        _cell20 = table_cell(cell_centent=_text20)
                        _row.add_cell_to_row(_cell20)
                    else:
                        _text1 = ui_text_element(text='')
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                    _rows.append(_row)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=['Id', 'Status', 'Submitted By', 'Submission', 'Elapsed Time',
                                                        'Size',
                                                        'Export File', ''],
                                          table_has_footer=False,
                                          table_is_striped=True,
                                          table_is_hover=True, table_is_bordered=True)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

            _ui_form_block = ui_form_block(block_title='',
                                           form_action='generate_zipped_measurement_reports_list', form_id='test',
                                           form_method='POST')

            _selected_semester = form_field(input_label='', input_name='selected_semester',
                                            input_value=str(_actual_semester.semester_id),
                                            input_type=FormInputTypeEnum.HIDDEN_INPUT)
            _selected_action = form_field(input_label='', input_name='selected_action', input_value='report',
                                          input_type=FormInputTypeEnum.HIDDEN_INPUT)

            _submit_field = form_field('Generate and export zipped reports list', 'Generate zipped reports list',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_DANGER)

            _ui_form_block.addFormField(_selected_semester)
            _ui_form_block.addFormField(_selected_action)
            _ui_form_block.addFormField(_submit_field)
            res.append(_ui_form_block)


        else:
            _ui_basic_block = ui_basic_block(block_title='Access Denied')
            _text1 = ui_text_element(
                text='The actual page is only for Quality Committee Heads.',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                background=UI_TEXT_BG_Enum.NONE,
                heading=UI_TEXT_HEADING_Enum.H4)

            _ui_basic_block.addBasicElement(_text1)

            res.append(_ui_basic_block)

        return res
