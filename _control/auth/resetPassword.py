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

from _web.models import main_site, footer


class _reset_password_page:
    def __init__(self, request, link):
        self.request_obj = request
        self.page_link = link
        self.context = {}

        _site = main_site.objects.order_by('-site_id')[0]
        self.context['site_name_en'] = _site.site_name_en
        self.context['site_short_name_en'] = _site.site_short_name_en
        self.context['site_name_ar'] = _site.site_name_ar
        self.context['site_short_name_ar'] = _site.site_short_name_ar
        self.context['site_name_link'] = _site.site_name_link
        self.context['site_logo'] = _site.site_logo

        _footer = footer.objects.order_by('-footer_id')[0]
        self.context['footer_text_en'] = _footer.footer_text_en
        self.context['footer_text_ar'] = _footer.footer_text_ar
        self.context['footer_year'] = _footer.footer_year
        self.context['footer_version'] = _footer.footer_version
        self.context['footer_address_en'] = _footer.footer_address_en
        self.context['footer_address_ar'] = _footer.footer_address_ar
        self.context['footer_logo'] = _footer.footer_logo


    def getContext(self):
        return self.context
