def setup_unit_icon(self):
    """Setup unit selection list in unit selector ui top left of screen"""
    from gamescript import battleui
    row = 30
    start_column = 25
    column = start_column
    unit_list = self.team1_unit
    if self.player_team == 2:
        unit_list = self.team2_unit
    if self.enactment:  # include another team unit icon as well in enactment mode
        unit_list = self.all_unit_list
    current_index = int(self.unit_selector.current_row * self.unit_selector.max_column_show)  # the first index of current row
    self.unit_selector.log_size = len(unit_list) / self.unit_selector.max_column_show

    if self.unit_selector.log_size.is_integer() is False:
        self.unit_selector.log_size = int(self.unit_selector.log_size) + 1

    if self.unit_selector.current_row > self.unit_selector.log_size - 1:
        self.unit_selector.current_row = self.unit_selector.log_size - 1
        current_index = int(self.unit_selector.current_row * self.unit_selector.max_column_show)
        self.unit_selector_scroll.change_image(new_row=self.unit_selector.current_row)

    if len(self.unit_icon) > 0:  # Remove all old icon first before making new list
        for icon in self.unit_icon:
            icon.kill()
            del icon

    for index, unit in enumerate(unit_list):  # add unit icon for drawing according to appropriated current row
        if index >= current_index:
            self.unit_icon.add(battleui.UnitIcon((column, row), unit))
            column += 40
            if column > 250:
                row += 50
                column = start_column
            if row > 100:
                break  # do not draw for the third row
    self.unit_selector_scroll.change_image(log_size=self.unit_selector.log_size)