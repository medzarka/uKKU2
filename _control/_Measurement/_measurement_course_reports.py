# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from _control.AbstractPage import Abstract_UI_Page
from _control._Measurement.Measurement_tools import Section_Measurment, Course_Measurment
from _data._data_academic_program import Course
from _data._data_measurement import GradesFile, ReportState, CourseFile
from _data._data_periods import Semester
from _data._data_schedule import Meeting
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_text_element, UI_TEXT_COLOR_Enum, UI_TEXT_BG_Enum, \
    UI_Text_BADGE_Type, UI_TEXT_ALIGNMENT_Enum, UI_Text_Alert_Type, UI_TEXT_HEADING_Enum, ui_list_element, \
    ui_table_element, UI_Row_Cell_Class_Enum, table_row, table_cell, UI_IMAGE_ALIGNMENT_Enum, ui_image_element
from _web.UI.UI_FORM_Element import ui_form_block, form_field, FormInputTypeEnum, ButtonClassEnum


class _page_generate_course_reports(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Measurement :: Generate Measurement Course Reports', link=link,
                         request_obj=request)

    def CreateBlocks(self, _blocks_list=None):
        _actual_semester = Semester.objects.get(semester_id=self.request_obj.session['selected_semester'])
        _actual_user = User.objects.get(id=self.request_obj.user.id)
        res = []

        ###################################################################################
        ###################################################################################
        #################   STEP 3 - Generate and submit the report
        if self.request_obj.method == 'POST' and 'Analysis' in self.request_obj.POST and 'Department' in self.request_obj.POST \
                and 'id' in self.request_obj.POST:

            _report = ui_basic_block(block_title='Measurement Course Report')
            _analysis = self.request_obj.POST['Analysis']
            _department = self.request_obj.POST['Department']
            _id = int(self.request_obj.POST['id'])

            try:
                _course_report = CourseFile.objects.get(course_file_id=_id)
                _course_report.teacher_analysis = _analysis
                _course_report.section_department = _department
                _course_report.save()
                _tool = Course_Measurment(course_file_obj=_course_report)
                if _tool.generate_report():
                    _course_report.report_state = ReportState.CREATED.value
                    _course_report.save()
                    _h1 = ui_text_element(
                        text='Done. The report is Generated and Submitted.',
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

            _ui_form_block = ui_form_block(block_title='',
                                           form_action=self.link, form_id='test', form_method='GET')
            _submit_field = form_field('Back to the submission pgae', 'Back to the submission page',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_PRIMARY)
            _ui_form_block.addFormField(_submit_field)
            res.append(_ui_form_block)

        ###################################################################################
        ###################################################################################
        #################   STEP 2 - Statistics Display/edit
        elif (self.request_obj.method == 'POST' and 'id' in self.request_obj.POST.keys()) or (
                self.request_obj.method == 'GET' and 'editmode' in self.request_obj.GET.keys()):

            ########################################## Alerts
            _ui_basic_block = ui_basic_block(block_title='')

            ######################################################################################
            __edit_mode = False
            __readonly_mode = False
            __add_mode = False

            if self.request_obj.method == 'GET':
                _id = int(self.request_obj.GET['id'])
                _mode = int(self.request_obj.GET['editmode'])
                if _mode == 0:
                    __edit_mode = True
                else:
                    __readonly_mode = True
                __report = CourseFile.objects.get(course_file_id=_id)
                _course_name = __report.course_name
                _department = __report.course_department
                _course_grades_files = GradesFile.objects.filter(course_name=_course_name, semester=_actual_semester)

            if self.request_obj.method == 'POST':
                __add_mode = True
                _id = int(self.request_obj.POST['id'])
                _course_name = GradesFile.objects.get(grades_file_id=_id).course_name
                _course_grades_files = GradesFile.objects.filter(course_name=_course_name, semester=_actual_semester)
                _department = _course_grades_files[0].section_department

            _measurement = Course_Measurment(_grades_files_objs=_course_grades_files, course_name=_course_name,
                                             user=_actual_user, semester=_actual_semester,
                                             department=_department)
            CourseFile_obj = _measurement.create_Update_Course_report()

            ___is_required = False
            ___is_readonly = True

            if __add_mode:
                ___is_required = True
                ___is_readonly = False

            if __edit_mode:
                ___is_required = True
                ___is_readonly = False
            ######################################################################################

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

            if _measurement.dataloaded or __edit_mode or __readonly_mode:

                #########################################

                ########################################## Stats
                _statistics = _measurement.getStatistics()
                _stats = ui_basic_block(block_title='Statistic Results')

                if _statistics is None:
                    _text = ui_text_element(
                        text='Internal Error. The report model is not found or could not be saved',
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_WARNING,
                        background=UI_TEXT_BG_Enum.NONE, alert=UI_Text_Alert_Type.ALERT_DANGER)
                    _stats.addBasicElement(_text)

                else:

                    _h1 = ui_text_element(
                        text='Statistic values',
                        alignment=UI_TEXT_ALIGNMENT_Enum.LEFT,
                        color=UI_TEXT_COLOR_Enum.TEXT_SUCCESS,
                        heading=UI_TEXT_HEADING_Enum.H4)
                    _stats.addBasicElement(_h1)

                    _steps = []
                    _steps.append(ui_text_element(
                        text='Section Location : \t ' + CourseFile_obj.campus_name,
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Course Name : \t' + CourseFile_obj.course_name,
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Section Codes : \t' + str(CourseFile_obj.section_codes),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Mean : \t' + str(CourseFile_obj.stat_mean),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Standard Deviation : \t' + str(CourseFile_obj.stat_std),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Skewness : \t' + str(CourseFile_obj.stat_skewness),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Correlation between Mids/Finals : \t' + str(CourseFile_obj.stat_correlation_value),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Correlation between Sig. : \t' + str(CourseFile_obj.stat_correlation_sig),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Min : \t' + str(CourseFile_obj.stat_min),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Max : \t' + str(CourseFile_obj.stat_max),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Sections Correlation Type (Annova/TTEST) : \t' + str(
                            CourseFile_obj.stat_ttest_annova),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Annova/TTEST Value : \t' + str(CourseFile_obj.stat_ttest_annova_value),
                        alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                        color=UI_TEXT_COLOR_Enum.TEXT_DARK))
                    _steps.append(ui_text_element(
                        text='Annova/TTEST Sig. : \t' + str(CourseFile_obj.stat_ttest_annova_sig),
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

                    _hist = ui_image_element(image_url=CourseFile_obj.stat_histogram.url, image_alt='Histogram',
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
                        text=CourseFile_obj.stat_analysis,
                        alignment=UI_TEXT_ALIGNMENT_Enum.LEFT)
                    _stats.addBasicElement(tips)

                    _ui_form_block = ui_form_block(block_title='Generate Measurement Section Report',
                                                   form_action=self.link, form_id='test', form_method='POST')

                    if CourseFile_obj.course_department == None:
                        _department_content = ''
                    else:
                        _department_content = CourseFile_obj.course_department.department_name
                    _department = form_field('Department', 'Department', input_type=FormInputTypeEnum.TEXT_INPUT,
                                             input_value=_department_content, size=100,
                                             maxlength=100,
                                             placeholder='Type here your department',
                                             is_readonly=True)

                    if CourseFile_obj.teacher_analysis == None:
                        _analyse_content = ''
                    else:
                        _analyse_content = CourseFile_obj.teacher_analysis

                    _analysis = form_field('Analysis', 'Analysis', input_type=FormInputTypeEnum.TEXTAREA_INPUT,
                                           input_value=_analyse_content, size=100,
                                           maxlength=2048,
                                           placeholder='Type here your analysis',
                                           is_required=___is_required, is_readonly=___is_readonly)

                    _doc_id = form_field('id', 'id', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                         input_value=str(CourseFile_obj.course_file_id), is_required=True)

                    _submit_field = form_field('Generate Section Report', 'Generate Section Report',
                                               input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                               button_class=ButtonClassEnum.BTN_SUCCESS)
                    _cancel_field = form_field('Cancel', 'Cancel',
                                               input_type=FormInputTypeEnum.RESET_INPUT,
                                               button_class=ButtonClassEnum.BTN_SECONDARY)

                    _ui_form_block.addFormField(_department)
                    _ui_form_block.addFormField(_analysis)
                    _ui_form_block.addFormField(_doc_id)

                    if __edit_mode or __add_mode:
                        _ui_form_block.addFormField(_submit_field)
                        _ui_form_block.addFormField(_cancel_field)
                    res.append(_ui_form_block)

                    ##########################################################################################
                    if len(CourseFile_obj.getRemarks()) > 0:
                        __histories = ui_basic_block(block_title='Review History')

                        _history = []
                        for row in CourseFile_obj.getRemarks():
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
        elif self.request_obj.method == 'GET':
            ##### my reports list :

            if 'action' in self.request_obj.GET.keys() and 'id' in self.request_obj.GET.keys():
                try:
                    _id = int(self.request_obj.GET['id'])
                    _action = self.request_obj.GET['action']
                    _report = CourseFile.objects.get(course_file_id=_id)
                    if _action == 'submit':
                        try:
                            _reviewer_email = MeasurementReviewerAffectations.object.get(semester=_actual_semester,
                                                                                         user=_actual_user).reviewer.email
                        except:
                            _reviewer_email = ''
                        _report.submit(update=True, reviewer_email=_reviewer_email)
                    if _action == 'delete':
                        _report.end()
                except _report.DoesNotExist:
                    pass

            _list = CourseFile.objects.filter(teacher=_actual_user, semester=_actual_semester)
            if len(_list) > 0:
                _ui_table_block = ui_basic_block(block_title='List of my Course Reports')

                _rows = []

                for _report in _list:
                    if _report.report_state == ReportState.ACCEPTED.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
                    if _report.report_state == ReportState.SUBMITTED.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
                    if _report.report_state == ReportState.NEEDS_REVIEW.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                    if _report.report_state == ReportState.CREATED.value:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.NONE)

                    _text1 = ui_text_element(text=str(_report.course_file_id), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)
                    _text1 = ui_text_element(text=str(_report.campus_name), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)
                    _text1 = ui_text_element(text=str(_report.section_codes), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)
                    _text1 = ui_text_element(text=_report.course_department, color=UI_TEXT_COLOR_Enum.TEXT_DARK)
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
                        _rev = ''
                    else:
                        _rev = _report.reviewer.first_name
                    _text1 = ui_text_element(text=_rev,
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_report.version),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    try:
                        _text1 = ui_text_element(text='Download',
                                                 color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                                 link_url=_report.report_file.url,
                                                 alert=UI_Text_Alert_Type.ALERT_INFO)
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                    except ValueError:
                        _text1 = ui_text_element(text='')
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                    if _report.report_state == ReportState.CREATED.value:
                        _params = {}
                        _params['id'] = _report.course_file_id
                        _params['course_name'] = _report.course_name
                        _params['action'] = 'submit'
                        _text10 = ui_text_element(text='Submit', alert=UI_Text_Alert_Type.ALERT_PRIMARY,
                                                  link_url=self.link, link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _params = {}
                        _params['id'] = _report.course_file_id
                        _params['course_name'] = _report.course_name
                        _params['editmode'] = '0'
                        _text10 = ui_text_element(text='Edit', alert=UI_Text_Alert_Type.ALERT_WARNING,
                                                  color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                  link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _params = {}
                        _params['id'] = _report.course_file_id
                        _params['course_name'] = _report.course_name
                        _params['action'] = 'delete'
                        _text20 = ui_text_element(text='Delete', alert=UI_Text_Alert_Type.ALERT_DANGER,
                                                  link_url=self.link, link_parameter=_params)
                        _cell20 = table_cell(cell_centent=_text20)
                        _row.add_cell_to_row(_cell20)
                    elif _report.report_state == ReportState.NEEDS_REVIEW.value:

                        _text3 = ui_text_element(text='', badge=UI_Text_BADGE_Type.NONE,
                                                 color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=_report.report_file.url)
                        _cell3 = table_cell(cell_centent=_text3)
                        _row.add_cell_to_row(_cell3)

                        _params = {}
                        _params['id'] = _report.course_file_id
                        _params['course_name'] = _report.course_name
                        _params['editmode'] = '0'
                        _text10 = ui_text_element(text='Edit', alert=UI_Text_Alert_Type.ALERT_DANGER,
                                                  color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                  link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _text3 = ui_text_element(text='', badge=UI_Text_BADGE_Type.NONE,
                                                 color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=_report.report_file.url)
                        _cell3 = table_cell(cell_centent=_text3)
                        _row.add_cell_to_row(_cell3)

                    else:
                        _text3 = ui_text_element(text='', badge=UI_Text_BADGE_Type.NONE,
                                                 color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=_report.report_file.url)
                        _cell3 = table_cell(cell_centent=_text3)
                        _row.add_cell_to_row(_cell3)

                        _params = {}
                        _params['id'] = _report.course_file_id
                        _params['course_name'] = _report.course_name
                        _params['editmode'] = '1'
                        _text10 = ui_text_element(text='Details', alert=UI_Text_Alert_Type.ALERT_PRIMARY,
                                                  color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=self.link,
                                                  link_parameter=_params)
                        _cell10 = table_cell(cell_centent=_text10)
                        _row.add_cell_to_row(_cell10)

                        _text3 = ui_text_element(text='', badge=UI_Text_BADGE_Type.NONE,
                                                 color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url=_report.report_file.url)
                        _cell3 = table_cell(cell_centent=_text3)
                        _row.add_cell_to_row(_cell3)

                    _rows.append(_row)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=['Report ID', 'Location', 'Sections', 'Department',
                                                        'Course Name',
                                                        'State', 'Submission Time', 'Reviewer', 'Version', 'Report', '',
                                                        '', ''],
                                          table_has_footer=False,
                                          table_is_striped=True,
                                          table_is_hover=True, table_is_bordered=True)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

            _ui_basic_block = ui_basic_block(block_title='Instructions for Measurement Report Generation')
            _text1 = ui_text_element(
                text='The actual page helps faculties to generate measurement report for a given course based on section report already submitted and validated.',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.NONE)

            _text2 = ui_text_element(text='Please follow these steps to generate your course measurement report:',
                                     alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                     background=UI_TEXT_BG_Enum.TEXT_WHITE)

            _steps = []

            _step1 = ui_text_element(
                text='In the form below, select the course name. Only courses with more than one section will be displayed.',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)
            _step2 = ui_text_element(
                text='Click on the button "Select the Course",',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.TEXT_WHITE, badge=UI_Text_BADGE_Type.NONE)
            _step3 = ui_text_element(
                text='The system will computes the different statistical measurement and display them. You are asked then to type your analysis,',
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
            _steps.append(_step5)
            _list = ui_list_element(_steps, ordered=True)

            _ui_basic_block.addBasicElement(_text1)
            _ui_basic_block.addBasicElement(_text2)
            _ui_basic_block.addBasicElement(_list)
            # _ui_basic_block.addBasicElement(_text3)
            res.append(_ui_basic_block)

            ########################################################################################
            ############################################  Course Selection form

            __list_GradesFiles = []
            __list_sections_with_more_than_two_sections = {}
            _work_withCourses = False

            __list_courses = Course.objects.all()
            for _course in __list_courses:
                __list_meetings = Meeting.objects.filter(semester=_actual_semester, course=_course)
                if len(__list_meetings) > 1:

                    for _meeting in __list_meetings:
                        _section_code = _meeting.section
                        _section_campus = f'{_meeting.campus.campus_name}'
                        __list_Section_Reports = GradesFile.objects.filter(semester=_actual_semester,
                                                                           section_code=_section_code,
                                                                           campus_name=_section_campus)

                        print(
                            f'Looking for a section report with semester ={_actual_semester}, section code={_section_code}, and campus = {_section_campus} ')
                        if len(__list_Section_Reports) > 1:
                            __list_sections_with_more_than_two_sections[_course] = []
                            for _report in __list_Section_Reports:
                                print(f'####  --> course = {_course}')
                                __list_sections_with_more_than_two_sections[_course].append(_report.teacher)
                                __list_GradesFiles.append(_report)

                                if _actual_user.username == _report.teacher.username:
                                    _work_withCourses = True
            print(__list_sections_with_more_than_two_sections)
            if _work_withCourses:
                _ui_form_block = ui_form_block(block_title='Select the Course name',
                                               form_action=self.link, form_id='test', form_method='POST')
                _data = {}
                for _course in __list_sections_with_more_than_two_sections.keys():
                    _data[str(_report.grades_file_id)] = _course.course_code + ' ----' + _course.course_name

                _select_field = form_field('The Course Name', 'id',
                                           input_type=FormInputTypeEnum.SELECT_INPUT, list_data=_data)

                _submit_field = form_field('Select the Course', 'Select the Course',
                                           input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                           button_class=ButtonClassEnum.BTN_SUCCESS)
                _cancel_field = form_field('Cancel', 'Cancel',
                                           input_type=FormInputTypeEnum.RESET_INPUT,
                                           button_class=ButtonClassEnum.BTN_SECONDARY)

                _ui_form_block.addFormField(_select_field)
                _ui_form_block.addFormField(_submit_field)
                _ui_form_block.addFormField(_cancel_field)
                res.append(_ui_form_block)
            else:
                _report = ui_basic_block(block_title='')
                _h1 = ui_text_element(
                    text='You have no courses with more than one section.',
                    alignment=UI_TEXT_ALIGNMENT_Enum.CENTER,
                    color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                    heading=UI_TEXT_HEADING_Enum.H3)
                _report.addBasicElement(_h1)
                res.append(_report)
        return res
