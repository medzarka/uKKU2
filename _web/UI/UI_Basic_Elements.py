from enum import Enum, unique
from abc import ABC, abstractmethod

####################################### ENUMERATIONS
from django.template.defaulttags import url, URLNode
from django.urls import reverse, NoReverseMatch

from _web.UI.UI_Abstract_Content import Abstract_UI_Block, UI_Block_Element_Type_Enum


@unique
class UI_Basic_Content_Enum(Enum):
    TEXT = 'text'
    LIST = 'list'
    IMAGE = 'image'
    TABLE = 'table'
    MODAL = 'modal'


@unique
class UI_TEXT_BG_Enum(Enum):
    NONE = ''
    TEXT_PRIMARY = 'bg-primary'
    TEXT_SECONDARY = 'bg-secondary'
    TEXT_SUCCESS = 'bg-success'
    TEXT_DANGER = 'bg-danger'
    TEXT_WARNING = 'bg-warning'
    TEXT_INFO = 'bg-info'
    TEXT_LIGHT = 'bg-light'
    TEXT_DARK = 'bg-dark'
    TEXT_WHITE = 'bg-white'


@unique
class UI_TEXT_COLOR_Enum(Enum):
    NONE = ''
    TEXT_PRIMARY = 'text-primary'
    TEXT_SECONDARY = 'text-secondary'
    TEXT_SUCCESS = 'text-success'
    TEXT_DANGER = 'text-danger'
    TEXT_WARNING = 'text-warning'
    TEXT_INFO = 'text-info'
    TEXT_LIGHT = 'text-light'
    TEXT_DARK = 'text-dark'
    TEXT_WHITE = 'text-white'


@unique
class UI_TEXT_ALIGNMENT_Enum(Enum):
    CENTER = 'text-center'
    LEFT = 'text-left'
    RIGHT = 'text-right'
    JUSTIFY = 'text-justify'


@unique
class UI_IMAGE_ALIGNMENT_Enum(Enum):
    LEFT = 'left'
    RIGHT = 'right'
    MIDDLE = 'middle'
    TOP = 'top'
    BUTTOM = 'bottom'


@unique
class UI_TEXT_HEADING_Enum(Enum):
    P = 'p'
    H1 = 'h1'
    H2 = 'h2'
    H3 = 'h3'
    H4 = 'h4'
    H5 = 'h5'
    H6 = 'h6'


@unique
class UI_Text_BADGE_Type(Enum):
    NONE = ''
    BADGE_PRIMARY = 'badge badge-primary'
    BADGE_SECONDARY = 'badge badge-secondary'
    BADGE_SUCCESS = 'badge badge-success'
    BADGE_DANGER = 'badge badge-danger'
    BADGE_WARNING = 'badge badge-warning'
    BADGE_INFO = 'badge badge-info'
    BADGE_LIGHT = 'badge badge-light'
    BADGE_DARK = 'badge badge-dark'
    BADGE_WHITE = 'badge badge-white'


@unique
class UI_Text_Alert_Type(Enum):
    NONE = ''
    ALERT_PRIMARY = 'alert alert-primary'
    ALERT_SECONDARY = 'alert alert-secondary'
    ALERT_SUCCESS = 'alert alert-success'
    ALERT_DANGER = 'alert alert-danger'
    ALERT_WARNING = 'alert alert-warning'
    ALERT_INFO = 'alert alert-info'
    ALERT_LIGHT = 'alert alert-light'
    ALERT_DARK = 'alert alert-dark'
    ALERT_WHITE = 'alert alert-white'


@unique
class UI_Row_Cell_Class_Enum(Enum):
    NONE = ''
    TABLE_ACTIVE = 'table-active'
    TABLE_PRIMARY = 'table-primary'
    TABLE_SECONDARY = 'table-secondary'
    TABLE_SUCCESS = 'table-success'
    TABLE_DANGER = 'table-danger'
    TABLE_WARNING = 'table-warning'
    TABLE_INFO = 'table-info'
    TABLE_LIGHT = 'table-light'
    TABLE_DARK = 'table-dark'


