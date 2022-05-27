from abc import ABC, abstractmethod
from enum import Enum, unique


@unique
class UI_Block_Element_Type_Enum(Enum):
    BASIC_ELEMENT = 'basic'
    TEXT_ELEMENT = 'text'
    CARD_ELEMENT = 'card'
    DATATABLE_ELEMENT = 'datatable'
    FORM_ELEMENT = 'form'
    CALENDAR_ELEMENT = 'calendar'
    INFOTABLE_ELEMENT = 'infotable'


class Block_List:
    def __init__(self, page_title=''):
        self.elements = {}

    def addBlock(self, index, block):
        self.elements[index] = block

    def getBlocks(self):
        return self.elements


class Abstract_UI_Block(ABC):
    def __init__(self, block_title, UI_Block_Element_Type_Enum):
        self.block_title = block_title
        self.block_type = UI_Block_Element_Type_Enum

    @abstractmethod
    def toHTML(self):
        pass  # TODO  WORK on Title --> With or without block title
