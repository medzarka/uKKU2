# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group

from _control.AbstractPage import Abstract_UI_Page
from _data._data_measurement import GradesFile, ReportState, CourseFile
from _data._data_periods import Semester
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_text_element, UI_TEXT_COLOR_Enum, UI_TEXT_BG_Enum, \
    UI_Text_BADGE_Type, UI_TEXT_ALIGNMENT_Enum, UI_Text_Alert_Type, UI_TEXT_HEADING_Enum, ui_list_element, \
    ui_table_element, UI_Row_Cell_Class_Enum, table_row, table_cell, UI_IMAGE_ALIGNMENT_Enum, ui_image_element
from _web.UI.UI_FORM_Element import ui_form_block, form_field, FormInputTypeEnum, ButtonClassEnum

from _data._data_quality import Course_CFI, ReviewerAffectations


class _page_mycfis_admin(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Quality :: CFI Administration', link=link,
                         request_obj=request)

    def CreateBlocks(self, _blocks_list=None):

        _admin_group_name = 'QUALITY'
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
            _actual_semester = Semester.objects.get(semester_id=self.request_obj.session['selected_semester'])
            _actual_user = User.objects.get(id=self.request_obj.user.id)
            res = []

            ###################################################################################
            ###################################################################################
            #################   STEP 2 - Upload your Course File Index reports
            if self.request_obj.method == 'POST' or \
                    (self.request_obj.method == 'GET' and 'editmode' in self.request_obj.GET.keys()):

                __editmode = 0
                _section_report = None
                if self.request_obj.method == 'GET':
                    __section_grades_report = int(self.request_obj.GET['section_selected'])
                    __editmode = self.request_obj.GET['editmode']

                if self.request_obj.method == 'POST':
                    __section_grades_report = int(self.request_obj.POST['section_selected'])

                _info = ui_basic_block(block_title='Section Information')
                try:
                    _section_report = GradesFile.objects.get(grades_file_id=__section_grades_report)

                    _steps = []
                    _steps.append(ui_text_element(
                        text='Section Location : \t ' + _section_report.campus_name,
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Course Name : \t' + _section_report.course_name,
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Section Codes : \t' + str(_section_report.section_code),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Section Department : \t' + str(_section_report.section_department),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Faculty: \t' + str(_section_report.teacher.last_name),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))

                    _list = ui_list_element(_steps, ordered=False)
                    _info.addBasicElement(_list)

                except Exception as e:
                    _h1 = ui_text_element(
                        text='An internal error was occured: the report is not found ! Please try again. \n ' + str(e),
                        alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                        color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                        heading=UI_TEXT_HEADING_Enum.H4)
                    _info.addBasicElement(_h1)

                res.append(_info)

                _info2 = ui_basic_block(block_title='Course File Index Information')
                if _section_report is None:
                    _h1 = ui_text_element(
                        text='An internal error was occured: the Course File index is not found ! Please try again. \n ',
                        alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                        color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                        heading=UI_TEXT_HEADING_Enum.H4)
                    _info2.addBasicElement(_h1)
                else:
                    try:
                        _my_cfi = Course_CFI.objects.get(gradeFile=_section_report)
                    except Course_CFI.DoesNotExist as e:
                        _my_cfi = Course_CFI(gradeFile=_section_report)
                        _my_cfi.save()

                    if __editmode == '3' :
                        # course_cfi_id, reviewer = last_name, remark
                        __remark = self.request_obj.GET['remark']
                        __reviewer = self.request_obj.GET['reviewer']
                        _my_cfi.addRemark(__remark, __reviewer)
                        _my_cfi.save()

                    if len(_my_cfi.getRemarks()) > 0:
                        __histories = ui_basic_block(block_title='Review History')

                        _history = []
                        for row in _my_cfi.getRemarks():
                            _history.append(
                                ui_text_element(
                                    text=f'{row}',
                                    alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                                    color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _list = ui_list_element(_history, ordered=False)
                        __histories.addBasicElement(_list)

                        res.append(__histories)
                    if __editmode == '1':
                        _ui_form_block = ui_form_block(block_title='Add New Review Remark',
                                                       form_action=self.link, form_id='remarks', form_method='GET')
                        _submit_field = form_field('Add the Remark',
                                                   'Add the Remark',
                                                   input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                                   button_class=ButtonClassEnum.BTN_WARNING)

                        ___action = form_field('editmode', 'editmode', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                               input_value='3', is_required=True)
                        ___reviewer = form_field('reviewer', 'reviewer', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                                 input_value=_actual_user.last_name, is_required=True)
                        ___selected_grade_file = form_field('section_selected', 'section_selected',
                                                            input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                                            input_value=str(__section_grades_report), is_required=True)

                        theremark = form_field('remark', 'remark', input_type=FormInputTypeEnum.TEXTAREA_INPUT,
                                               input_value='', size=100,
                                               maxlength=2048,
                                               placeholder='Type here your remark')

                        _ui_form_block.addFormField(___reviewer)
                        _ui_form_block.addFormField(___action)
                        _ui_form_block.addFormField(___selected_grade_file)
                        _ui_form_block.addFormField(theremark)
                        _ui_form_block.addFormField(_submit_field)
                        res.append(_ui_form_block)

                    ## upload a new report
                    if len(self.request_obj.FILES) != 0:
                        _report_type_id = self.request_obj.POST['report_type_id']
                        if _report_type_id == '1':
                            _my_cfi.course_specification_file = self.request_obj.FILES['report_to_upload']
                        if _report_type_id == '2':
                            _my_cfi.exams_samples_file = self.request_obj.FILES['report_to_upload']
                        if _report_type_id == '3':
                            _my_cfi.marks_file = self.request_obj.FILES['report_to_upload']
                        if _report_type_id == '4':
                            _my_cfi.clos_measurement_file = self.request_obj.FILES['report_to_upload']
                        if _report_type_id == '5':
                            _my_cfi.course_report_file = self.request_obj.FILES['report_to_upload']
                        if _report_type_id == '6':
                            _my_cfi.kpis_measurements_file = self.request_obj.FILES['report_to_upload']
                        if _report_type_id == '7':
                            _my_cfi.instructor_schedule_file = self.request_obj.FILES['report_to_upload']
                        if _report_type_id == '8':
                            _my_cfi.course_plan_file = self.request_obj.FILES['report_to_upload']
                        if _report_type_id == '10':
                            _my_cfi.curriculum_vitae_file = self.request_obj.FILES['report_to_upload']
                        _my_cfi.save()

                    #################################################
                    #################################################
                    #################################################
                    #################################################
                    _ui_table_block = ui_basic_block(block_title='List of the Course File Index Reports')

                    _rows = []

                    ___mydata = {"1 - Course Specification": _my_cfi.course_specification_file,
                                 "2 - Exam Examples": _my_cfi.exams_samples_file,
                                 "3 - Detailed Marks ": _my_cfi.marks_file,
                                 "4 - CLOs Measurement": _my_cfi.clos_measurement_file,
                                 "5 - Course Report": _my_cfi.course_report_file,
                                 "6 - KPIs Measurement": _my_cfi.kpis_measurements_file,
                                 "7 - Instructor Schedule": _my_cfi.instructor_schedule_file,
                                 "8 - Course Plan": _my_cfi.course_plan_file,
                                 "9 - Statistical Measurement": _my_cfi.gradeFile.report_file,
                                 "10 - Instructor CV": _my_cfi.curriculum_vitae_file}

                    for key, value in ___mydata.items():
                        try:
                            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
                            _text1 = ui_text_element(text=key, color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                                     isBold=True)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)
                            _text2 = ui_text_element(text='Click to view the file', link_url=str(value.url),
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK, link_to_new_tab=True,
                                                     badge=UI_Text_BADGE_Type.BADGE_LIGHT)
                            _cell2 = table_cell(cell_centent=_text2)
                            _row.add_cell_to_row(_cell2)
                        except ValueError:
                            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SECONDARY)
                            _text1 = ui_text_element(text=key, color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                                     isBold=True)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)
                            _text2 = ui_text_element(text='Not yet uploaded', color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell2 = table_cell(cell_centent=_text2)
                            _row.add_cell_to_row(_cell2)
                        _rows.append(_row)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=[],
                                          table_has_footer=False,
                                          table_is_striped=False,
                                          table_is_hover=False, table_is_bordered=False)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

                #################################################
                #################################################
                #################################################
                #################################################
                #################################################

            if self.request_obj.method == 'GET' and 'editmode' not in self.request_obj.GET.keys():

                ##### my reports list :

                if 'action' in self.request_obj.GET.keys() and 'course_cfi_id' in self.request_obj.GET.keys():
                    try:
                        _id = int(self.request_obj.GET['course_cfi_id'])
                        _action = self.request_obj.GET['action']
                        _report = Course_CFI.objects.get(course_cfi_id=_id)
                        if _action == 'accept':
                            _report.validate(_actual_user)
                        if _action == 'reject':
                            _report.refuse(_actual_user)

                    except _report.DoesNotExist:
                        pass

                _list = Course_CFI.objects.filter(gradeFile__semester=_actual_semester)

                if len(_list) > 0:
                    _ui_table_block = ui_basic_block(
                        block_title='List of Course File Index Reports to be Administrated')

                    _rows = []

                    for _report in _list:
                        try:
                            affected_reviewer = ReviewerAffectations.objects.get(semester=_actual_semester,
                                                                                 user=_report.gradeFile.teacher)
                            if affected_reviewer.reviewer == None:
                                continue
                            if affected_reviewer.reviewer.id != _actual_user.id:
                                continue

                            if _report.cfi_report_state == ReportState.ACCEPTED.value:
                                _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
                            if _report.cfi_report_state == ReportState.SUBMITTED.value:
                                _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
                            if _report.cfi_report_state == ReportState.NEEDS_REVIEW.value:
                                _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                            if _report.cfi_report_state == ReportState.CREATED.value:
                                _row = table_row(row_class=UI_Row_Cell_Class_Enum.NONE)

                            _text1 = ui_text_element(text=str(_report.course_cfi_id),
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)
                            _text1 = ui_text_element(text=str(_report.gradeFile.campus_name),
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)
                            _text1 = ui_text_element(text=str(_report.gradeFile.section_code),
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)

                            _text1 = ui_text_element(text=_report.gradeFile.section_department,
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)

                            _text1 = ui_text_element(text=_report.gradeFile.teacher.last_name,
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)

                            _text1 = ui_text_element(text=_report.gradeFile.getCourseFullName(),
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)
                            _text1 = ui_text_element(text=_report.getReviewstate(), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)

                            _text1 = ui_text_element(text=_report.submission_time.strftime("%m/%d/%Y, %H:%M:%S"),
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)

                            if _report.cfi_reviewer is None:
                                _rev = ''
                            else:
                                _rev = _report.cfi_reviewer.last_name
                            _text1 = ui_text_element(text=_rev,
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)

                            _text1 = ui_text_element(text=str(_report.cfi_version),
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)

                            if _report.cfi_report_state == ReportState.CREATED.value:
                                _text10 = ui_text_element(text='')
                                _cell10 = table_cell(cell_centent=_text10)
                                _row.add_cell_to_row(_cell10)
                                _row.add_cell_to_row(_cell10)
                                _row.add_cell_to_row(_cell10)

                            elif _report.cfi_report_state == ReportState.NEEDS_REVIEW.value or _report.cfi_report_state == ReportState.ACCEPTED.value:
                                _params = {}
                                _params['course_cfi_id'] = _report.course_cfi_id
                                _params['section_selected'] = _report.gradeFile.grades_file_id
                                _params['editmode'] = '0'
                                _text10 = ui_text_element(text='View Reports', alert=UI_Text_Alert_Type.ALERT_PRIMARY,
                                                          color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                          link_parameter=_params)
                                _cell10 = table_cell(cell_centent=_text10)
                                _row.add_cell_to_row(_cell10)

                                _text10 = ui_text_element(text='')
                                _cell10 = table_cell(cell_centent=_text10)
                                _row.add_cell_to_row(_cell10)
                                _row.add_cell_to_row(_cell10)

                            else:

                                _params = {}
                                _params['course_cfi_id'] = _report.course_cfi_id
                                _params['section_selected'] = _report.gradeFile.grades_file_id
                                _params['editmode'] = '1'
                                _text10 = ui_text_element(text='View Reports', alert=UI_Text_Alert_Type.ALERT_PRIMARY,
                                                          color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                          link_parameter=_params)
                                _cell10 = table_cell(cell_centent=_text10)
                                _row.add_cell_to_row(_cell10)

                                _params = {}
                                _params['course_cfi_id'] = _report.course_cfi_id
                                _params['section_selected'] = _report.gradeFile.grades_file_id
                                _params['action'] = 'accept'
                                _text10 = ui_text_element(text='Accept', alert=UI_Text_Alert_Type.ALERT_SUCCESS,
                                                          link_url=self.link, link_parameter=_params)
                                _cell10 = table_cell(cell_centent=_text10)
                                _row.add_cell_to_row(_cell10)

                                _params = {}
                                _params['course_cfi_id'] = _report.course_cfi_id
                                _params['section_selected'] = _report.gradeFile.grades_file_id
                                _params['action'] = 'reject'
                                _text10 = ui_text_element(text='Reject', alert=UI_Text_Alert_Type.ALERT_DANGER,
                                                          link_url=self.link, link_parameter=_params)
                                _cell10 = table_cell(cell_centent=_text10)
                                _row.add_cell_to_row(_cell10)

                            _rows.append(_row)
                        except ReviewerAffectations.DoesNotExist:
                            continue

                    _table = ui_table_element(table_rows=_rows,
                                              table_header=['Report ID', 'Location', 'Section', 'Department',
                                                            'Faculty', 'Course Name', 'Status', 'Submission',
                                                            'Reviewer', 'Version', '', '', ''],
                                              table_has_footer=False,
                                              table_is_striped=True,
                                              table_is_hover=True, table_is_bordered=True)
                    _ui_table_block.addBasicElement(_table)
                    res.append(_ui_table_block)

            return res

        else:

            ###################################################################################
            ###################################################################################
            ###################################################################################
            ###################################################################################
            #################

            _ui_basic_block = ui_basic_block(block_title='Access Denied')
            _text1 = ui_text_element(
                text='The actual page is only for Quality Committee Members.',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                background=UI_TEXT_BG_Enum.NONE,
                heading=UI_TEXT_HEADING_Enum.H4)

            _ui_basic_block.addBasicElement(_text1)

            res.append(_ui_basic_block)

        return res
