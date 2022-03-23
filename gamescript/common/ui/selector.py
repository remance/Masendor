def setup_unit_icon(selector, unit_group, unit_list, select_scroll, icon_scale=0.55):
    """Setup unit selection list in unit selector ui top left of screen"""
    from gamescript import battleui
    current_index = int(selector.current_row * selector.max_column_show)  # the first index of current row
    selector.log_size = len(unit_list) / selector.max_column_show

    if selector.log_size.is_integer() is False:
        selector.log_size = int(selector.log_size) + 1

    if selector.current_row > selector.log_size - 1:
        selector.current_row = selector.log_size - 1
        current_index = int(selector.current_row * selector.max_column_show)
        select_scroll.change_image(new_row=selector.current_row)

    if len(unit_group) > 0:  # Remove all old icon first before making new list
        for icon in unit_group:
            icon.kill()
            del icon

    if len(unit_list) > 0:
        for index, unit in enumerate(unit_list):  # add unit icon for drawing according to appropriated current row
            if index == 0:
                start_column = selector.rect.topleft[0] + (unit.leader[0].image.get_width() / 1.5)
                column = start_column
                row = selector.rect.topleft[1] + (unit.leader[0].image.get_height() / 1.5)
            if index >= current_index:
                new_icon = battleui.UnitIcon((column, row), unit, (int(unit.leader[0].image.get_width() * icon_scale),
                                                                   int(unit.leader[0].image.get_height() * icon_scale)))
                unit_group.add(new_icon)
                column += new_icon.image.get_width() * 1.2
                if column > selector.rect.topright[0] - (new_icon.image.get_width() / 2):
                    row += new_icon.image.get_height() * 1.5
                    column = start_column
                if row > selector.rect.bottomright[1] - (new_icon.image.get_height() / 2):
                    break  # do not draw for row that exceed the box
    select_scroll.change_image(log_size=selector.log_size)
