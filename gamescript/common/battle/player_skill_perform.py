def player_skill_perform(self, mouse_left_up, mouse_right_up, key_state):
    base_target_pos = self.command_mouse_pos
    target_pos = self.base_mouse_pos

    if mouse_left_up:
        self.player_char.command_action

        self.player_cancel_input()
    elif mouse_right_up:
        self.player_cancel_input()
    else:
        self.camera_process(key_state)