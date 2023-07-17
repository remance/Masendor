from pygame import Vector2

from engine.uibattle.uibattle import AimTarget


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

        if self.player_unit:  # command that require player unit
            if choice in self.unit_behaviour_wheel["Group"]:
                if choice == "Group Formation":  # get formation from leader
                    self.unit_behaviour_wheel[choice] = {value: value for value in
                                                         self.player_unit.formation_list}  # TODO change when has icon
                    renew_wheel(self, choice)
            elif choice in self.unit_behaviour_wheel["Army"]:
                if choice == "Army Formation":  # get formation from leader
                    self.unit_behaviour_wheel[choice] = {value: value for value in
                                                         self.player_unit.formation_list}
                    renew_wheel(self, choice)

            elif choice in self.unit_behaviour_wheel["Group Style"]:
                self.player_unit.setup_formation("group", style=choice)
            elif choice in self.unit_behaviour_wheel["Group Phase"]:
                self.player_unit.setup_formation("group", phase=choice)
            elif choice in self.unit_behaviour_wheel["Group Density"]:
                self.player_unit.setup_formation("group", density=choice)
            elif choice in self.unit_behaviour_wheel["Group Position"]:
                self.player_unit.setup_formation("group", position=choice)
            elif choice in self.unit_behaviour_wheel["Group Order"]:
                self.player_unit.change_follow_order(choice, "group")
            elif "Group Formation" in self.unit_behaviour_wheel and choice in self.unit_behaviour_wheel[
                "Group Formation"]:
                self.player_unit.change_formation("group", formation=choice)

            elif choice in self.unit_behaviour_wheel["Army Style"]:
                self.player_unit.setup_formation("army", style=choice[5:])
            elif choice in self.unit_behaviour_wheel["Army Phase"]:
                self.player_unit.setup_formation("army", phase=choice[5:])
            elif choice in self.unit_behaviour_wheel["Army Density"]:
                self.player_unit.setup_formation("army", density=choice[5:])
            elif choice in self.unit_behaviour_wheel["Army Position"]:
                self.player_unit.setup_formation("army", position=choice[5:])
            elif choice in self.unit_behaviour_wheel["Army Order"]:
                self.player_unit.change_follow_order(choice[5:], "army")
            elif "Army Formation" in self.unit_behaviour_wheel and choice in self.unit_behaviour_wheel[
                "Army Formation"]:
                self.player_unit.change_formation("army", formation=choice)

            elif choice in self.unit_behaviour_wheel["Range Attack"]:
                self.realtime_ui_updater.remove(self.wheel_ui)
                self.previous_player_input_state = self.player_input_state
                self.player_input_state = None
                self.camera_mode = "Free"
                self.true_camera_pos = Vector2(self.player_unit.base_pos)
                for shoot_line in self.shoot_lines:
                    shoot_line.delete()  # reset shoot guide lines
                self.player1_battle_cursor.change_image("aim")
                self.text_popup.popup(self.player1_battle_cursor.rect, "")
                self.realtime_ui_updater.add(self.text_popup)
                if choice == "Leader Aim":
                    self.player_input_state = "leader aim"
                    AimTarget(self.player_unit)
                elif choice == "Line Aim":
                    self.player_input_state = "line aim"
                    for this_unit in self.player_unit.alive_troop_follower:
                        AimTarget(this_unit)
                elif choice == "Focus Aim":
                    self.player_input_state = "focus aim"
                    for this_unit in self.player_unit.alive_troop_follower:
                        AimTarget(this_unit)
            elif choice in self.unit_behaviour_wheel["Charge"]:
                self.realtime_ui_updater.remove(self.wheel_ui)
                self.previous_player_input_state = self.player_input_state
                self.player_input_state = None
                self.camera_mode = "Free"
                self.true_camera_pos = Vector2(self.player_unit.base_pos)
                for shoot_line in self.shoot_lines:
                    shoot_line.delete()  # reset shoot guide lines
                # self.player1_battle_cursor.change_image("aim")
                if choice == "Line Charge":
                    self.player_input_state = "line charge"
                elif choice == "Focus Charge":
                    self.player_input_state = "focus charge"
                elif choice == "Cancel Charge":
                    for this_unit in self.player_unit.alive_troop_follower:
                        this_unit.charge_target = None


def renew_wheel(self, choice):
    self.wheel_ui.generate(self.unit_behaviour_wheel[choice])
