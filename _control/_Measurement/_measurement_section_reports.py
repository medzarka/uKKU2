# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from _data._data_measurement import MeasurementReviewerAffectations

from _control.AbstractPage import Abstract_UI_Page
from _control._Measurement.Measurement_tools import Section_Measurment
from _data._data_measurement import GradesFile, ReportState, Department
from _data._data_academic_program import Course
from _data._data_schedule import Meeting
from _data._data_periods import Semester
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_text_element, UI_TEXT_COLOR_Enum, UI_TEXT_BG_Enum, \
    UI_Text_BADGE_Type, UI_TEXT_ALIGNMENT_Enum, UI_Text_Alert_Type, UI_TEXT_HEADING_Enum, ui_list_element, \
    ui_table_element, UI_Row_Cell_Class_Enum, table_row, table_cell, UI_IMAGE_ALIGNMENT_Enum, ui_image_element

from _web.UI.UI_FORM_Element import ui_form_block, form_field, FormInputTypeEnum, ButtonClassEnum


class _page_generate_section_reports(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Measurement :: Generate Measurement Section Reports', link=link,
                         request_obj=request)

    def CreateBlocks(self, _blocks_list=None):
        _actual_semester = Semester.objects.get(semester_id=self.request_obj.session['selected_semester'])
        _actual_user = User.objects.get(id=self.request_obj.user.id)
        res = []

        ###################################################################################
        ###################################################################################
        #################   STEP 3 - Generate and submit the report
        if self.request_obj.method == 'POST' and 'Analysis' in self.request_obj.POST and 'id' in self.request_obj.POST:

            _report = ui_basic_block(block_title='Measurement Section Report')
            _analysis = self.request_obj.POST['Analysis']
            _id = int(self.request_obj.POST['id'])

            try:
                _course_report = GradesFile.objects.get(grades_file_id=_id)
                _course_report.teacher_analysis = _analysis
                # _course_report.section_department = Department.objects.get(department_id=_department)
                # _course_report.section_courseObj = Course.objects.get(course_id=_course_id)
                # _course_report.course_name = _course_report.section_courseObj.course_name
                # _course_report.course_code = _course_report.section_courseObj.course_code
                _course_report.save()
                _tool = Section_Measurment(report_obj=_course_report)
                if _tool.generate_report():
                    # _course_report.report_state = ReportState.SUBMITTED.value
                    try:
                        _reviewer_email = MeasurementReviewerAffectations.objects.get(semester=_actual_semester,
                                                                                      user=_actual_user).reviewer.email
                    except:
                        _reviewer_email = ''
                    _course_report.submit(reviewer_email=_reviewer_email)
                    _course_report.save()
                    _h1 = ui_text_element(
                        text='Done. The report is Generated.',
                        alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                        color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS,
                        heading=UI_TEXT_HEADING_Enum.H3)
                    _report.addBasicElement(_h1)

                    _h1 = ui_text_element(
                        text='Click here to download the generated report',
                        alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                        color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS,
                        heading=UI_TEXT_HEADING_Enum.H5, link_url=_course_report.report_file.url)
                    _report.addBasicElement(_h1)

                else:
                    _h1 = ui_text_element(
                        text='An error is occured when creating the report.',
                        alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                        color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                        heading=UI_TEXT_HEADING_Enum.H4)
                    _report.addBasicElement(_h1)


            except Exception as e:
                _h1 = ui_text_element(
                    text='An internal error was occured: the report is not found ! Please try again. \n ' + str(e),
                    alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                    color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                    heading=UI_TEXT_HEADING_Enum.H4)
                _report.addBasicElement(_h1)

            res.append(_report)

            _course_report = GradesFile.objects.get(grades_file_id=_id)

            # _ui_form_block = ui_form_block(block_title='',
            #                               form_action=self.link, form_id='test', form_method='POST')
            # _doc_id = form_field('submission_id', 'submission_id', input_type=FormInputTypeEnum.HIDDEN_INPUT,
            #                     input_value=str(_course_report.grades_file_id), is_required=True)
            # _submit_field = form_field('Submit the Report', 'Submit the Report',
            #                           input_type=FormInputTypeEnum.SUBMIT_INPUT,
            #                           button_class=ButtonClassEnum.BTN_SUCCESS)
            # _ui_form_block.addFormField(_doc_id)
            # _ui_form_block.addFormField(_submit_field)
            # res.append(_ui_form_block)

            _ui_form_block = ui_form_block(block_title='',
                                           form_action=self.link, form_id='test', form_method='GET')
            _submit_field = form_field('Go Back to the submission page',
                                       'Go Back to the submission page',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_PRIMARY)
            _ui_form_block.addFormField(_submit_field)
            res.append(_ui_form_block)

        ###################################################################################
        ###################################################################################
        #################   STEP 2 - Statistics Display/Edit
        if (self.request_obj.method == 'POST' and 'gradesfile' in self.request_obj.FILES.keys()) or (
                self.request_obj.method == 'GET' and 'editmode' in self.request_obj.GET.keys()):

            _extraction_result = False
            __edit_mode = False
            __readonly_mode = False
            __add_mode = False

            if 'editmode' in self.request_obj.GET.keys():
                _mode = int(self.request_obj.GET['editmode'])
                __doc_ID = int(self.request_obj.GET['id'])
                if _mode == 0:
                    __edit_mode = True
                else:
                    __readonly_mode = True
            elif 'gradesfile' in self.request_obj.FILES.keys():
                __add_mode = True
                __meeting_id = int(self.request_obj.POST['meeting_id'])
                _meeting_obj = Meeting.objects.get(meeting_id=__meeting_id)

            ########################################## Alerts
            _ui_basic_block = ui_basic_block(block_title='')

            if not __edit_mode and not __readonly_mode:
                _measurement = Section_Measurment(filename=self.request_obj.FILES['gradesfile'],
                                                  user=_actual_user, semester=_actual_semester)
                _extraction_result = _measurement.extract_data()

                for text in _measurement.info:
                    _text = ui_text_element(
                        text=text,
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                        background=UI_TEXT_BG_Enum.NONE, alert=UI_Text_Alert_Type.ALERT_SUCCESS)
                    _ui_basic_block.addBasicElement(_text)
                for text in _measurement.errors:
                    _text = ui_text_element(
                        text=text,
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                        background=UI_TEXT_BG_Enum.NONE, alert=UI_Text_Alert_Type.ALERT_DANGER)
                    _ui_basic_block.addBasicElement(_text)
                for text in _measurement.warning:
                    _text = ui_text_element(
                        text=text,
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_WARNING,
                        background=UI_TEXT_BG_Enum.NONE, alert=UI_Text_Alert_Type.ALERT_WARNING)
                    _ui_basic_block.addBasicElement(_text)
                res.append(_ui_basic_block)

            if _extraction_result or __edit_mode or __readonly_mode:
                ########################################## Stats
                if _extraction_result:
                    GradesFile_obj = _measurement.getReportObj()
                    if 'meeting_id' in self.request_obj.POST.keys():
                        __meeting_id = int(self.request_obj.POST['meeting_id'])
                        _meeting_obj = Meeting.objects.get(meeting_id=__meeting_id)
                        GradesFile_obj.course_name = f'{_meeting_obj.course.course_name} ({_meeting_obj.course.course_name_ar})'
                        GradesFile_obj.course_code = _meeting_obj.course.course_code
                        GradesFile_obj.section_department = _meeting_obj.department
                        GradesFile_obj.campus_name = f'{_meeting_obj.campus.campus_name} ({_meeting_obj.campus.campus_name_ar})'
                        GradesFile_obj.section_courseObj = _meeting_obj.course
                        GradesFile_obj.section_code = _meeting_obj.section
                        GradesFile_obj.save()

                if __edit_mode or __readonly_mode:
                    GradesFile_obj = GradesFile.objects.get(grades_file_id=__doc_ID)

                _stats = ui_basic_block(block_title='Statistic Results')

                if GradesFile_obj is None:
                    _text = ui_text_element(
                        text='Internal Error. The report model is not found or could not be saved',
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_WARNING,
                        background=UI_TEXT_BG_Enum.NONE, alert=UI_Text_Alert_Type.ALERT_DANGER)
                    _stats.addBasicElement(_text)

                else:
                    if GradesFile_obj.report_state == ReportState.ACCEPTED.value and not __readonly_mode:
                        _text1 = ui_text_element(
                            text='The grade file is already submitted. And the report is already validated',
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_PRIMARY, heading=UI_TEXT_HEADING_Enum.H3)
                        _stats.addBasicElement(_text1)

                    if GradesFile_obj.report_state == ReportState.SUBMITTED.value:
                        _text1 = ui_text_element(
                            text='The grade file is already submitted. And the report is under review process.',
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_WARNING, heading=UI_TEXT_HEADING_Enum.H3)
                        _stats.addBasicElement(_text1)

                    if GradesFile_obj.report_state == ReportState.CREATED.value or GradesFile_obj.report_state == ReportState.NEEDS_REVIEW.value or __readonly_mode:

                        _h1 = ui_text_element(
                            text='Course Information',
                            alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                            color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS,
                            heading=UI_TEXT_HEADING_Enum.H4)
                        _stats.addBasicElement(_h1)

                        _steps = []
                        _steps.append(ui_text_element(
                            text='Campus: \t ' + GradesFile_obj.campus_name,
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Department: \t' + f'{GradesFile_obj.section_department}',
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Section Code: \t' + str(GradesFile_obj.section_code),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Course Name: \t' + str(GradesFile_obj.section_courseObj),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Teacher: \t' + f'{GradesFile_obj.teacher.first_name} ({GradesFile_obj.teacher.last_name})',
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))

                        _list = ui_list_element(_steps, ordered=False)
                        _stats.addBasicElement(_list)

                        _h1 = ui_text_element(
                            text='Statistic values',
                            alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                            color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS,
                            heading=UI_TEXT_HEADING_Enum.H4)
                        _stats.addBasicElement(_h1)

                        _steps = []
                        _steps.append(ui_text_element(
                            text='Mean : \t' + str(GradesFile_obj.stat_mean),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Standard Deviation : \t' + str(GradesFile_obj.stat_std),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Skewness : \t' + str(GradesFile_obj.stat_skewness),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Correlation between Mids/Finals : \t' + str(GradesFile_obj.stat_correlation_value),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Correlation between Sig. : \t' + str(GradesFile_obj.stat_correlation_sig),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Min : \t' + str(GradesFile_obj.stat_min),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _steps.append(ui_text_element(
                            text='Max : \t' + str(GradesFile_obj.stat_max),
                            alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                            color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                        _list = ui_list_element(_steps, ordered=False)
                        _stats.addBasicElement(_list)

                        _h1 = ui_text_element(
                            text='Histogram',
                            alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                            color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS,
                            heading=UI_TEXT_HEADING_Enum.H4)
                        _stats.addBasicElement(_h1)

                        _hist = ui_image_element(image_url=GradesFile_obj.stat_histogram.url, image_alt='Histogram',
                                                 image_width='500', image_height='500',
                                                 image_alignment=UI_IMAGE_ALIGNMENT_Enum.MIDDLE)
                        _stats.addBasicElement(_hist)
                        _h1 = ui_text_element(
                            text='Tips for the Section Result Analysis',
                            alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                            color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS,
                            heading=UI_TEXT_HEADING_Enum.H4)
                        _stats.addBasicElement(_h1)

                        tips = ui_text_element(
                            text=GradesFile_obj.stat_analysis,
                            alignment=UI_TEXT_ALIGNMENT_Enum.LEFT)
                        _stats.addBasicElement(tips)

                        _ui_form_block = ui_form_block(block_title='Generate Measurement Section Report',
                                                       form_action=self.link, form_id='test', form_method='POST')

                        if GradesFile_obj.section_department == None:
                            _department_content = ''
                        else:
                            _department_content = GradesFile_obj.section_department.department_name

                        _department_list = {}
                        for _dep in Department.objects.all():
                            _department_list[str(_dep.department_id)] = _dep.department_name

                        try:
                            _dep = str(GradesFile_obj.section_department.department_id)
                        except:
                            _dep = ''

                        ___is_required = False
                        ___is_readonly = True

                        if __add_mode:
                            ___is_required = True
                            ___is_readonly = False

                        if __edit_mode:
                            ___is_required = True
                            ___is_readonly = False

                        if GradesFile_obj.teacher_analysis == None:
                            _analyse_content = ''
                        else:
                            _analyse_content = GradesFile_obj.teacher_analysis

                        _analysis = form_field('Analysis', 'Analysis', input_type=FormInputTypeEnum.TEXTAREA_INPUT,
                                               input_value=_analyse_content, size=100,
                                               maxlength=2048,
                                               placeholder='Type here your analysis',
                                               is_required=___is_required, is_readonly=___is_readonly)
                        _doc_id = form_field('id', 'id', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                             input_value=str(GradesFile_obj.grades_file_id), is_required=True)

                        _submit_field = form_field('Generate Section Report', 'Generate Section Report',
                                                   input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                                   button_class=ButtonClassEnum.BTN_SUCCESS)
                        _cancel_field = form_field('Cancel', 'Cancel',
                                                   input_type=FormInputTypeEnum.RESET_INPUT,
                                                   button_class=ButtonClassEnum.BTN_SECONDARY)

                        _ui_form_block.addFormField(_analysis)
                        _ui_form_block.addFormField(_doc_id)
                        if __edit_mode or __add_mode:
                            _ui_form_block.addFormField(_submit_field)
                            _ui_form_block.addFormField(_cancel_field)

                        res.append(_ui_form_block)

                        ##########################################################################################
                        if len(GradesFile_obj.getRemarks()) > 0:
                            __histories = ui_basic_block(block_title='Review History')

                            _history = []
                            for row in GradesFile_obj.getRemarks():
                                _history.append(
                                    ui_text_element(
                                        text=f'{row}',
                                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                            _list = ui_list_element(_history, ordered=False)
                            __histories.addBasicElement(_list)

                            res.append(__histories)
                        ##########################################################################################

                res.append(_stats)

            _ui_form_block = ui_form_block(block_title='',
                                           form_action=self.link, form_id='test', form_method='GET')
            _submit_field = form_field('Back to the submission page', 'Back to the submission page',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_PRIMARY)
            _ui_form_block.addFormField(_submit_field)
            res.append(_ui_form_block)

        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        #################   STEP 1 - Submission Page
        if (self.request_obj.method == 'GET' and 'editmode' not in self.request_obj.GET.keys()) or (
                self.request_obj.method == 'POST' and 'submission_id' in self.request_obj.POST.keys()):

            if 'submission_id' in self.request_obj.POST.keys() and self.request_obj.POST['submission_id']:
                print('Updating the report with ID = ' + self.request_obj.POST['submission_id'])
                _id = int(self.request_obj.POST['submission_id'])
                _course_report = GradesFile.objects.get(grades_file_id=_id)
                _course_report.report_state = ReportState.SUBMITTED.value
                _course_report.save()
                print('Report Updated')

            if 'action' in self.request_obj.GET.keys() and 'id' in self.request_obj.GET.keys():
                try:
                    _id = int(self.request_obj.GET['id'])
                    _action = self.request_obj.GET['action']
                    _report = GradesFile.objects.get(grades_file_id=_id)
                    if _action == 'submit':
                        try:
                            _reviewer_email = MeasurementReviewerAffectations.objects.get(semester=_actual_semester,
                                                                                          user=_actual_user).reviewer.email
                        except:
                            _reviewer_email = ''
                        _report.submit(update=True, reviewer_email=_reviewer_email)
                    if _action == 'delete':
                        _report.end()
                except GradesFile.DoesNotExist:
                    pass

            _list = GradesFile.objects.filter(teacher=_actual_user, semester=_actual_semester)
            print('nbr of reports == ' + str(len(_list)))
            if len(_list) > 0:
                _ui_table_block = ui_basic_block(block_title='List of my Section Reports')

                _rows = []

                for _report in _list:
                    if _report.report_state == ReportState.ACCEPTED.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
                    if _report.report_state == ReportState.SUBMITTED.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
                    if _report.report_state == ReportState.NEEDS_REVIEW.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                    if _report.report_state == ReportState.CREATED.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_LIGHT)

                    _text1 = ui_text_element(text=str(_report.grades_file_id), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)
                    _text1 = ui_text_element(text=str(_report.campus_name), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)
                    _text1 = ui_text_element(text=str(_report.section_code), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)
                    _text1 = ui_text_element(text=_report.section_department, color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)
                    _text1 = ui_text_element(text=_report.getCourseFullName(), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)
                    _text1 = ui_text_element(text=_report.getReviewstate(), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)
                    _text1 = ui_text_element(text=_report.submission_time.strftime("%m/%d/%Y, %H:%M:%S"),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    if _report.reviewer is None:
                        _text1 = ui_text_element(text='', color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    else:
                        _text1 = ui_text_element(text=_report.reviewer.last_name, color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_report.version),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    try:
                        _text1 = ui_text_element(text='View', alert=UI_Text_Alert_Type.ALERT_LIGHT,
                                                 color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                                 link_url=_report.report_file.url)
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                    except ValueError:
                        _text1 = ui_text_element(text='')
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                    if _report.report_state == ReportState.CREATED.value:
                        _params = {}
                        _params['id'] = _report.grades_file_id
                        _params['action'] = 'submit'
                        _text10 = ui_text_element(text='Submit', alert=UI_Text_Alert_Type.ALERT_PRIMARY,
                                                  link_url=self.link, link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _params = {}
                        _params['id'] = _report.grades_file_id
                        _params['editmode'] = '0'
                        _text10 = ui_text_element(text='Edit', alert=UI_Text_Alert_Type.ALERT_WARNING,
                                                  color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                  link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _params = {}
                        _params['id'] = _report.grades_file_id
                        _params['action'] = 'delete'
                        _text20 = ui_text_element(text='Delete', alert=UI_Text_Alert_Type.ALERT_DANGER,
                                                  link_url=self.link, link_parameter=_params)
                        _cell20 = table_cell(cell_centent=_text20)
                        _row.add_cell_to_row(_cell20)
                    elif _report.report_state == ReportState.NEEDS_REVIEW.value:

                        _text3 = ui_text_element(text='', badge=UI_Text_BADGE_Type.NONE,
                                                 color=UI_TEXT_COLOR_Enum.TEXT_WHITE)
                        _cell3 = table_cell(cell_centent=_text3)
                        _row.add_cell_to_row(_cell3)

                        _params = {}
                        _params['id'] = _report.grades_file_id
                        _params['editmode'] = '0'
                        _text10 = ui_text_element(text='Edit', alert=UI_Text_Alert_Type.ALERT_WARNING,
                                                  color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                  link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _text3 = ui_text_element(text='', badge=UI_Text_BADGE_Type.NONE,
                                                 color=UI_TEXT_COLOR_Enum.TEXT_WHITE)
                        _cell3 = table_cell(cell_centent=_text3)
                        _row.add_cell_to_row(_cell3)

                    else:
                        _text3 = ui_text_element(text='', badge=UI_Text_BADGE_Type.NONE,
                                                 color=UI_TEXT_COLOR_Enum.TEXT_WHITE)
                        _cell3 = table_cell(cell_centent=_text3)
                        _row.add_cell_to_row(_cell3)

                        _params = {}
                        _params['id'] = _report.grades_file_id
                        _params['editmode'] = '1'
                        _text10 = ui_text_element(text='Details', alert=UI_Text_Alert_Type.ALERT_PRIMARY,
                                                  color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                  link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _text3 = ui_text_element(text='', badge=UI_Text_BADGE_Type.NONE,
                                                 color=UI_TEXT_COLOR_Enum.TEXT_WHITE)
                        _cell3 = table_cell(cell_centent=_text3)
                        _row.add_cell_to_row(_cell3)

                    _rows.append(_row)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=['ID', 'Location', 'Section', 'Department', 'Course Name',
                                                        'Status', 'Submission', 'Reviewer', 'Version', 'Report', '',
                                                        '', ''],
                                          table_has_footer=False,
                                          table_is_striped=True,
                                          table_is_hover=True, table_is_bordered=True)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

            _ui_basic_block = ui_basic_block(block_title='Instructions for Measurement Report Generation')
            _text1 = ui_text_element(
                text='The actual page helps faculties to generate measurement report for a given section based on grades downloaded from the KKU Academia Service.',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.NONE)

            _text2 = ui_text_element(text='Please follow these steps to generate your section measurement report:',
                                     alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                     background=UI_TEXT_BG_Enum.TEXT_WHITE)

            _text3 = ui_text_element(
                text='Please remember that the generated report do not contain the analysis section. Then, you are asked to fill that section.',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                background=UI_TEXT_BG_Enum.NONE)

            _steps = []

            _step1 = ui_text_element(
                text='Download your grades Excel file from the KKU Academia Service (for one section),',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)
            _step2 = ui_text_element(
                text='Upload the grades Excel file through the following form,',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)
            _step3 = ui_text_element(
                text='Click on the button "Submit the Grade File",',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)
            _step4 = ui_text_element(
                text='The statistics about your grades will be displayed. Then, type your department name, and your analysis. And click in "Generate the Report".',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)
            _step5 = ui_text_element(
                text='The report will be then generated. You can download the report. You can submit it by clicking on "Submit the report".',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)

            _steps.append(_step1)
            _steps.append(_step2)
            _steps.append(_step3)
            _steps.append(_step4)
            _steps.append(_step5)
            _list = ui_list_element(_steps, ordered=True)

            _ui_basic_block.addBasicElement(_text1)
            _ui_basic_block.addBasicElement(_text2)
            _ui_basic_block.addBasicElement(_list)
            # _ui_basic_block.addBasicElement(_text3)
            res.append(_ui_basic_block)

            ########################################################################################
            ############################################  File Upload form
            _ui_form_block = ui_form_block(block_title='Submit the Grades Excel File for a given Section',
                                           form_action=self.link, form_id='test', form_method='POST')

            _meetings_list = {}
            for _meeting in Meeting.objects.filter(semester=_actual_semester, teacher=_actual_user):
                # TODO filter section that where successfuly uploaded
                # look for a gradeFile with the same section code.
                try:
                    _report_tmp = GradesFile.objects.get(semester=_actual_semester, teacher=_actual_user,
                                                         section_courseObj=_meeting.course,
                                                         section_code=_meeting.section)
                except:
                    _meetings_list[
                        str(_meeting.meeting_id)] = f'{_meeting.course.course_code} {_meeting.course.course_name}  (section {_meeting.section})'

            if len(_meetings_list) > 0:

                _meeting = form_field('Section', 'meeting_id', input_type=FormInputTypeEnum.SELECT_INPUT,
                                      size=100, maxlength=100, list_data=_meetings_list,
                                      is_required=True, is_readonly=False)

                _file_field = form_field('The Grades Excel File', 'gradesfile', input_type=FormInputTypeEnum.FILE_INPUT)

                _submit_field = form_field('Submit the Grade File', 'Submit the Grade File',
                                           input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                           button_class=ButtonClassEnum.BTN_SUCCESS)
                _cancel_field = form_field('Cancel', 'Cancel',
                                           input_type=FormInputTypeEnum.RESET_INPUT,
                                           button_class=ButtonClassEnum.BTN_SECONDARY)

                _ui_form_block.addFormField(_meeting)
                _ui_form_block.addFormField(_file_field)
                _ui_form_block.addFormField(_submit_field)
                _ui_form_block.addFormField(_cancel_field)
                res.append(_ui_form_block)

            else:
                _report = ui_basic_block(block_title='')
                _h1 = ui_text_element(
                    text='All your sections are handled.',
                    alignment=UI_TEXT_ALIGNMENT_Enum.CENTER,
                    color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                    heading=UI_TEXT_HEADING_Enum.H3)
                _report.addBasicElement(_h1)
                res.append(_report)

        return res
