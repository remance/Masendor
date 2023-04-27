from pygame import Vector2

from gamescript import battleui


def wheel_ui_process(self, choice):
    if choice in self.unit_behaviour_wheel:  # click choice that has children choice
        renew_wheel(self, choice)
    elif choice:  # click choice with game effect
        if choice in self.unit_behaviour_wheel["Setting"]:
            if choice == "Height Map":
                self.battle_map.mode += 1  # change height map mode
                if self.battle_map.mode > 1:
                    self.battle_map.mode = 0
                self.battle_map.change_map_stuff("mode")

        if self.player_char:  # command that require player char
            if choice in self.unit_behaviour_wheel["Formation"]:
                if choice == "Formation List":  # get formation from leader
                    self.unit_behaviour_wheel[choice] = {value: value for value in
                                                         self.player_char.formation_list}  # TODO change when has icon
                    renew_wheel(self, choice)
            elif choice in self.unit_behaviour_wheel["Unit"]:
                if choice == "Unit Formation List":  # get formation from leader
                    self.unit_behaviour_wheel[choice] = {value: value for value in
                                                         self.player_char.formation_list}
                    renew_wheel(self, choice)

            elif choice in self.unit_behaviour_wheel["Formation Style"]:
                self.player_char.setup_formation("troop", style=choice)
            elif choice in self.unit_behaviour_wheel["Formation Phase"]:
                self.player_char.setup_formation("troop", phase=choice)
            elif choice in self.unit_behaviour_wheel["Formation Density"]:
                self.player_char.setup_formation("troop", density=choice)
            elif choice in self.unit_behaviour_wheel["Formation Position"]:
                self.player_char.setup_formation("troop", position=choice)
            elif choice in self.unit_behaviour_wheel["Formation Order"]:
                self.player_char.change_follow_order(choice, "troop")
            elif "Formation List" in self.unit_behaviour_wheel and choice in self.unit_behaviour_wheel[
                "Formation List"]:
                self.player_char.change_formation("troop", formation=choice)

            elif choice in self.unit_behaviour_wheel["Unit Style"]:
                self.player_char.setup_formation("unit", style=choice[5:])
            elif choice in self.unit_behaviour_wheel["Unit Phase"]:
                self.player_char.setup_formation("unit", phase=choice[5:])
            elif choice in self.unit_behaviour_wheel["Unit Density"]:
                self.player_char.setup_formation("unit", density=choice[5:])
            elif choice in self.unit_behaviour_wheel["Unit Position"]:
                self.player_char.setup_formation("unit", position=choice[5:])
            elif choice in self.unit_behaviour_wheel["Unit Order"]:
                self.player_char.change_follow_order(choice[5:], "unit")
            elif "Unit Formation List" in self.unit_behaviour_wheel and choice in self.unit_behaviour_wheel[
                "Unit Formation List"]:
                self.player_char.change_formation("unit", formation=choice)

            elif choice in self.unit_behaviour_wheel["Range Attack"]:
                self.battle_ui_updater.remove(self.wheel_ui)
                self.previous_player_input_state = self.player_input_state
                self.player_input_state = None
                self.camera_mode = "Free"
                self.true_camera_pos = Vector2(self.player_char.base_pos)
                for shoot_line in self.shoot_lines:
                    shoot_line.delete()  # reset shoot guide lines
                self.cursor.change_image("aim")
                self.single_text_popup.pop(self.cursor.rect.bottomright, "")
                self.battle_ui_updater.add(self.single_text_popup)
                if choice == "Leader Aim":
                    self.player_input_state = "leader aim"
                    battleui.AimTarget(self.screen_scale, self.player_char)
                elif choice == "Line Aim":
                    self.player_input_state = "line aim"
                    for this_subunit in self.player_char.alive_troop_follower:
                        battleui.AimTarget(self.screen_scale, this_subunit)
                elif choice == "Focus Aim":
                    self.player_input_state = "focus aim"
                    for this_subunit in self.player_char.alive_troop_follower:
                        battleui.AimTarget(self.screen_scale, this_subunit)


def renew_wheel(self, choice):
    self.wheel_ui.generate(self.unit_behaviour_wheel[choice])