####################################### CLASSES block_title, UI_Block_Element_Type_Enum

class ui_basic_block(Abstract_UI_Block):
    def __init__(self, block_title='', ui_basic_elements=None):
        super().__init__(block_title, UI_Block_Element_Type_Enum=UI_Block_Element_Type_Enum.BASIC_ELEMENT)
        self.ui_basic_elements = ui_basic_elements

    def addBasicElement(self, ui_element):
        if self.ui_basic_elements == None:
            self.ui_basic_elements = []
        self.ui_basic_elements.append(ui_element)

    def nbr_elements(self):
        if self.ui_basic_elements == None:
            return 0
        return len(self.ui_basic_elements)

    @property
    def toHTML(self):
        tmp = ''
        for element in self.ui_basic_elements:
            tmp = tmp + '\n' + element.toHTML()
        return tmp


class ui_element(ABC):
    def __init__(self, ui_basic_content_type):
        self.ui_basic_content_type = ui_basic_content_type

    @abstractmethod
    def toHTML(self):
        pass


class ui_text_element(ui_element):

    def __init__(self, text='', isBold=False, isItalic=False, isUnderligned=False,
                 alignment=UI_TEXT_ALIGNMENT_Enum.JUSTIFY, color=UI_TEXT_COLOR_Enum.NONE,
                 background=UI_TEXT_BG_Enum.NONE, heading=UI_TEXT_HEADING_Enum.P, badge=UI_Text_BADGE_Type.NONE,
                 alert=UI_Text_Alert_Type.NONE, link_url='', link_parameter={}, link_to_new_tab=False,
                 isForModalWindow=False):
        super().__init__(UI_Basic_Content_Enum.TEXT)
        self.alignment = alignment
        self.color = color
        self.background = background
        self.text = text
        self.isBold = isBold
        self.isItalic = isItalic
        self.isUnderligned = isUnderligned
        self.heading = heading
        self.badge = badge
        self.alert = alert
        self.link_url = link_url
        self.link_parameter = link_parameter
        self.link_to_new_tab = link_to_new_tab
        self.isForModalWindow = isForModalWindow

    def toHTML(self):
        res = ''
        if self.alert != UI_Text_Alert_Type.NONE:
            res += '<div class="' + self.alert.value + '" role="alert">'
        res += '<' + self.heading.value + ' class="' + self.alignment.value + ' ' + self.color.value + ' ' + self.background.value + '">'
        if self.isBold:
            res += '<strong>'
        if self.isItalic:
            res += '<em>'
        if self.isUnderligned:
            res += '<u>'
        if self.badge != UI_Text_BADGE_Type.NONE:
            res += '<span class="' + self.badge.value + '">'

        if self.link_url != '':

            if self.isForModalWindow:
                res += f'<br><br><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{self.link_url}">{self.text}</button><br><br><br>'
            else:
                _params = ''
                if len(self.link_parameter.keys()) != 0:
                    _params += '?'
                    for key, value in self.link_parameter.items():
                        _params += str(key) + '=' + str(value) + '&'

                try:
                    res += '<a href="' + reverse(self.link_url, args=[], kwargs={},
                                                 current_app=None)[:-1] + _params + '">'
                except NoReverseMatch:
                    res += '<a href="' + self.link_url + _params + '" '
                    if self.link_to_new_tab:
                        res += 'target="_blank"'
                    res += '>'
        res += str(self.text)

        if self.link_url != '':
            res += '</a>'

        if self.badge != UI_Text_BADGE_Type.NONE:
            res += '</span>'
        if self.isUnderligned:
            res += '</u>'
        if self.isItalic:
            res += '</em>'
        if self.isBold:
            res += '</strong>'
        res += '</' + self.heading.value + '>'
        if self.alert != UI_Text_Alert_Type.NONE:
            res += '</div>'

        return res


class ui_list_element(ui_element):

    def __init__(self, items=[], ordered=False):
        super().__init__(UI_Basic_Content_Enum.LIST)
        self.items = items
        self.ordered = ordered

    def toHTML(self):
        list_key = 'ul'
        if self.ordered is True:
            list_key = 'ol'
        res = '<' + list_key + '>'
        for _item in self.items:
            res = res + '\n <li>' + _item.toHTML() + '</li>'
        res = res + '</' + list_key + '>'
        return res


