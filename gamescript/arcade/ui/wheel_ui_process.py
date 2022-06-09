def wheel_ui_process(self, choice):
    if choice in self.unit_behaviour_wheel:  # click choice that has children choice
        self.battle_ui_updater.remove(self.wheel_ui)  # remove current wheel first
        self.player_input_ui = None
        if len(self.unit_behaviour_wheel[choice]) > 4:
            self.player_input_ui = self.eight_wheel_ui
            self.eight_wheel_ui.change_text_icon(self.unit_behaviour_wheel[choice])
            self.battle_ui_updater.add(self.eight_wheel_ui)
        elif len(self.unit_behaviour_wheel[choice]) <= 4:
            self.player_input_ui = self.four_wheel_ui
            self.four_wheel_ui.change_text_icon(self.unit_behaviour_wheel[choice])
            self.battle_ui_updater.add(self.four_wheel_ui)
    elif choice is not None:  # click choice with game effect
        if "Skill" in choice:
            if "Troop" in choice:
                self.player_char.unit.process_command(None, other_command="Troop Skill " + str(int(choice[-1]) - 1))
            elif "Leader" in choice:
                self.player_char.command_action = ("Leader Skill " + str(int(choice[-1]) - 1),)
        elif "Height Map" in choice:
            self.map_mode += 1  # change height map mode
            if self.map_mode > 2:
                self.map_mode = 0
            self.show_map.change_mode(self.map_mode)
            self.show_map.change_scale(self.camera_zoom)
        elif " To " in choice:  # shift line
            self.player_char.unit.shift_line(choice)


