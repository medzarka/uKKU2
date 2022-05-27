from enum import Enum, unique

from _web.UI.UI_Abstract_Content import Abstract_UI_Block, UI_Block_Element_Type_Enum


@unique
class ButtonClassEnum(Enum):
    BTN_PRIMARY = 'btn-primary'
    BTN_SECONDARY = 'btn-secondary'
    BTN_SUCCESS = 'btn-success'
    BTN_DANGER = 'btn-danger'
    BTN_WARNING = 'btn-warning'
    BTN_INFO = 'btn-info'
    BTN_LIGHT = 'btn-light'
    BTN_DARK = 'btn-dark'


@unique
class FormInputTypeEnum(Enum):
    TEXT_INPUT = 'text'
    SUBMIT_INPUT = 'submit'
    HIDDEN_INPUT = 'hidden'
    EMAIL_INPUT = 'email'
    TEXTAREA_INPUT = 'textarea'
    PASSWORD_INPUT = 'password'
    COLOR_INPUT = 'color'
    FILE_INPUT = 'file'
    DATE_INPUT = 'date'
    TIME_INPUT = 'time'
    WEEK_INPUT = 'week'
    DATETIMELOCAL_INPUT = 'datetime-local'
    MONTH_INPUT = 'month'
    RESET_INPUT = 'reset'
    SELECT_INPUT = 'select'

    BUTTON_INPUT = 'button'
    CHECKBOX_INPUT = 'checkbox'
    IMAGE_INPUT = 'image'
    NUMBER_INPUT = 'number'
    RADIO_INPUT = 'radio'
    RANGE_INPUT = 'range'
    SEARCH_INPUT = 'search'
    TEL_INPUT = 'tel'
    URL_INPUT = 'url'


class ui_form_block(Abstract_UI_Block):
    def __init__(self, block_title='', form_action='', form_id='', form_method='GET', ui_form_fields=None):
        super().__init__(block_title, UI_Block_Element_Type_Enum=UI_Block_Element_Type_Enum.FORM_ELEMENT)
        self.form_action = form_action
        self.form_id = form_id
        self.method = form_method
        self.ui_form_fields = ui_form_fields

    def addFormField(self, ui_form_field):
        if self.ui_form_fields == None:
            self.ui_form_fields = []
        self.ui_form_fields.append(ui_form_field)

    def nbr_Fields(self):
        if self.ui_form_fields == None:
            return 0
        return len(self.ui_form_fields)

    @property
    def toHTML(self):
        res = ''
        for field in self.ui_form_fields:
            res += '\n' + field.toHTML
        return res


class form_field:
    def __init__(self, input_label, input_name, input_type=FormInputTypeEnum.TEXT_INPUT, input_value='', size=30,
                 maxlength=30,
                 placeholder='',
                 is_readonly=False,
                 is_disabled=False, is_required=True, button_class=ButtonClassEnum.BTN_PRIMARY, list_data={}):
        self.input_label = input_label
        self.input_type = input_type
        self.input_name = input_name
        self.input_value = input_value
        self.size = str(size)
        self.maxlength = str(maxlength)
        self.placeholder = placeholder

        self.is_readonly = is_readonly
        self.is_disabled = is_disabled
        self.is_required = is_required

        self.button_class = button_class
        self.list_data = list_data

    @property
    def toHTML(self):
        res = ''
        if self.input_type == FormInputTypeEnum.TEXT_INPUT or self.input_type == FormInputTypeEnum.EMAIL_INPUT or \
                self.input_type == FormInputTypeEnum.PASSWORD_INPUT or self.input_type == FormInputTypeEnum.COLOR_INPUT or \
                self.input_type == FormInputTypeEnum.FILE_INPUT or self.input_type == FormInputTypeEnum.DATE_INPUT or \
                self.input_type == FormInputTypeEnum.TIME_INPUT or self.input_type == FormInputTypeEnum.WEEK_INPUT or \
                self.input_type == FormInputTypeEnum.DATETIMELOCAL_INPUT or self.input_type == FormInputTypeEnum.MONTH_INPUT:
            res += '\n<div class ="form-group" >'
            res += '\n  <label for ="' + self.input_name + '"><strong>' + self.input_label + '</strong></label>'
            res += '\n  <input type = "' + self.input_type.value + '" class ="form-control" id = "' + self.input_name + '" name = "' + self.input_name + '" '
            res += '        placeholder="' + self.placeholder + '" value="' + self.input_value + '" size="' + self.size + '" maxlength="' + self.maxlength + '"'
            if self.is_disabled:
                res += ' disabled '
            if self.is_readonly:
                res += ' readonly '
            if self.is_required:
                res += ' required '
            res += '>'
            res += '\n</div>'
        elif self.input_type == FormInputTypeEnum.SUBMIT_INPUT or self.input_type == FormInputTypeEnum.RESET_INPUT:
            res += ' \n<button type = "' + self.input_type.value + '" class ="btn ' + self.button_class.value + '" > ' + self.input_label + '</button>'
        elif self.input_type == FormInputTypeEnum.HIDDEN_INPUT:
            res += '\n<div class="form-group">'
            res += '\n<input type="' + self.input_type.value + '" class="form-control" id="' + self.input_name + '" name="' + self.input_name + '" value="' + self.input_value + '">'
            res += '\n</div>'
        elif self.input_type == FormInputTypeEnum.TEXTAREA_INPUT:
            res += '\n<div class="form-group">'
            res += '\n  <label for="' + self.input_name + '"><strong>' + self.input_label + '</strong></label>'
            res += '\n  <textarea class="form-control" id="' + self.input_name + '" name="' + self.input_name + '" placeholder="' + self.placeholder + '" size="' + self.size + '" rows="4"'
            if self.is_disabled:
                res += ' disabled '
            if self.is_readonly:
                res += ' readonly '
            if self.is_required:
                res += ' required '
            res += '>' + self.input_value + '</textarea>'
            res += '\n</div>'
        elif self.input_type == FormInputTypeEnum.SELECT_INPUT:
            res += '\n <div class="form-group">'
            res += '\n <label for="' + self.input_name + '"><strong>' + self.input_label + '</strong></label>'
            res += '\n <select class="form-control" id="' + self.input_name + '" name="' + self.input_name + '" placeholder="' + self.placeholder + '"'
            if self.is_disabled:
                res += ' disabled '
            if self.is_readonly:
                res += ' readonly '
            if self.is_required:
                res += ' required '
            res += '>'
            for key, value in self.list_data.items():
                res += f'<option value="{key}" '
                if key == self.input_value:
                    res += 'selected'
                res += '>'
                res += value + '</option>'
            res += '\n</select>'
            res += '\n</div>'
        else:
            res += 'NOT IMPLEMENTED'

        return res
