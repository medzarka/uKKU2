# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group

from _control.AbstractPage import Abstract_UI_Page
from _data._data_measurement import GradesFile, ReportState, MeasurementReviewerAffectations
from _data._data_periods import Semester
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_text_element, UI_TEXT_COLOR_Enum, UI_TEXT_BG_Enum, \
    UI_Text_BADGE_Type, UI_TEXT_ALIGNMENT_Enum, UI_TEXT_HEADING_Enum, ui_table_element, UI_Row_Cell_Class_Enum, \
    table_row, table_cell, ui_list_element, UI_Text_Alert_Type
from _web.UI.UI_FORM_Element import ui_form_block, form_field, FormInputTypeEnum, ButtonClassEnum


class _measurement_section_reports_admin(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Measurement :: Section Reports Administration', link=link,
                         request_obj=request)

    def CreateBlocks(self, _blocks_list=None):

        _admin_group_name = 'MEASUREMENT'
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

            if 'selected_action' in self.request_obj.POST.keys() and 'selected_semester' in self.request_obj.POST.keys():
                _selected_semester = Semester.objects.get(
                    semester_id=int(self.request_obj.POST['selected_semester']))

            if 'action' in self.request_obj.GET.keys() and 'id' in self.request_obj.GET.keys():
                try:
                    _id = int(self.request_obj.GET['id'])
                    _action = self.request_obj.GET['action']
                    _report = GradesFile.objects.get(grades_file_id=_id)
                    if _action == 'refuse':
                        _report.refuse(_reviewer = _actual_user, semester=_actual_semester)
                    if _action == 'validate':
                        _report.validate(_reviewer = _actual_user, semester=_actual_semester)

                    if _action == 'review':
                        __reviewMode = True
                    if _action == 'remark':
                        __remark = self.request_obj.GET['remark']
                        __reviewer = self.request_obj.GET['reviewer']
                        _report.addRemark(__remark, __reviewer)
                        _report.save()

                except _report.DoesNotExist:
                    pass

            if __reviewMode:
                ##########################################################################################

                GradesFile_obj = GradesFile.objects.get(grades_file_id=_id)

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

                ################
                if GradesFile_obj.report_state == ReportState.SUBMITTED.value:
                    _ui_form_block = ui_form_block(block_title='Add New Review Remark',
                                                   form_action=self.link, form_id='test', form_method='GET')
                    _submit_field = form_field('Add the Remark',
                                               'Add the Remark',
                                               input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                               button_class=ButtonClassEnum.BTN_WARNING)

                    _doc_id = form_field('id', 'id', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                         input_value=str(GradesFile_obj.grades_file_id), is_required=True)
                    ___action = form_field('action', 'action', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                           input_value='remark', is_required=True)
                    ___reviewer = form_field('reviewer', 'reviewer', input_type=FormInputTypeEnum.HIDDEN_INPUT,
                                             input_value=_actual_user.last_name, is_required=True)

                    theremark = form_field('remark', 'remark', input_type=FormInputTypeEnum.TEXTAREA_INPUT,
                                           input_value='', size=100,
                                           maxlength=2048,
                                           placeholder='Type here your remark')

                    _ui_form_block.addFormField(___reviewer)
                    _ui_form_block.addFormField(___action)
                    _ui_form_block.addFormField(_doc_id)
                    _ui_form_block.addFormField(theremark)
                    _ui_form_block.addFormField(_submit_field)
                    res.append(_ui_form_block)

                ################

                _ui_form_block = ui_form_block(block_title='',
                                               form_action=self.link, form_id='test', form_method='GET')
                _submit_field = form_field('Go Back to the report list',
                                           'Go Back to the report list',
                                           input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                           button_class=ButtonClassEnum.BTN_PRIMARY)
                _ui_form_block.addFormField(_submit_field)
                res.append(_ui_form_block)

                ##########################################################################################
            else:

                _list = GradesFile.objects.filter(semester=_actual_semester)
                print('nbr of reports == ' + str(len(_list)))
                if len(_list) > 0:

                    _ui_table_block = ui_basic_block(block_title='List of Submitted Section Reports')

                    _rows = []

                    for _report in _list:
                        ## check her that the actual user (as a reviwer) could review the report
                        try:
                            affected_reviewer = MeasurementReviewerAffectations.objects.get(semester=_actual_semester,
                                                                                            user=_report.teacher)
                            if affected_reviewer.reviewer == None:
                                continue
                            if affected_reviewer.reviewer.id != _actual_user.id:
                                continue

                            if _report.report_state == ReportState.ACCEPTED.value:
                                _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
                            if _report.report_state == ReportState.SUBMITTED.value:
                                _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
                            if _report.report_state == ReportState.NEEDS_REVIEW.value:
                                _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                            if _report.report_state == ReportState.CREATED.value:
                                _row = table_row(row_class=UI_Row_Cell_Class_Enum.NONE)

                            _text1 = ui_text_element(text=str(_report.grades_file_id),
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)
                            _text1 = ui_text_element(text=str(_report.campus_name), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)
                            _text1 = ui_text_element(text=str(_report.section_code), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)
                            _text1 = ui_text_element(text=_report.section_department,
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)

                            _text1 = ui_text_element(text=_report.teacher.last_name,
                                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                            _cell1 = table_cell(cell_centent=_text1)
                            _row.add_cell_to_row(_cell1)

                            _text1 = ui_text_element(text=_report.getCourseFullName(),
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

                            try:
                                _text1 = ui_text_element(text='Report', alert=UI_Text_Alert_Type.ALERT_LIGHT,
                                                         color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                                         link_url=_report.report_file.url)
                                _cell1 = table_cell(cell_centent=_text1)
                                _row.add_cell_to_row(_cell1)
                                _rows.append(_row)

                            except ValueError:
                                _text1 = ui_text_element(text='')
                                _cell1 = table_cell(cell_centent=_text1)
                                _row.add_cell_to_row(_cell1)
                                _rows.append(_row)

                            if _report.is_submitted():
                                _params = {}
                                _params['id'] = _report.grades_file_id
                                _params['action'] = 'validate'
                                _text1 = ui_text_element(text='Validate', alert=UI_Text_Alert_Type.ALERT_SUCCESS,
                                                         link_url=self.link, link_parameter=_params)
                                _cell1 = table_cell(cell_centent=_text1)
                                _row.add_cell_to_row(_cell1)

                                _params = {}
                                _params['id'] = _report.grades_file_id
                                _params['action'] = 'refuse'
                                _text1 = ui_text_element(text='Reject', alert=UI_Text_Alert_Type.ALERT_DANGER,
                                                         link_url=self.link, link_parameter=_params)
                                _cell1 = table_cell(cell_centent=_text1)
                                _row.add_cell_to_row(_cell1)

                                _params = {}
                                _params['id'] = _report.grades_file_id
                                _params['action'] = 'review'
                                _text1 = ui_text_element(text='Remarks', alert=UI_Text_Alert_Type.ALERT_WARNING,
                                                         link_url=self.link, link_parameter=_params)
                                _cell1 = table_cell(cell_centent=_text1)
                                _row.add_cell_to_row(_cell1)


                            else:
                                _text1 = ui_text_element(text='')
                                _cell1 = table_cell(cell_centent=_text1)
                                _row.add_cell_to_row(_cell1)

                                _text1 = ui_text_element(text='')
                                _cell1 = table_cell(cell_centent=_text1)
                                _row.add_cell_to_row(_cell1)

                                _params = {}
                                _params['id'] = _report.grades_file_id
                                _params['action'] = 'review'
                                _text1 = ui_text_element(text='Remarks', alert=UI_Text_Alert_Type.ALERT_WARNING,
                                                         link_url=self.link, link_parameter=_params)
                                _cell1 = table_cell(cell_centent=_text1)
                                _row.add_cell_to_row(_cell1)
                        except MeasurementReviewerAffectations.DoesNotExist:
                            continue

                    _table = ui_table_element(table_rows=_rows,
                                              table_header=['ID', 'Location', 'Section', 'Department', 'Teacher',
                                                            'Course Name',
                                                            'Status', 'Submission Time', 'Report', '', '', ''],
                                              table_has_footer=False,
                                              table_is_striped=True,
                                              table_is_hover=True, table_is_bordered=True)
                    _ui_table_block.addBasicElement(_table)
                    res.append(_ui_table_block)



                else:
                    _ui_basic_block = ui_basic_block(block_title='No Section Reports')
                    _text1 = ui_text_element(
                        text='There are non section reports submitted for the ' + _actual_semester.semester_name + '.',
                        alignment=UI_TEXT_ALIGNMENT_Enum.CENTER,
                        color=UI_TEXT_COLOR_Enum.TEXT_PRIMARY,
                        background=UI_TEXT_BG_Enum.NONE,
                        heading=UI_TEXT_HEADING_Enum.H4)

                    _ui_basic_block.addBasicElement(_text1)

                    res.append(_ui_basic_block)

        else:

            ###################################################################################
            ###################################################################################
            ###################################################################################
            ###################################################################################
            #################   STEP 1 - Submission Page

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
