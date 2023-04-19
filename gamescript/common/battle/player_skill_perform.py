def player_skill_perform(self):
    skill_range = self.player_char.skill[self.player_char.current_action["skill"]]["Range"]
    if self.player_char.base_pos.distance_to(self.command_mouse_pos) <= skill_range:
        can_shoot = True
        if self.player_char.shoot_line not in self.battle_camera:
            self.battle_camera.add(self.player_char.shoot_line)
        self.player_char.shoot_line.update(self.command_mouse_pos, self.base_mouse_pos, can_shoot)
    else:
        can_shoot = False
        if self.player_char.shoot_line in self.battle_camera:  # remove shoot line
            self.battle_camera.remove(self.player_char.shoot_line)

    if self.battle.player_keyboard_press["Main Weapon Attack"] and can_shoot:
        self.player_char.current_action["pos"] = self.player_char.shoot_line.base_target_pos
        self.player_char.current_action.pop("require input")
        self.player_cancel_input()
    elif self.battle.player_keyboard_press["Sub Weapon Attack"]:
        self.player_char.current_action = {}
        self.player_cancel_input()
    else:
        self.camera_process()
