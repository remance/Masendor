from gamescript.common import utility

clean_group_object = utility.clean_group_object


def char_select_menu_process(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.char_back_button.event or esc_press or self.start_button.event:  # go back to team/source selection screen
        self.current_source_row = 0
        self.menu_state = "team_select"
        self.char_back_button.event = False

        self.main_ui_updater.remove(self.char_selector, self.char_selector.scroll,
                                    list(self.char_stat.values()), *self.char_select_button)
        self.menu_button.remove(*self.char_select_button)

        clean_group_object((self.subunit_updater, self.leader_updater, self.preview_char,
                            self.unit_icon, self.troop_number_sprite))

        self.change_to_source_selection_menu()

        self.create_team_coa([self.map_data[self.map_title.name]["Team 1"],
                              self.map_data[self.map_title.name]["Team 2"]], self.main_ui_updater)

        if self.start_button.event:  # start battle button
            self.start_button.event = False
            self.start_battle(self.char_selected)

    elif self.char_selector.scroll.rect.collidepoint(self.mouse_pos):
        if mouse_left_down or mouse_left_up:
            new_row = self.char_selector.scroll.player_input(self.mouse_pos)
            if self.char_selector.current_row != new_row:
                self.char_selector.current_row = new_row
                self.char_selector.setup_unit_icon(self.unit_icon, self.preview_char)

    elif self.char_selector.rect.collidepoint(self.mouse_pos) and mouse_left_up:
        for index, icon in enumerate(self.unit_icon):
            if icon.rect.collidepoint(self.mouse_pos):
                for other_icon in self.unit_icon:
                    if other_icon.selected:  # unselected all others first
                        other_icon.selection()
                        self.main_ui_updater.remove(other_icon.unit.subunit_list)
                icon.selection()
                self.char_stat["char"].add_leader_stat(icon.unit.leader[0])
                self.map_show.change_mode(1, team_pos_list=self.team_pos, selected=icon.unit.base_pos)

                self.main_ui_updater.add(icon.unit.subunit_list)

                self.char_selected = icon.unit.game_id
                break

    elif self.char_stat["troop"].rect.collidepoint(self.mouse_pos):
        for icon in self.unit_icon:
            if icon.selected:
                for subunit in icon.unit.subunit_list:
                    if subunit.rect.collidepoint(self.mouse_pos):
                        self.main_ui_updater.add(self.char_popup)
                        self.char_popup.pop(self.mouse_pos, subunit.name)

    else:
        self.main_ui_updater.remove(self.char_popup)
