# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from _control.AbstractPage import Abstract_UI_Page
from _control._Measurement.Measurement_tools import Section_Measurment, Course_Measurment
from _data._data_measurement import GradesFile, ReportState, CourseFile
from _data._data_periods import Semester
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_text_element, UI_TEXT_COLOR_Enum, UI_TEXT_BG_Enum, \
    UI_Text_BADGE_Type, UI_TEXT_ALIGNMENT_Enum, UI_Text_Alert_Type, UI_TEXT_HEADING_Enum, ui_list_element, \
    ui_table_element, UI_Row_Cell_Class_Enum, table_row, table_cell, UI_IMAGE_ALIGNMENT_Enum, ui_image_element
from _web.UI.UI_FORM_Element import ui_form_block, form_field, FormInputTypeEnum, ButtonClassEnum

from _data._data_quality import Course_CFI
from _data._data_quality import ReviewerAffectations


class _page_mycfis(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Quality :: My Course File indices', link=link,
                         request_obj=request)

    def CreateBlocks(self, _blocks_list=None):
        _actual_semester = Semester.objects.get(semester_id=self.request_obj.session['selected_semester'])
        _actual_user = User.objects.get(id=self.request_obj.user.id)
        res = []

        ###################################################################################
        ###################################################################################
        #################   STEP 2 - Upload your Course File Index reports
        if self.request_obj.method == 'POST' or (
                self.request_obj.method == 'GET' and 'editmode' in self.request_obj.GET.keys()):

            __editmode = 0
            __uploadmode = 0
            _section_report = None
            if self.request_obj.method == 'GET':
                __section_grades_report = int(self.request_obj.GET['section_selected'])
                __editmode = int(self.request_obj.GET['editmode'])
            if self.request_obj.method == 'POST':
                __section_grades_report = int(self.request_obj.POST['section_selected'])
                __editmode = int(self.request_obj.POST['editmode'])
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

                ## upload a new report
                if len(self.request_obj.FILES) != 0:
                    __uploadmode = 1
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

            if __editmode == 1 or __uploadmode == 1:
                _ui_form_block_upload = ui_form_block(block_title='Upload/Update a Report',
                                                      form_action=self.link, form_id='report_upload',
                                                      form_method='POST')
                _data = {'1': '1 - Course Specification', '2': '2 - Exams Example', '3': '3 - Marks File',
                         '4': '4 - CLOs Measurement',
                         '5': '5 - Course Report', '6': '6 - KPIs Measurement', '7': '7 - Faculty Schedule',
                         '8': '8 - Course Plan',
                         '10': '10 - Curriculum Vitae'}

                _select_field = form_field('The Report Type', 'report_type_id',
                                           input_type=FormInputTypeEnum.SELECT_INPUT, list_data=_data)
                _report_field = form_field('The report (60 MB Max Size)', 'report_to_upload',
                                           input_type=FormInputTypeEnum.FILE_INPUT)

                _submit_field = form_field('Upload/Update', 'Upload_Update',
                                           input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                           button_class=ButtonClassEnum.BTN_SUCCESS)
                _cancel_field = form_field('Cancel', 'Cancel',
                                           input_type=FormInputTypeEnum.RESET_INPUT,
                                           button_class=ButtonClassEnum.BTN_SECONDARY)
                _edit_field = form_field('editmode', 'editmode', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                         input_value='1')
                _section_selected_field = form_field('section_selected', 'section_selected',
                                                     input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                                     input_value=str(__section_grades_report))

                _ui_form_block_upload.addFormField(_select_field)
                _ui_form_block_upload.addFormField(_report_field)
                _ui_form_block_upload.addFormField(_submit_field)
                _ui_form_block_upload.addFormField(_cancel_field)
                _ui_form_block_upload.addFormField(_edit_field)
                _ui_form_block_upload.addFormField(_section_selected_field)

                res.append(_ui_form_block_upload)

            if 'adminmode' in self.request_obj.GET.keys():
                _ui_form_block = ui_form_block(block_title='',
                                               form_action='quality_export', form_id='back', form_method='GET')
                _submit_field = form_field('Back to the Course File Index list',
                                           'Back to the Course File Index list',
                                           input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                           button_class=ButtonClassEnum.BTN_PRIMARY)
                _ui_form_block.addFormField(_submit_field)
                res.append(_ui_form_block)
            else:

                _ui_form_block = ui_form_block(block_title='',
                                               form_action=self.link, form_id='back', form_method='GET')
                _submit_field = form_field('Back to the Course File Index list Page',
                                           'Back to the Course File Index list Page',
                                           input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                           button_class=ButtonClassEnum.BTN_PRIMARY)
                _ui_form_block.addFormField(_submit_field)
                res.append(_ui_form_block)

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
                    if _action == 'submit':
                        try:
                            _reviewer_email = ReviewerAffectations.objects.get(semester=_actual_semester,
                                                                               user=_actual_user).reviewer.email
                        except:
                            _reviewer_email = ''
                        _report.submit(update=True, reviewer_email=_reviewer_email)
                    if _action == 'delete':
                        _report.end()
                except _report.DoesNotExist:
                    pass

            _list = Course_CFI.objects.filter(gradeFile__teacher=_actual_user, gradeFile__semester=_actual_semester)
            if len(_list) > 0:
                _ui_table_block = ui_basic_block(block_title='List of my Course File Index Reports')

                _rows = []

                for _report in _list:
                    if _report.cfi_report_state == ReportState.ACCEPTED.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
                    if _report.cfi_report_state == ReportState.SUBMITTED.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
                    if _report.cfi_report_state == ReportState.NEEDS_REVIEW.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                    if _report.cfi_report_state == ReportState.CREATED.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.NONE)

                    _text1 = ui_text_element(text=str(_report.course_cfi_id), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
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
                        _rev = _report.cfi_reviewer.first_name
                    _text1 = ui_text_element(text=_rev,
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_report.cfi_version),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    if _report.cfi_report_state == ReportState.CREATED.value:
                        _params = {}
                        _params['course_cfi_id'] = _report.course_cfi_id
                        _params['section_selected'] = _report.gradeFile.grades_file_id
                        _params['action'] = 'submit'
                        _text10 = ui_text_element(text='Submit', alert=UI_Text_Alert_Type.ALERT_PRIMARY,
                                                  link_url=self.link, link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _params = {}
                        _params['course_cfi_id'] = _report.course_cfi_id
                        _params['section_selected'] = _report.gradeFile.grades_file_id
                        _params['editmode'] = '1'
                        _text10 = ui_text_element(text='View/Edit Reports', alert=UI_Text_Alert_Type.ALERT_WARNING,
                                                  color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                  link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _params = {}
                        _params['course_cfi_id'] = _report.course_cfi_id
                        _params['section_selected'] = _report.gradeFile.grades_file_id
                        _params['action'] = 'delete'
                        _text20 = ui_text_element(text='Delete', alert=UI_Text_Alert_Type.ALERT_DANGER,
                                                  link_url=self.link, link_parameter=_params)
                        _cell20 = table_cell(cell_centent=_text20)
                        _row.add_cell_to_row(_cell20)
                    elif _report.cfi_report_state == ReportState.NEEDS_REVIEW.value:

                        _params = {}
                        _params['course_cfi_id'] = _report.course_cfi_id
                        _params['section_selected'] = _report.gradeFile.grades_file_id
                        _params['action'] = 'submit'
                        _text10 = ui_text_element(text='Submit', alert=UI_Text_Alert_Type.ALERT_PRIMARY,
                                                  link_url=self.link, link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _params = {}
                        _params['course_cfi_id'] = _report.course_cfi_id
                        _params['section_selected'] = _report.gradeFile.grades_file_id
                        _params['editmode'] = '1'
                        _text10 = ui_text_element(text='View/Edit Reports', alert=UI_Text_Alert_Type.ALERT_PRIMARY,
                                                  color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                  link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _text10 = ui_text_element(text='')
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                    else:

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

                    _rows.append(_row)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=['Report ID', 'Location', 'Section', 'Department',
                                                        'Course Name', 'Status', 'Submission',
                                                        'Reviewer', 'Version', '', '', ''],
                                          table_has_footer=False,
                                          table_is_striped=True,
                                          table_is_hover=True, table_is_bordered=True)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

            _ui_basic_block = ui_basic_block(block_title='Instructions for Uploading a Course File Index')
            _text1 = ui_text_element(
                text='The actual page helps to submit your course quality files. They will be then evaluated by the Quality committee of your departement.',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.NONE)

            _text2 = ui_text_element(text='Please follow these steps to upload your course quality files:',
                                     alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                     background=UI_TEXT_BG_Enum.TEXT_WHITE)

            _steps = []

            _step1 = ui_text_element(
                text='In the form below, select the section that you will upload course files for it. Only sections that have validated by the measurement committee will be displayed.',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)
            _step2 = ui_text_element(
                text='Click on the button "Select the Section",',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)
            _step3 = ui_text_element(
                text='The system will create a course file index for the section being selected. It will be displayed in the start of this page,',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)
            _step5 = ui_text_element(
                text='Then, Select your course file index from the table in the start of this page, and start uploading your files .',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)

            _steps.append(_step1)
            _steps.append(_step2)
            _steps.append(_step3)
            _steps.append(_step5)
            _list = ui_list_element(_steps, ordered=True)

            _ui_basic_block.addBasicElement(_text1)
            _ui_basic_block.addBasicElement(_text2)
            _ui_basic_block.addBasicElement(_list)
            # _ui_basic_block.addBasicElement(_text3)
            res.append(_ui_basic_block)

            ########################################################################################
            ############################################  Course Selection form

            _list_sections = []
            _work_withCourses = False
            for _gradeFile in GradesFile.objects.filter(semester=_actual_semester, teacher=_actual_user,
                                                        report_state=ReportState.ACCEPTED.value):
                try:
                    Course_CFI.objects.get(gradeFile=_gradeFile)
                except Course_CFI.DoesNotExist:
                    _list_sections.append(_gradeFile)

            if len(_list_sections) > 0:
                _ui_form_block = ui_form_block(block_title='Select a Section',
                                               form_action=self.link, form_id='section_selection', form_method='POST')
                _data = {}
                for _report in _list_sections:
                    _data[str(
                        _report.grades_file_id)] = f'section {_report.section_code} ---> {_report.getCourseFullName()}'

                _select_field = form_field('The Section', 'section_selected',
                                           input_type=FormInputTypeEnum.SELECT_INPUT, list_data=_data)

                _submit_field = form_field('Select the Section', 'Submit',
                                           input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                           button_class=ButtonClassEnum.BTN_SUCCESS)
                _cancel_field = form_field('Cancel', 'Cancel',
                                           input_type=FormInputTypeEnum.RESET_INPUT,
                                           button_class=ButtonClassEnum.BTN_SECONDARY)

                _action_field = form_field('select', 'select', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                           input_value='1')
                _edit_field = form_field('editmode', 'editmode', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                         input_value='1')

                _ui_form_block.addFormField(_select_field)
                _ui_form_block.addFormField(_submit_field)
                _ui_form_block.addFormField(_cancel_field)
                _ui_form_block.addFormField(_action_field)
                _ui_form_block.addFormField(_edit_field)
                res.append(_ui_form_block)
            else:
                _report = ui_basic_block(block_title='')
                _h1 = ui_text_element(
                    text='You have no sections being validated by the measurement committee.',
                    alignment=UI_TEXT_ALIGNMENT_Enum.CENTER,
                    color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                    heading=UI_TEXT_HEADING_Enum.H3)
                _report.addBasicElement(_h1)
                res.append(_report)
        return res
