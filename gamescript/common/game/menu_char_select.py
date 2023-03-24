from gamescript.common import utility

clean_group_object = utility.clean_group_object


def menu_char_select(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.char_back_button.event or esc_press or self.start_button.event:  # go back to team/source selection screen
        self.current_source_row = 0
        self.menu_state = "preset_team_select"
        self.char_back_button.event = False

        self.main_ui_updater.remove(self.char_selector, self.char_selector.scroll,
                                    tuple(self.char_stat.values()), *self.char_select_button)
        self.menu_button.remove(*self.char_select_button)

        clean_group_object((self.subunit_updater, self.all_subunits, self.preview_char, self.char_icon))

        self.change_to_source_selection_menu()

        self.create_team_coa([self.map_data[self.map_title.name][data] for data in self.map_data[self.map_title.name] if
                              "Team " in data], self.main_ui_updater)

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
            if mouse_left_up:
                for index, icon in enumerate(self.char_icon):
                    if icon.rect.collidepoint(self.mouse_pos):
                        for other_icon in self.char_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                        self.char_stat["char"].add_leader_stat(icon.who, self.leader_data, self.troop_data)
                        who_todo = {key: value for key, value in self.leader_data.leader_list.items() if key == icon.who.troop_id}
                        preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True, max_preview_size=400)
                        self.char_stat["model"].add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"],
                                                                  icon.who.coa)
                        self.map_preview.change_mode(1, team_pos_list=self.team_pos,
                                                     camp_pos_list=self.camp_pos[self.map_source],
                                                     selected=icon.who.base_pos)

                        self.char_selected = icon.who.map_id
                        break
