def battle_mouse_process(self, mouse_left_up, mouse_right_up, mouse_left_down, mouse_right_down, key_state):
    if self.event_log.rect.collidepoint(self.mouse_pos):  # check mouse collide for event log ui
        if self.event_log.scroll.rect.collidepoint(
                self.mouse_pos):  # Must check mouse collide for scroll before event log ui
            if mouse_left_down or mouse_left_up:
                new_row = self.event_log.scroll.player_input(self.mouse_pos)
                if self.event_log.current_start_row != new_row:
                    self.event_log.current_start_row = new_row
                    self.event_log.recreate_image()

    elif self.effect_icon_mouse_over(self.skill_icon, mouse_right_up):
        pass
    elif self.effect_icon_mouse_over(self.effect_icon, mouse_right_up):
        pass

    if self.player_char and self.player_char.alive:
        self.player_char.player_input(self.command_mouse_pos, mouse_left_up=mouse_left_up,
                                      mouse_right_up=mouse_right_up, mouse_left_down=mouse_left_down,
                                      mouse_right_down=mouse_right_down, key_state=key_state)
