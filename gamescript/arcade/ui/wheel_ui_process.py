def wheel_ui_process(self, choice):
    if choice in self.unit_behaviour_wheel:  # click choice that has children choice
        renew_wheel(self, choice)
    elif choice is not None:  # click choice with game effect
        if choice in self.unit_behaviour_wheel["Skill"]:
            if "Troop" in choice:
                self.current_selected.issue_order(None, other_command="Troop Skill " + str(int(choice[-1]) - 1))
            elif "Leader" in choice:
                self.player_char.command_action = ("Leader Skill " + str(int(choice[-1]) - 1),)
            self.battle_ui_updater.remove(self.wheel_ui)
            self.player_input_state = None

        elif choice in self.unit_behaviour_wheel["Setting"]:
            if choice == "Height Map":
                self.map_mode += 1  # change height map mode
                if self.map_mode > 2:
                    self.map_mode = 0
                self.battle_map.change_mode(self.map_mode)
                self.battle_map.change_scale(self.camera_zoom)
            self.battle_ui_updater.remove(self.wheel_ui)
            self.player_input_state = None

        elif choice in self.unit_behaviour_wheel["Shift Line"]:
            self.current_selected.shift_line(choice)

        elif choice in self.unit_behaviour_wheel["Formation"]:
            if choice == "Original":
                self.current_selected.change_formation(formation="true original")
            elif choice == "Formation List":  # get formation from leader
                self.unit_behaviour_wheel[choice] = {value: value for value in self.player_char.leader.formation}  # TODO change when has icon
                renew_wheel(self, choice)

        elif choice in self.unit_behaviour_wheel["Formation Style"]:
            self.current_selected.change_formation(self.current_selected.formation, style=choice)
        elif choice in self.unit_behaviour_wheel["Formation Phase"]:
            self.current_selected.change_formation(self.current_selected.formation, phase=choice)
        elif "Formation List" in self.unit_behaviour_wheel and choice in self.unit_behaviour_wheel["Formation List"]:
            self.current_selected.change_formation(formation=choice)
        elif choice in self.unit_behaviour_wheel["Equipment"]:
            self.current_selected.swap_weapon_command(choice)
            self.battle_ui_updater.remove(self.wheel_ui)
            self.player_input_state = None

        elif choice in self.unit_behaviour_wheel["Range Attack"]:
            if choice == "Fire At Will":
                self.current_selected.fire_at_will = 0
            elif choice == "Volley At Will":
                self.current_selected.fire_at_will = 1
            elif choice == "Manual Only":
                self.current_selected.fire_at_will = 1
            elif "Aim" in choice:
                self.battle_ui_updater.remove(self.wheel_ui)
                self.player_input_state = None
                self.camera_zoom = 4
                self.camera_zoom_change()
                self.cursor.change_image("aim")
                self.single_text_popup.pop(self.cursor.rect.bottomright, "")
                self.battle_ui_updater.add(self.single_text_popup)
                for this_subunit in self.player_char.unit.subunit_list:
                    this_subunit.range_weapon_selection()
                if choice == "Leader Aim":
                    self.player_input_state = "leader aim"
                elif choice == "Volley Aim":
                    self.player_input_state = "volley aim"
                elif choice == "Troop Aim":
                    self.player_input_state = "troop aim"


def renew_wheel(self, choice):
    self.battle_ui_updater.remove(self.wheel_ui)  # remove current wheel first
    self.player_input_state = None
    if len(self.unit_behaviour_wheel[choice]) > 4:
        self.player_input_state = self.eight_wheel_ui
        self.eight_wheel_ui.change_text_icon(self.unit_behaviour_wheel[choice])
        self.battle_ui_updater.add(self.eight_wheel_ui)
    elif len(self.unit_behaviour_wheel[choice]) <= 4:
        self.player_input_state = self.four_wheel_ui
        self.four_wheel_ui.change_text_icon(self.unit_behaviour_wheel[choice])
        self.battle_ui_updater.add(self.four_wheel_ui)