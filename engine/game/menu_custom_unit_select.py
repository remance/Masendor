from engine import utility

from engine.game import menu_custom_unit_setup

leader_change_team_unit = menu_custom_unit_setup.leader_change_team_unit
clean_group_object = utility.clean_group_object


def menu_custom_unit_select(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    self.main_ui_updater.remove(self.single_text_popup)
    if self.map_back_button.event or esc_press or self.start_button.event:  # go back to team/source selection screen
        self.map_back_button.event = False
        clean_group_object((self.unit_updater, self.all_units, self.preview_unit, self.unit_icon))

        self.main_ui_updater.remove(tuple(self.unit_stat.values()), self.start_button)
        self.menu_button.remove(self.start_button)
        self.menu_state = "custom_leader_setup"
        self.unit_select_row = 0
        self.current_map_row = 0

        self.menu_button.add(*self.team_select_button)

        self.main_ui_updater.add(*self.team_select_button, self.team_coa)

        self.main_ui_updater.add(self.org_chart)

        for icon in self.preview_unit:
            icon.kill()
        self.preview_unit.empty()

        leader_change_team_unit(self)

        if self.start_button.event:  # start battle button
            self.start_button.event = False
            self.start_battle(self.unit_selected)

    elif self.unit_selector.rect.collidepoint(self.mouse_pos):
        if mouse_scroll_up:
            if self.unit_selector.current_row > 0:
                self.unit_selector.current_row -= 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        elif mouse_scroll_down:
            if self.unit_selector.current_row < self.unit_selector.row_size:
                self.unit_selector.current_row += 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        elif self.unit_selector.scroll.rect.collidepoint(self.mouse_pos):
            if mouse_left_down or mouse_left_up:
                new_row = self.unit_selector.scroll.player_input(self.mouse_pos)
                if self.unit_selector.current_row != new_row:
                    self.unit_selector.current_row = new_row
                    self.unit_selector.scroll.change_image(new_row=new_row, row_size=self.unit_selector.row_size)
                    self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        else:
            for index, icon in enumerate(self.unit_icon):
                if icon.rect.collidepoint(self.mouse_pos):
                    popup_text = [icon.who.name]
                    for item in self.play_map_data["unit"]:
                        if item["ID"] == icon.who.map_id:
                            for troop, value in item["Troop"].items():
                                popup_text += [self.troop_data.troop_list[int(troop)]["Name"] + ": " +
                                               value]
                            break
                    self.single_text_popup.pop(self.mouse_pos, popup_text)
                    self.main_ui_updater.add(self.single_text_popup)
                    if mouse_left_up:
                        for other_icon in self.unit_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                        who_todo = {key: value for key, value in self.leader_data.leader_list.items() if
                                    key == icon.who.troop_id}
                        preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True)
                        self.unit_stat["model"].add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"],
                                                                  icon.who.coa)
                        self.map_preview.change_mode(1, team_pos_list=self.team_pos,
                                                     camp_pos_list=self.camp_pos,
                                                     selected=icon.who.base_pos)

                        self.unit_selected = icon.who.map_id
                    break
