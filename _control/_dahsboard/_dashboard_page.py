# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from _control.AbstractPage import Abstract_UI_Page

from _data._data_periods import Semester
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_text_element, UI_TEXT_COLOR_Enum, UI_TEXT_BG_Enum, \
    UI_Text_BADGE_Type, UI_TEXT_ALIGNMENT_Enum, UI_Text_Alert_Type, UI_TEXT_HEADING_Enum, ui_list_element, \
    ui_table_element, UI_Row_Cell_Class_Enum, table_row, table_cell, UI_IMAGE_ALIGNMENT_Enum, ui_image_element
from _web.UI.UI_FORM_Element import ui_form_block, form_field, FormInputTypeEnum, ButtonClassEnum

from _data._data_quality import Course_CFI
from _data._data_quality import ReviewerAffectations
from _data._data_measurement import GradesFile
from _data._data_measurement import ReportState

from _data._data_schedule import Meeting
from _data._data_dashboard import Link


class _dashboard(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Dashboard', link=link,
                         request_obj=request)

    def CreateBlocks(self, _blocks_list=None):
        _actual_semester = Semester.objects.get(semester_id=self.request_obj.session['selected_semester'])
        _actual_user = User.objects.get(id=self.request_obj.user.id)
        res = []

        ###################################################################################
        ###################################################################################
        #################   STEP 1 - List of my meetings

        _my_meetings = Meeting.objects.filter(semester=_actual_semester, teacher=_actual_user)
        _ui_table_block = ui_basic_block(block_title='List of my sections')

        _rows = []

        for _meeting in _my_meetings:
            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_LIGHT)

            _text1 = ui_text_element(text=str(_meeting.section), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)

            _text1 = ui_text_element(text=f'{_meeting.course.course_code}-{_meeting.course.course_name}',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)

            _text1 = ui_text_element(text=str(_meeting.department), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)

            _text1 = ui_text_element(text=str(_meeting.campus), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)

            try:
                _measurementReport = GradesFile.objects.get(section_courseObj=_meeting.course,
                                                            semester=_actual_semester, section_code=_meeting.section)

                _color = UI_TEXT_BG_Enum.NONE
                if _measurementReport.report_state == ReportState.CREATED.value:
                    _color = UI_TEXT_BG_Enum.TEXT_SECONDARY
                if _measurementReport.report_state == ReportState.SUBMITTED.value:
                    _color = UI_TEXT_BG_Enum.TEXT_PRIMARY
                if _measurementReport.report_state == ReportState.NEEDS_REVIEW.value:
                    _color = UI_TEXT_BG_Enum.TEXT_WARNING
                if _measurementReport.report_state == ReportState.ACCEPTED.value:
                    _color = UI_TEXT_BG_Enum.TEXT_SUCCESS

                _text1 = ui_text_element(text=_measurementReport.getReviewstate(), color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                         background=_color)
                _cell1 = table_cell(cell_centent=_text1)
                _row.add_cell_to_row(_cell1)
            except:
                _text1 = ui_text_element(text='Not Uploaded', color=UI_TEXT_COLOR_Enum.TEXT_LIGHT,
                                         background=UI_TEXT_BG_Enum.TEXT_DANGER)
                _cell1 = table_cell(cell_centent=_text1)
                _row.add_cell_to_row(_cell1)

            try:
                _measurementReport = GradesFile.objects.get(section_courseObj=_meeting.course,
                                                            semester=_actual_semester, section_code=_meeting.section)
                _qualityReport = Course_CFI.objects.get(gradeFile=_measurementReport,
                                                        gradeFile__semester=_actual_semester)

                _color = UI_TEXT_BG_Enum.NONE
                if _qualityReport.cfi_report_state == ReportState.CREATED.value:
                    _color = UI_TEXT_BG_Enum.TEXT_SECONDARY
                if _qualityReport.cfi_report_state == ReportState.SUBMITTED.value:
                    _color = UI_TEXT_BG_Enum.TEXT_PRIMARY
                if _qualityReport.cfi_report_state == ReportState.NEEDS_REVIEW.value:
                    _color = UI_TEXT_BG_Enum.TEXT_WARNING
                if _qualityReport.cfi_report_state == ReportState.ACCEPTED.value:
                    _color = UI_TEXT_BG_Enum.TEXT_SUCCESS

                _text1 = ui_text_element(text=_qualityReport.getReviewstate(), color=UI_TEXT_COLOR_Enum.TEXT_DARK,
                                         background=_color)
                _cell1 = table_cell(cell_centent=_text1)
                _row.add_cell_to_row(_cell1)
            except Exception as e:
                _text1 = ui_text_element(text='Not Uploaded', color=UI_TEXT_COLOR_Enum.TEXT_LIGHT,
                                         background=UI_TEXT_BG_Enum.TEXT_DANGER)
                _cell1 = table_cell(cell_centent=_text1)
                _row.add_cell_to_row(_cell1)

            _rows.append(_row)

        _table = ui_table_element(table_rows=_rows,
                                  table_header=['Section', 'Course', 'Department',
                                                'Campus', 'Measurement Status', 'Quality Status', ],
                                  table_has_footer=False,
                                  table_is_striped=True,
                                  table_is_hover=True, table_is_bordered=True)
        _ui_table_block.addBasicElement(_table)
        res.append(_ui_table_block)

        ###################################################################################
        ###################################################################################
        #################   STEP 2 - List of links

        _my_links = Link.objects.filter(link_semester=_actual_semester)
        _ui_table_block = ui_basic_block(block_title='Links')

        _rows = []

        for _link in _my_links:
            _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_LIGHT)

            _text1 = ui_text_element(text=f'{_link.link_description}',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)

            _text1 = ui_text_element(text=f'{_link.link_time}',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)

            _text1 = ui_text_element(text=f'Click to view',
                                     color=UI_TEXT_COLOR_Enum.TEXT_DARK, link_url=_link.link_url)
            _cell1 = table_cell(cell_centent=_text1)
            _row.add_cell_to_row(_cell1)

            _rows.append(_row)

        _table = ui_table_element(table_rows=_rows,
                                  table_header=['Description', 'Upload Time', 'Link URL', ],
                                  table_has_footer=False,
                                  table_is_striped=True,
                                  table_is_hover=True, table_is_bordered=True)
        _ui_table_block.addBasicElement(_table)
        res.append(_ui_table_block)

        ###################################################################################
        ###################################################################################
        #################   STEP 3 - My progress

        # _progress = ui_basic_block(block_title='My Progress')

        # res.append(_progress)

        return res
