def read_selected_map_lore(self):
    if self.menu_state == "preset_map" or self.last_select == "preset_map":
        data = self.localisation.grab_text(key=("preset_map",
                                                self.battle_campaign[self.battle_map_folder[self.current_map_select]],
                                                self.battle_map_folder[self.current_map_select]))
    else:
        if self.battle_map_folder[self.current_map_select] != "Random":
            data = self.localisation.grab_text(key=("custom_map", self.battle_map_folder[self.current_map_select]))
            if type(data) is str:  # try from preset list
                data = self.localisation.grab_text(key=("preset_map",
                                                        self.battle_campaign[
                                                            self.battle_map_folder[self.current_map_select]],
                                                        "info", self.battle_map_folder[self.current_map_select]))
        else:
            data = {"Random": ["", ""]}

    return data
