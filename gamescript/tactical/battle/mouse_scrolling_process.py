from gamescript.common import utility

list_scroll = utility.list_scroll


def mouse_scrolling_process(self, mouse_scroll_up, mouse_scroll_down):
    if self.event_log.rect.collidepoint(self.mouse_pos):  # Scrolling when mouse at event log
        if mouse_scroll_up:
            self.event_log.current_start_row -= 1
            if self.event_log.current_start_row < 0:  # can go no further than the first log
                self.event_log.current_start_row = 0
            else:
                self.event_log.recreate_image()  # recreate event_log image
                self.event_log.scroll.change_image(new_row=self.event_log.current_start_row)
        elif mouse_scroll_down:
            self.event_log.current_start_row += 1
            if self.event_log.current_start_row + self.event_log.max_row_show - 1 < self.event_log.len_check and \
                    self.event_log.len_check > 9:
                self.event_log.recreate_image()
                self.event_log.scroll.change_image(new_row=self.event_log.current_start_row)
            else:
                self.event_log.current_start_row -= 1

    elif self.unit_selector.rect.collidepoint(self.mouse_pos):  # Scrolling when mouse at unit selector ui
        if mouse_scroll_up:
            self.unit_selector.current_row -= 1
            if self.unit_selector.current_row < 0:
                self.unit_selector.current_row = 0
            else:
                self.unit_selector.setup_unit_icon(self.unit_icon, self.all_team_unit[self.team_selected])
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row)
        elif mouse_scroll_down:
            self.unit_selector.current_row += 1
            if self.unit_selector.current_row < self.unit_selector.row_size:
                self.unit_selector.setup_unit_icon(self.unit_icon, self.all_team_unit[self.team_selected])
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row)
            else:
                self.unit_selector.current_row -= 1
                if self.unit_selector.current_row < 0:
                    self.unit_selector.current_row = 0

    elif self.popup_list_box in self.battle_ui_updater:  # mouse scroll on popup list
        if self.popup_list_box.type == "terrain":
            self.current_pop_up_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                                  self.popup_list_box.scroll,
                                                  self.popup_list_box,
                                                  self.current_pop_up_row, self.battle_map_base.terrain_list,
                                                  self.popup_namegroup, self.battle_ui_updater)
        elif self.popup_list_box.type == "feature":
            self.current_pop_up_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                                  self.popup_list_box.scroll,
                                                  self.popup_list_box,
                                                  self.current_pop_up_row, self.battle_map_feature.feature_list,
                                                  self.popup_namegroup, self.battle_ui_updater)
        elif self.popup_list_box.type == "weather":
            self.current_pop_up_row = (mouse_scroll_up, mouse_scroll_down, self.popup_list_box.scroll,
                                       self.popup_list_box, self.current_pop_up_row, self.weather_list,
                                       self.popup_namegroup, self.battle_ui_updater)
        elif self.popup_list_box.type == "leader":
            self.current_pop_up_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                                  self.popup_list_box.scroll,
                                                  self.popup_list_box, self.current_pop_up_row, self.leader_list,
                                                  self.popup_namegroup, self.battle_ui_updater, layer=19)

    elif self.unit_preset_list_box in self.battle_ui_updater and self.unit_preset_list_box.rect.collidepoint(
            self.mouse_pos):  # mouse scroll on unit preset list
        self.current_unit_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                            self.unit_preset_list_box.scroll,
                                            self.unit_preset_list_box,
                                            self.current_unit_row, list(self.custom_unit_preset_list.keys()),
                                            self.unitpreset_namegroup, self.battle_ui_updater)
    elif self.editor_troop_list_box in self.battle_ui_updater and self.editor_troop_list_box.rect.collidepoint(
            self.mouse_pos):
        if self.current_list_show == "troop":  # mouse scroll on troop list
            self.current_troop_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                                 self.editor_troop_list_box.scroll,
                                                 self.editor_troop_list_box, self.current_troop_row, self.troop_list,
                                                 self.troop_namegroup, self.battle_ui_updater)
        elif self.current_list_show == "faction":  # mouse scroll on faction list
            self.current_troop_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                                 self.editor_troop_list_box.scroll,
                                                 self.editor_troop_list_box, self.current_troop_row,
                                                 self.faction_data.faction_name_list,
                                                 self.troop_namegroup, self.battle_ui_updater)

    elif self.map_scale_delay == 0:  # Scrolling in self map to zoom
        if mouse_scroll_up:
            try:
                self.camera_zoom = self.camera_zoom_level[self.camera_zoom_level.index(self.camera_zoom) + 1]
                self.camera_zoom_change()
            except IndexError:
                pass

        elif mouse_scroll_down:
            if self.camera_zoom_level.index(self.camera_zoom) > 1:
                self.camera_zoom = self.camera_zoom_level[self.camera_zoom_level.index(self.camera_zoom) - 1]
                self.camera_zoom_change()
