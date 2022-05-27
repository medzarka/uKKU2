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

from _data._data_schedule import Meeting



class _page_mycfis_reviewers(Abstract_UI_Page):
    def __init__(self, request, link):
        super().__init__(page_title='Quality :: CFI Reviewers Administration', link=link,
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
            #################   STEP 1 - Update the affectation

            _all_users = User.objects.all()
            for _user in _all_users:
                if _user.username == 'admin':
                    continue
                try:
                    ReviewerAffectations.objects.get(user=_user, semester=_actual_semester)
                except:
                    _tmp = ReviewerAffectations(user=_user, semester=_actual_semester, reviewer=None)
                    _tmp.save()

            ###################################################################################
            ###################################################################################
            #################   STEP 2 - Handle Affectation Update

            if self.request_obj.method == 'POST':
                _user_id = int(self.request_obj.POST['user'])
                _reviewer_id = int(self.request_obj.POST['reviewer'])
                _user = User.objects.get(id=_user_id)
                _reviewer = User.objects.get(id=_reviewer_id)
                _tmp = ReviewerAffectations.objects.get(user=_user, semester=_actual_semester)
                _tmp.reviewer = _reviewer
                _tmp.save()

            ###################################################################################
            ###################################################################################
            #################   STEP 3 - Display all the Affectations

            __actual__meetings = Meeting.objects.filter(semester=_actual_semester)
            __actual_teachers = {}
            for __meeting in __actual__meetings:
                __actual_teachers[__meeting.teacher] = ''

            _list = ReviewerAffectations.objects.filter(semester=_actual_semester)
            if len(_list) > 0:
                _ui_table_block = ui_basic_block(
                    block_title='Quality Reviewers Affectation')

                _rows = []

                for _affectation in _list:

                    if _affectation.user not in __actual_teachers.keys():
                        continue


                    if _affectation.reviewer is None:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_DANGER)
                    else:
                        _row = table_row(row_class=UI_Row_Cell_Class_Enum.TABLE_SUCCESS)

                    _text1 = ui_text_element(text=str(_affectation.user.first_name), color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    if _affectation.reviewer is None:
                        _text1 = ui_text_element(text='No reviewer Affected',
                                                 color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    else:
                        _text1 = ui_text_element(text=str(_affectation.reviewer.first_name),
                                                 color=UI_TEXT_COLOR_Enum.TEXT_DARK)
                    _cell1 = table_cell(cell_centent=_text1)
                    _row.add_cell_to_row(_cell1)

                    _rows.append(_row)

                _table = ui_table_element(table_rows=_rows,
                                          table_header=['Faculty Member', 'Quality Work Reviewed by:', ],
                                          table_has_footer=False,
                                          table_is_striped=True,
                                          table_is_hover=True, table_is_bordered=True)
                _ui_table_block.addBasicElement(_table)
                res.append(_ui_table_block)

            ###################################################################################
            ###################################################################################
            #################   STEP 4 - The Affectation Form

            _ui_form_block = ui_form_block(block_title='Update Affectations',
                                           form_action=self.link, form_id='test', form_method='POST')

            __user_data = {}
            __reviwers_data = {}
            head_group = Group.objects.get(name=_reviewers_group_name)

            for _aff in ReviewerAffectations.objects.filter(semester=_actual_semester).order_by('user'):
                __user_data[_aff.user.id] = _aff.user.first_name
                if head_group in _aff.user.groups.all():
                    __reviwers_data[_aff.user.id] = _aff.user.first_name

            _user_field = form_field('The Faculty Member', 'user',
                                     input_type=FormInputTypeEnum.SELECT_INPUT, list_data=__user_data)
            _reviewer_field = form_field('The Reviewer', 'reviewer',
                                         input_type=FormInputTypeEnum.SELECT_INPUT, list_data=__reviwers_data)

            _submit_field = form_field('Save/Update the Affectation', 'submit',
                                       input_type=FormInputTypeEnum.SUBMIT_INPUT,
                                       button_class=ButtonClassEnum.BTN_SUCCESS)
            _cancel_field = form_field('Cancel', 'Cancel',
                                       input_type=FormInputTypeEnum.RESET_INPUT,
                                       button_class=ButtonClassEnum.BTN_SECONDARY)

            _ui_form_block.addFormField(_user_field)
            _ui_form_block.addFormField(_reviewer_field)
            _ui_form_block.addFormField(_submit_field)
            _ui_form_block.addFormField(_cancel_field)
            res.append(_ui_form_block)





        else:

            ###################################################################################
            ###################################################################################
            ###################################################################################
            ###################################################################################
            #################

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
