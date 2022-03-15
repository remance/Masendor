def setup_unit_icon(unit_selector, unit_icon, unit_list, select_scroll):
    """Setup unit selection list in unit selector ui top left of screen"""
    from gamescript import battleui
    current_index = int(unit_selector.current_row * unit_selector.max_column_show)  # the first index of current row
    unit_selector.log_size = len(unit_list) / unit_selector.max_column_show

    if unit_selector.log_size.is_integer() is False:
        unit_selector.log_size = int(unit_selector.log_size) + 1

    if unit_selector.current_row > unit_selector.log_size - 1:
        unit_selector.current_row = unit_selector.log_size - 1
        current_index = int(unit_selector.current_row * unit_selector.max_column_show)
        select_scroll.change_image(new_row=unit_selector.current_row)

    if len(unit_icon) > 0:  # Remove all old icon first before making new list
        for icon in unit_icon:
            icon.kill()
            del icon

    if len(unit_list) > 0:
        row = unit_list[0].leader[0].image.get_width() / 2
        start_column = unit_list[0].leader[0].image.get_height() / 2
        column = start_column

        for index, unit in enumerate(unit_list):  # add unit icon for drawing according to appropriated current row
            if index >= current_index:
                new_icon = battleui.UnitIcon((column, row), unit, (int(unit.leader[0].image.get_width() / 1.5),
                                                                   int(unit.leader[0].image.get_height() / 1.5)))
                unit_icon.add(new_icon)
                column += new_icon.image.get_width() * 1.2
                if column > unit_selector.rect.topright[0] - (new_icon.image.get_width() / 2):
                    row += new_icon.image.get_height() * 1.5
                    column = start_column
                if row > unit_selector.image.get_height() - (new_icon.image.get_height() / 2):
                    break  # do not draw for row that exceed the box
    select_scroll.change_image(log_size=unit_selector.log_size)
