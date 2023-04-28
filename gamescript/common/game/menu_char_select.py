from gamescript.common import utility

from gamescript.common.game import menu_unit_setup

leader_change_team_unit = menu_unit_setup.leader_change_team_unit
clean_group_object = utility.clean_group_object


def menu_char_select(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    self.main_ui_updater.remove(self.single_text_popup)

    if self.map_back_button.event or esc_press or self.start_button.event:  # go back to team/source selection screen
        self.map_back_button.event = False
        clean_group_object((self.subunit_updater, self.all_subunits, self.preview_char, self.char_icon))

        self.main_ui_updater.remove(tuple(self.char_stat.values()), self.start_button)
        self.menu_button.remove(self.start_button)
        self.menu_state = "unit_leader_setup"
        self.char_select_row = 0
        self.current_map_row = 0

        self.menu_button.add(*self.team_select_button)

        self.main_ui_updater.add(*self.team_select_button, self.team_coa)

        self.main_ui_updater.add(self.org_chart)

        for icon in self.preview_char:
            icon.kill()
        self.preview_char.empty()

        leader_change_team_unit(self)

        if self.start_button.event:  # start battle button
            self.start_button.event = False
            self.start_battle(self.char_selected)

    elif self.char_selector.rect.collidepoint(self.mouse_pos):
        if mouse_scroll_up:
            if self.char_selector.current_row > 0:
                self.char_selector.current_row -= 1
                self.char_selector.scroll.change_image(new_row=self.char_selector.current_row,
                                                       row_size=self.char_selector.row_size)
                self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

        elif mouse_scroll_down:
            if self.char_selector.current_row < self.char_selector.row_size:
                self.char_selector.current_row += 1
                self.char_selector.scroll.change_image(new_row=self.char_selector.current_row,
                                                       row_size=self.char_selector.row_size)
                self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

        elif self.char_selector.scroll.rect.collidepoint(self.mouse_pos):
            if mouse_left_down or mouse_left_up:
                new_row = self.char_selector.scroll.player_input(self.mouse_pos)
                if self.char_selector.current_row != new_row:
                    self.char_selector.current_row = new_row
                    self.char_selector.scroll.change_image(new_row=new_row, row_size=self.char_selector.row_size)
                    self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

        else:
            for index, icon in enumerate(self.char_icon):
                if icon.rect.collidepoint(self.mouse_pos):
                    popup_text = [icon.who.name]
                    for troop in icon.who.troop_reserve_list:
                        popup_text += [self.troop_data.troop_list[troop]["Name"] + ": " +
                                       str(len([subunit for subunit in icon.who.alive_troop_follower if
                                                subunit.troop_id == troop])) + " + " +
                                       str(icon.who.troop_reserve_list[troop])]
                    self.single_text_popup.pop(self.mouse_pos, popup_text)
                    self.main_ui_updater.add(self.single_text_popup)
                    if mouse_left_up:
                        for other_icon in self.char_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                        self.char_stat["char"].add_leader_stat(icon.who, self.leader_data, self.troop_data)
                        who_todo = {key: value for key, value in self.leader_data.leader_list.items() if
                                    key == icon.who.troop_id}
                        preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True)
                        self.char_stat["model"].add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"],
                                                                  icon.who.coa)
                        self.map_preview.change_mode(1, team_pos_list=self.team_pos,
                                                     camp_pos_list=self.camp_pos[self.map_source],
                                                     selected=icon.who.base_pos)

                        self.char_selected = icon.who.map_id
                    break
