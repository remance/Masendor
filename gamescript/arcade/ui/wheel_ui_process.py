from gamescript import battleui

leader_skill_command_action = ({"name": "Leader Skill 0"}, {"name": "Leader Skill 1"})


def wheel_ui_process(self, choice):
    if choice in self.unit_behaviour_wheel:  # click choice that has children choice
        renew_wheel(self, choice)
    elif choice is not None:  # click choice with game effect
        if choice in self.unit_behaviour_wheel["Skill"]:
            if "Troop" in choice:
                self.current_selected.issue_order(None, other_command="Troop Skill " + str(int(choice[-1]) - 1))
            elif "Leader" in choice:
                self.player_char.command_action = leader_skill_command_action[int(choice[-1]) - 1]

        elif choice in self.unit_behaviour_wheel["Setting"]:
            if choice == "Height Map":
                self.map_mode += 1  # change height map mode
                if self.map_mode > 2:
                    self.map_mode = 0
                self.battle_map.change_mode(self.battle_map_height, self.map_mode)

        elif choice in self.unit_behaviour_wheel["Shift Line"]:
            self.current_selected.shift_line(choice)

        elif choice in self.unit_behaviour_wheel["Formation"]:
            if choice == "Original":
                self.current_selected.change_formation(formation="true original")
            elif choice == "Formation List":  # get formation from leader
                self.unit_behaviour_wheel[choice] = {value: value for value in
                                                     self.player_char.leader.formation}  # TODO change when has icon
                renew_wheel(self, choice)

        elif choice in self.unit_behaviour_wheel["Formation Style"]:
            self.current_selected.change_formation(self.current_selected.formation, style=choice)
        elif choice in self.unit_behaviour_wheel["Formation Phase"]:
            self.current_selected.change_formation(self.current_selected.formation, phase=choice)
        elif "Formation List" in self.unit_behaviour_wheel and choice in self.unit_behaviour_wheel["Formation List"]:
            self.current_selected.change_formation(formation=choice)
        elif choice in self.unit_behaviour_wheel["Equipment"]:
            self.current_selected.swap_weapon_command(choice)

        elif choice in self.unit_behaviour_wheel["Range Attack"]:
            if choice == "Fire At Will":
                self.current_selected.fire_at_will = 0
            elif choice == "Volley At Will":
                self.current_selected.fire_at_will = 1
            elif choice == "Manual Only":
                self.current_selected.fire_at_will = 1
            elif choice == "Allow Arc Shot":
                self.current_selected.shoot_mode = 0
            elif choice == "No Arc Shot":
                self.current_selected.shoot_mode = 1
            elif "Aim" in choice:
                self.battle_ui_updater.remove(self.wheel_ui)
                self.previous_player_input_state = self.player_input_state
                self.player_input_state = None
                self.camera_zoom = self.camera_zoom_level[3]
                self.camera_zoom_change()
                for shoot_line in self.shoot_lines:
                    shoot_line.delete()  # reset shoot guide lines
                self.cursor.change_image("aim")
                self.single_text_popup.pop(self.cursor.rect.bottomright, "")
                self.battle_ui_updater.add(self.single_text_popup)
                if choice == "Leader Aim":
                    self.player_input_state = "leader aim"
                    self.player_char.range_weapon_selection()
                    battleui.ShootLine(self.screen_scale, self.player_char)
                elif choice == "Line Aim":
                    self.player_input_state = "line aim"
                    for this_subunit in self.player_char.unit.alive_subunit_list:
                        this_subunit.range_weapon_selection()
                        battleui.ShootLine(self.screen_scale, this_subunit)
                elif choice == "Focus Aim":
                    self.player_input_state = "focus aim"
                    for this_subunit in self.player_char.unit.alive_subunit_list:
                        this_subunit.range_weapon_selection()
                        battleui.ShootLine(self.screen_scale, this_subunit)


def renew_wheel(self, choice):
    self.wheel_ui.generate(self.unit_behaviour_wheel[choice])
