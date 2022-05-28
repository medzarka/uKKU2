# -*- coding: utf-8 -*-
import os
import shutil

from django.contrib.auth.models import User, Group

from _control.AbstractPage import Abstract_UI_Page

from _data._data_measurement import Department
from _control._quality._quality_Archieve_Maker import QualityArchiveMakerThread
from _data._data_measurement import GradesFile, ReportState, CourseFile
from _data._data_periods import Semester
from _data._data_schedule import Meeting
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_text_element, UI_TEXT_COLOR_Enum, UI_TEXT_BG_Enum, \
    UI_Text_BADGE_Type, UI_TEXT_ALIGNMENT_Enum, UI_Text_Alert_Type, UI_TEXT_HEADING_Enum, ui_modal_element, \
    ui_table_element, UI_Row_Cell_Class_Enum, table_row, table_cell, UI_IMAGE_ALIGNMENT_Enum, ui_image_element
from _web.UI.UI_FORM_Element import ui_form_block, form_field, FormInputTypeEnum, ButtonClassEnum

from _data._data_quality import Course_CFI, ReviewerAffectations, QualityExportFile


class _page_quality_export(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Quality :: Quality Documents Statistics/Export', link=link,
                         request_obj=request)

    def getDiskSpaceInfo(self):

        total, used, free = shutil.disk_usage("/")
        _info = "Total: %d GiB" % (total // (2 ** 30)) + ', ' + "Used: %d GiB" % (
                used // (2 ** 30)) + ', ' "Free: %d GiB" % (free // (2 ** 30))
        return _info

    def CreateBlocks(self, _blocks_list=None):

        _admin_group_name = 'QUALITY_HEAD'
        _reviewers_group_name = 'QUALITY'
        _actual_semester = Semester.objects.get(semester_id=self.request_obj.session['selected_semester'])
        _actual_user = User.objects.get(id=self.request_obj.user.id)

        __modalWindows = {}

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

                        _export_file = QualityExportFile.objects.get(quality_export_file_id=_export_file_id)

                        try:
                            log_filename = _export_file.exec_trace_file.path
                            zip_filename = _export_file.export_file.path
                            os.remove(log_filename)
                            os.remove(zip_filename)
                        except ValueError as ee:
                            pass

                        _export_file.delete()

                    except QualityExportFile.DoesNotExist as e:
                        print(e)

            ###################################################################################

            #################################################################################################

            _list = QualityExportFile.objects.filter(semester=_actual_semester)

            _ui_table_block = ui_basic_block(
                block_title='List of Quality Work Export (' + self.getDiskSpaceInfo() + ')')

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

                    _text1 = ui_text_element(text=str(_doc.quality_export_file_id),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_doc.quality_type),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_doc.department.department_name),
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

                    # _text1 = ui_text_element(text='{}'.format(_doc.exec_trace),
                    #                         color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    # _cell1 = table_cell(cell_centent=_text1)
                    # _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text='{}'.format(_doc.exec_trace),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _modal = ui_modal_element('exec_trace', 'Log Trace  ', _text1)
                    __modalWindows['exec_trace'] = _modal

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

                    if _doc.state != 0 or QualityArchiveMakerThread.isActiveThread(
                            _doc.quality_export_file_id) == False:
                        _params = {}
                        _params['id'] = _doc.quality_export_file_id
                        _params['action'] = 'delete_export_file'
                        _text20 = ui_text_element(text='Delete', alert=UI_Text_Alert_Type.ALERT_DANGER,
                                                  link_url=self.link, link_parameter=_params)
                        _cell20 = table_cell(cell_centent=_text20)
                        _row.add_cell_to_row(_cell20)
                    else:
                        _text1 = ui_text_element(text='')
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                    try:

                        _text1 = ui_text_element(text='Log Trace',
                                                 color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                                 link_url=_doc.exec_trace_file.url,
                                                 alert=UI_Text_Alert_Type.ALERT_INFO)
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)
                    except ValueError:
                        _text1 = ui_text_element(text='No Log Trace')
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                    _rows.append(_row)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=['Id', 'Quality Type', 'Department', 'Status', 'Submitted By',
                                                        'Submission', 'Elapsed Time',
                                                        'Size', 'Export File', '', ''],
                                          table_has_footer=False,
                                          table_is_striped=True,
                                          table_is_hover=True, table_is_bordered=True)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

            _ui_form_block = ui_form_block(block_title='Export Quality Files',
                                           form_action='generate_zipped_quality_reports_list', form_id='test',
                                           form_method='POST')

            _selected_semester = form_field(input_label='', input_name='selected_semester',
                                            input_value=str(_actual_semester.semester_id),
                                            input_type=FormInputTypeEnum.HIDDEN_INPUT)

            _selected_action = form_field(input_label='', input_name='selected_action', input_value='report',
                                          input_type=FormInputTypeEnum.HIDDEN_INPUT)

            _data = {}
            for _dep in Department.objects.all():
                _data[str(_dep.department_id)] = _dep.department_name
            _select_department = form_field('The Department', 'department',
                                            input_type=FormInputTypeEnum.SELECT_INPUT, list_data=_data)

            _data = {}
            _data['cfr'] = 'Quality File Requirements'
            _data['cfi'] = 'Quality File Index'
            _select_quality = form_field('Course File Type', 'quality',
                                         input_type=FormInputTypeEnum.SELECT_INPUT, list_data=_data)

            _submit_field = form_field('Export', 'Generate zipped reports list',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_DANGER)

            _ui_form_block.addFormField(_selected_semester)
            _ui_form_block.addFormField(_selected_action)
            _ui_form_block.addFormField(_select_department)
            _ui_form_block.addFormField(_select_quality)
            _ui_form_block.addFormField(_submit_field)
            res.append(_ui_form_block)
            #################################################################################################

            ###################################################################################

            ###################################################################################
            #################   STEP 3 - Display all the Affectations

            _list = Course_CFI.objects.filter(gradeFile__semester=_actual_semester)
            _number_created = 0
            _number_submitted = 0
            _number_need_review = 0
            _number_accpted = 0

            _ui_table_block = ui_basic_block(
                block_title='List of stored quality documents')

            if len(_list) == 0:
                _text1 = ui_text_element(
                    text='There is not quality documents uploaded.',
                    alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                    color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                    background=UI_TEXT_BG_Enum.NONE,
                    heading=UI_TEXT_HEADING_Enum.H4)

                _ui_table_block.addBasicElement(_text1)

                res.append(_ui_table_block)

            else:

                _rows = []

                for _doc in _list:

                    if _doc.is_submitted():
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_PRIMARY)
                        _number_submitted += 1
                    elif _doc.is_refused():
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                        _number_need_review += 1
                    elif _doc.is_validated():
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
                        _number_accpted += 1
                    else:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_WARNING)
                        _number_created += 1

                    _text1 = ui_text_element(text=str(_doc.course_cfi_id), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_doc.gradeFile.campus_name), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_doc.gradeFile.section_department),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_doc.gradeFile.teacher.last_name),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_doc.gradeFile.section_code),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_doc.gradeFile.course_name),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=_doc.getReviewstate(), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=_doc.submission_time.strftime("%m/%d/%Y, %H:%M:%S"),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    if _doc.cfi_reviewer is not None:
                        _text1 = ui_text_element(text=str(_doc.cfi_reviewer.last_name),
                                                 color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)
                    else:
                        _text1 = ui_text_element(text='',
                                                 color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                        _cell1 = table_cell(cell_centent=_text1)
                        _row.add_cell_to_row(_cell1)

                    _text1 = ui_text_element(text=str(_doc.cfi_version),
                                             color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _rows.append(_row)

                    _params = {}
                    _params['course_cfi_id'] = _doc.course_cfi_id
                    _params['section_selected'] = _doc.gradeFile.grades_file_id
                    _params['editmode'] = '0'
                    _params['adminmode='] = '1'
                    _text10 = ui_text_element(text='View', alert=UI_Text_Alert_Type.ALERT_WARNING,
                                              color=UI_TEXT_COLOR_Enum.TEXT_WHITE, link_url='quality_mycfis',
                                              link_parameter=_params)
                    _cell10 = table_cell(cell_centent=_text10)
                    _row.add_cell_to_row(_cell10)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=['Id', 'Campus', 'Department', 'Faculty', 'Section', 'Course',
                                                        'Status', 'Submission', 'reviewer', 'Version', 'Actions'],
                                          table_has_footer=False,
                                          table_is_striped=True,
                                          table_is_hover=True, table_is_bordered=True)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

            ###################################################################################
            ###################################################################################
            #################   STEP 2 - The Statistics

            _ui_basic_block = ui_basic_block(block_title='Statistics')
            _text1 = ui_text_element(
                text=f'Total number of stored quality documents : {(_number_created + _number_submitted + _number_need_review + _number_accpted)}',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                background=UI_TEXT_BG_Enum.NONE,
                heading=UI_TEXT_HEADING_Enum.H4)

            _ui_basic_block.addBasicElement(_text1)

            _text1 = ui_text_element(
                text=f'\tDrafted --> {_number_created}',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_INFO,
                background=UI_TEXT_BG_Enum.NONE,
                heading=UI_TEXT_HEADING_Enum.H6)

            _ui_basic_block.addBasicElement(_text1)

            _text1 = ui_text_element(
                text=f'\tSubmitted (Under Review) --> {_number_submitted}',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_INFO,
                background=UI_TEXT_BG_Enum.NONE,
                heading=UI_TEXT_HEADING_Enum.H6)

            _ui_basic_block.addBasicElement(_text1)

            _text1 = ui_text_element(
                text=f'\tAccepted --> {_number_accpted}',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_INFO,
                background=UI_TEXT_BG_Enum.NONE,
                heading=UI_TEXT_HEADING_Enum.H6)

            _ui_basic_block.addBasicElement(_text1)

            _text1 = ui_text_element(
                text=f'\tNeeds Review --> {_number_need_review}',
                alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                color=UI_TEXT_COLOR_Enum.TEXT_INFO,
                background=UI_TEXT_BG_Enum.NONE,
                heading=UI_TEXT_HEADING_Enum.H6)

            _ui_basic_block.addBasicElement(_text1)

            res.append(_ui_basic_block)

            #################################################################################################

            # We print the course list and we check if the section report is well submitted

            _list = Meeting.objects.filter(semester=_actual_semester)

            _ui_table_block = ui_basic_block(
                block_title='Available Meeting Quality Reports ')

            if len(_list) == 0:
                _text1 = ui_text_element(
                    text='There is no Available Quality Reports.',
                    alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY,
                    color=UI_TEXT_COLOR_Enum.TEXT_DANGER,
                    background=UI_TEXT_BG_Enum.NONE,
                    heading=UI_TEXT_HEADING_Enum.H4)

                _ui_table_block.addBasicElement(_text1)

                res.append(_ui_table_block)

            else:

                _rows = []

                for _section in _list:

                    # here we have a meeting --> we look for the corresponding quality file

                    try:

                        _rep = Course_CFI.objects.get(gradeFile__semester=_actual_semester,
                                                      gradeFile__section_code=_section.section,
                                                      gradeFile__teacher=_section.teacher,
                                                      gradeFile__section_courseObj=_section.course)

                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)
                        _textToAdd = _rep.getReviewstate()

                    except Course_CFI.DoesNotExist:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                        _textToAdd = 'Not yet Uploaded'

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

        for id, content in __modalWindows.items():
            res.append(content)
            print(content.toHTML())
        return res