class ui_modal_element(ui_element):

    def __init__(self, id, title, content):
        super().__init__(UI_Basic_Content_Enum.MODAL)
        self.title = title
        self.content = content
        self.id = id

    def toHTML(self):
        res = f'<div class="modal fade" id="{id}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">'
        res += '<div class="modal-dialog" role="document">'
        res += '<div class="modal-content">'
        res += '<div class="modal-header">'
        res += '<h5 class="modal-title" id="exampleModalLabel">Modal title</h5>'
        res += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">'
        res += '  <span aria-hidden="true">&times;</span>'
        res += '</button>'
        res += '</div>'
        res += '<div class="modal-body">'
        res += self.content.toHTML()
        res += '</div>'
        res += '<div class="modal-footer">'
        res += '<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>'
        res += '</div>'
        res += '</div>'
        res += '</div>'
        res += '</div>'
        return res


class ui_image_element(ui_element):

    def __init__(self, image_url, image_alt='', image_width='', image_height='',
                 image_alignment=UI_IMAGE_ALIGNMENT_Enum.MIDDLE):
        super().__init__(UI_Basic_Content_Enum.IMAGE)
        self.image_url = image_url
        self.image_alt = image_alt
        self.image_width = image_width
        self.image_height = image_height
        self.image_alignment = image_alignment

    def toHTML(self):
        res = '<img src="' + self.image_url + '" alt="' + self.image_alt + '" align="' + self.image_alignment.value + '"'
        if self.image_width != '':
            res += ' width="' + self.image_width + '"'
        if self.image_height != '':
            res += ' height="' + self.image_height + '"'
        res += '>'
        return res


class ui_table_element(ui_element):

    def __init__(self, table_rows=[], table_header=[], table_has_footer=False, table_is_striped=True,
                 table_is_hover=True, table_is_bordered=True):
        super().__init__(UI_Basic_Content_Enum.TABLE)
        self.table_rows = table_rows
        self.table_header = table_header
        self.table_has_footer = table_has_footer
        self.table_is_striped = table_is_striped
        self.table_is_hover = table_is_hover
        self.table_is_bordered = table_is_bordered

    def toHTML(self):
        res = '\n<div style="table table-sm" class="table-responsive">'
        res += '\n<table class="table '
        if self.table_is_striped:
            res += ' table-striped '
        if self.table_is_hover:
            res += ' table-hover '
        if self.table_is_bordered:
            res += ' table-bordered '
        res += '" width="100%">'

        if len(self.table_header) != 0:
            res += '\n<thead class="thead-dark">\n<tr>'
            for cell_text in self.table_header:
                res += '\n<th>' + cell_text + '</th>'
            res += '\n</tr>\n</thead>'

        if self.table_has_footer:
            res += '\n<tfoot class="thead-dark">\n<tr>'
            for cell_text in self.table_header:
                res += '\n<th>' + cell_text + '</th>'
            res += '\n</tr>\n</tfoot>'

        for row in self.table_rows:
            res += row.toHTML()

        res += '\n</table>'

        res += '\n</div>'
        return res


class table_row:
    def __init__(self, row_class=UI_Row_Cell_Class_Enum.NONE):
        self.row_class = row_class
        self.cells = []

    def add_cell_to_row(self, cell):
        self.cells.append(cell)

    def toHTML(self):
        res = '\n<tr class="' + self.row_class.value + '">'
        for cell in self.cells:
            res += '\n' + cell.toHTML()
        res += '\n</tr>'
        return res


class table_cell:
    def __init__(self, cell_centent='', cell_class=UI_Row_Cell_Class_Enum.NONE):
        self.cell_class = cell_class
        self.cell_centent = cell_centent

    def toHTML(self):
        res = '\n<td class="' + self.cell_class.value + '">'
        res += '\n' + self.cell_centent.toHTML()
        res += '\n</td>'
        return res
