def player_skill_perform(self):
    skill_range = self.player_unit.skill[self.player_unit.current_action["skill"]]["Range"]
    if self.player_unit.base_pos.distance_to(self.command_cursor_pos) <= skill_range:
        can_shoot = True
        if self.player_unit.shoot_line not in self.battle_camera:
            self.battle_camera.add(self.player_unit.shoot_line)
        self.player_unit.shoot_line.update(self.command_cursor_pos, self.base_cursor_pos, can_shoot)
    else:
        can_shoot = False
        if self.player_unit.shoot_line in self.battle_camera:  # remove shoot line
            self.battle_camera.remove(self.player_unit.shoot_line)

    if self.player_key_press["Main Weapon Attack"] and can_shoot:
        self.player_unit.current_action["pos"] = self.player_unit.shoot_line.base_target_pos
        self.player_unit.current_action.pop("require input")
        self.player_cancel_input()
    elif self.player_key_press["Sub Weapon Attack"]:
        self.player_unit.current_action = {}
        self.player_cancel_input()
    else:
        self.camera_process()
