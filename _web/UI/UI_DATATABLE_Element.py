from enum import Enum, unique

from _web.UI.UI_Abstract_Content import Abstract_UI_Block, UI_Block_Element_Type_Enum


class ui_datatable_block(Abstract_UI_Block):
    def __init__(self, block_title='', table_element=None):
        super().__init__(block_title, UI_Block_Element_Type_Enum=UI_Block_Element_Type_Enum.FORM_ELEMENT)
        self.table_element = table_element

    def SetTableElement(self, table_element):
        self.table_element = table_element

    @property
    def toHTML(self):
        pass  # TODO
