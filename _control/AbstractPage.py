from abc import ABC, abstractmethod

from django.contrib.auth.models import User

from _data._data_periods import Semester
from _web.models import main_site, footer, menu_box, menu

from _web.UI.UI_Abstract_Content import UI_Block_Element_Type_Enum, Block_List, Abstract_UI_Block
from _web.UI.UI_Basic_Elements import UI_TEXT_BG_Enum, UI_TEXT_COLOR_Enum, UI_TEXT_ALIGNMENT_Enum, ui_list_element, \
    UI_TEXT_HEADING_Enum, UI_Text_BADGE_Type, UI_Text_Alert_Type
from _web.UI.UI_Basic_Elements import ui_basic_block, ui_element, ui_text_element


class Abstract_UI_Page(ABC):
    def __init__(self, page_title, link, request_obj):
        self.page_title = page_title
        self.request_obj = request_obj
        self.link = link

        self.context = {}
        self.BasicContext(self.request_obj)  # add basic context

        self.context['menu']
        self.context['blocks'] = self.CreateBlocks()

    @abstractmethod
    def CreateBlocks(self, request):
        pass  # add extra content to the page

    def getContext(self):
        return self.context

    def List2text(self, list, withNoOccurence=True):
        _str = ''

        if withNoOccurence:
            list = set(list)

            if len(list) > 0:
                _str += f'{list.pop()}'

            while len(list) > 0:
                _str += f', {list.pop()}'

        else:
            if len(list) > 0:
                _str += f'{list[0]}'
            if len(list) > 1:
                for _idx in range(1, len(list)+1):
                    _str = _str + f', {list[_idx]}'

        return _str

    def BasicContext(self, request):

        _actual_user = User.objects.get(id=self.request_obj.user.id)
        self.context['actual_user_name'] = _actual_user.last_name

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

        tmp = []
        for semester in Semester.objects.all().order_by('semester_date_start'):
            tt = {}
            tt[
                semester.semester_id] = semester.semester_academic_year.academic_year_name + ' | ' + semester.semester_name
            tmp.append(tt)
        self.context['semesters'] = tmp

        try:
            self.context['selected_semester'] = self.request_obj.session['selected_semester']
        except:
            try:
                self.request_obj.session['selected_semester'] = Semester.objects.get(semester_isInUse=True).semester_id
            except Semester.DoesNotExist:
                for _semester in Semester.objects.all():
                    if _semester.isActualSemester is True:
                        request.session['selected_semester'] = _semester.semester_id
                        break
        self.context['selected_semester'] = self.request_obj.session['selected_semester']

        tmp = []
        for _menu_box in menu_box.objects.all().order_by('-menu_box_order'):
            tt = {}
            tt['image'] = _menu_box.menu_box_logo.url
            tt['items'] = []
            for _menu_box_item in _menu_box.items.order_by('menu_box_item_order'):
                ttt = {}
                ttt['name'] = _menu_box_item.menu_box_item_name
                ttt['logo'] = _menu_box_item.menu_box_item_fontawesome
                ttt['link'] = _menu_box_item.menu_box_link
                tt['items'].append(ttt)
            tmp.append(tt)
        self.context['menu_boxes'] = tmp

        tmp = []
        for _menu in menu.objects.all().order_by('menu_order'):
            tmp.append(_menu)
        self.context['menu'] = tmp
        self.context['page_title'] = self.page_title
