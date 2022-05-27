################################## text
_text1 = text_element(title='Title2', text='Hello')
_text2 = text_element(title='Title3', text='Hello')

################################## INFOTable
_infotable = infotable_element(title='INFO TABLE', is_table_striped=True, is_table_hover=True,
                               is_table_bordered=True)
for i in range(0, 10):
    ___row = table_row(row_class=RowClassEnum.NORMAL)
    cell1 = table_cell(cell_class=RowClassEnum.NORMAL, cell_type=CellTypeEnum.TEXT_CELL, text=str(i),
                       link='dashboard',
                       link_parameters={}, tag_type=BadgeClassEnum.BADGE_PRIMARY)
    cell2 = table_cell(cell_class=RowClassEnum.NORMAL, cell_type=CellTypeEnum.TEXT_CELL, text='test',
                       link='dashboard',
                       link_parameters={}, tag_type=BadgeClassEnum.BADGE_PRIMARY)
    ___row.add_cell_to_row(cell1)
    ___row.add_cell_to_row(cell2)
    _infotable.addDataRow(___row)

################################## DATATable
_table1 = datatable_element(title='Title4', footer=True)
___header = table_row(row_class=RowClassEnum.NORMAL)
for j in range(0, 6):
    acell = table_cell(cell_class=RowClassEnum.NORMAL, cell_type=CellTypeEnum.TEXT_CELL, text=str(j),
                       link='dashboard',
                       link_parameters={}, tag_type=BadgeClassEnum.BADGE_PRIMARY)
    ___header.add_cell_to_row(acell)
_table1.setHeader(___header)

_dict = {}
_dict['name'] = 'ali'
_dict['code'] = 5

for i in range(0, 10):
    ___row = table_row(row_class=RowClassEnum.NORMAL)
    for j in range(0, 6):
        acell = table_cell(cell_class=RowClassEnum.NORMAL, cell_type=CellTypeEnum.LINK_CELL,
                           text=str(j),
                           link='dashboard',
                           link_parameters=_dict, tag_type=BadgeClassEnum.BADGE_LIGHT)
        ___row.add_cell_to_row(acell)
    _table1.addBodyRow(___row)
################################## CALENDAR
_calendar = calendar_element(title='Calendar (TERM II)', calendar_view_type=CalendarViewTypeEnum.THREE_WEEKs)

for i in range(1, 23):
    _week = week(i)
    for j in range(1, 8):
        _day = day(day_date_text1='day' + str(j), day_date_text2='day' + str(j), day_number=j)

        _event1 = event(text='event1', link='dashboard', link_parameters={'code': '1'},
                        badge_type=BadgeClassEnum.BADGE_PRIMARY)
        _event2 = event(text='event2', link='dashboard', link_parameters={'code': '2'},
                        badge_type=BadgeClassEnum.BADGE_SUCCESS)
        _day.addEvent(_event1)
        _day.addEvent(_event2)
        _week.addDay(_day)
    _calendar.addWeek(_week)

################################## CARDS
_cards_row = cards_row()
_card1 = card('primary', 'Earnings1', '$41,000', progress_value=10, progress_min=0, progress_max=100,
              icon_type='fa-calendar')
_card2 = card('success', 'Earnings2', '$42,000', progress_value=25, progress_min=0, progress_max=100,
              icon_type='fa-dollar-sign')
_card3 = card('info', 'Earnings3', '$43,000', progress_value=50, progress_min=0, progress_max=100,
              icon_type='fa-clipboard-list')
_card4 = card('warning', 'Earnings4', '$44,000', progress_value=70, progress_min=0, progress_max=100,
              icon_type='fa-comments')
_cards_row.addCard(_card1)
_cards_row.addCard(_card2)
_cards_row.addCard(_card3)
_cards_row.addCard(_card4)

################################## FORMS
_form = form_element('Form Test', 'form1', 'dashboard', 'POST')
_text1 = field('Text1', 't1', FormInputTypeEnum.TEXT_INPUT, value='', placeholder='type text here', maxlength=20,
               size=20)
_text2 = field('Text2', 't2', FormInputTypeEnum.TEXT_INPUT, value='', placeholder='type text here')
_submit = field('Save', 's', FormInputTypeEnum.SUBMIT_INPUT, button_class=ButtonClassEnum.BTN_SUCCESS)
_reset = field('REset', 'reset', FormInputTypeEnum.RESET_INPUT, button_class=ButtonClassEnum.BTN_WARNING)
_hidden = field('Hidden', 'h1', FormInputTypeEnum.HIDDEN_INPUT, value='hello')
_email = field('email', 'email', FormInputTypeEnum.EMAIL_INPUT, value='', placeholder='type email here')
_textarea = field('Text Area', 'textarea', FormInputTypeEnum.TEXTAREA_INPUT, value='',
                  placeholder='type your paragraph here')
_password = field('Password', 'pass', FormInputTypeEnum.PASSWORD_INPUT, value='',
                  placeholder='type your password here')

_date = field('date', 'date', FormInputTypeEnum.DATE_INPUT, value='',
              placeholder='choose your date here')
_time = field('time', 'time', FormInputTypeEnum.TIME_INPUT, value='',
              placeholder='choose your time here')
_week = field('week', 'week', FormInputTypeEnum.WEEK_INPUT, value='',
              placeholder='choose your week here')
_localtime = field('localtime', 'localtime', FormInputTypeEnum.DATETIMELOCAL_INPUT, value='',
                   placeholder='choose your date here')
_month = field('month', 'month', FormInputTypeEnum.MONTH_INPUT, value='',
               placeholder='choose your month here')

_color = field('color', 'color', FormInputTypeEnum.COLOR_INPUT, value='',
               placeholder='choose your color here')
_file = field('file', 'file', FormInputTypeEnum.FILE_INPUT, value='',
              placeholder='choose your file here')

_form.addField(_text1)
_form.addField(_text2)
_form.addField(_textarea)
_form.addField(_hidden)
_form.addField(_email)
_form.addField(_password)
_form.addField(_color)
_form.addField(_file)

_form.addField(_date)
_form.addField(_time)
_form.addField(_week)
_form.addField(_localtime)
_form.addField(_month)

_form.addField(_submit)
_form.addField(_reset)

# --- SELECT
_data = {}
_data[1] = 'Hello1'
_data[2] = 'Hello2'
_data[3] = 'Hello3'
_data[4] = 'Hello4'

_select = field('select', 'select', FormInputTypeEnum.SELECT_INPUT, value=2, data=_data)
_form.addField(_select)

################################## MIX TOGETHER

_block.addElement(1, _text1)
_block.addElement(2, _text2)
_block.addElement(3, _table1)
_block.addElement(4, _calendar)
_block.addElement(5, _infotable)
_block.addElement(6, _form)

context['ui_elements'] = _block.getElements()
context['block_title'] = _block.getTitle()
context['cards_row'] = _cards_row