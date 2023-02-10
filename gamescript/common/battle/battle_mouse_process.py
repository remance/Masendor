def battle_mouse_process(self, mouse_left_up, mouse_right_up, double_mouse_right, mouse_left_down, mouse_right_down,
                         key_state, key_press):
    if self.event_log.rect.collidepoint(self.mouse_pos):  # check mouse collide for event log ui
        self.click_any = True
        if self.event_log.scroll.rect.collidepoint(
                self.mouse_pos):  # Must check mouse collide for scroll before event log ui
            if mouse_left_down or mouse_left_up:
                self.click_any = True
                new_row = self.event_log.scroll.player_input(self.mouse_pos)
                if self.event_log.current_start_row != new_row:
                    self.event_log.current_start_row = new_row
                    self.event_log.recreate_image()

    elif self.ui_mouse_click():  # check mouse collide for other ui
        pass

    if self.player_char.alive:
        self.player_char.player_input(self.command_mouse_pos, mouse_left_up=mouse_left_up,
                                      mouse_right_up=mouse_right_up, mouse_left_down=mouse_left_down,
                                      mouse_right_down=mouse_right_down, double_mouse_right=double_mouse_right,
                                      key_state=key_state)
