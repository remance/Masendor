def battle_mouse_process(self, mouse_left_up, mouse_right_up, double_mouse_right, mouse_left_down, mouse_right_down,
                         key_state, key_press):
    if self.event_log.rect.collidepoint(self.mouse_pos):  # check mouse collide for event log ui
        self.click_any = True
        if self.event_log.scroll.rect.collidepoint(self.mouse_pos):  # Must check mouse collide for scroll before event log ui
            if mouse_left_down or mouse_left_up:
                self.click_any = True
                new_row = self.event_log.scroll.player_input(self.mouse_pos)
                if self.event_log.current_start_row != new_row:
                    self.event_log.current_start_row = new_row
                    self.event_log.recreate_image()

    elif self.ui_mouse_click():  # check mouse collide for other ui
        pass

    else:
        for index, button in enumerate(self.event_log_button):  # Event log button and timer button click
            if button.rect.collidepoint(self.mouse_pos):
                if index in (0, 1, 2, 3, 4, 5):  # event_log button
                    self.click_any = True
                    if mouse_left_up:
                        if button.event in (0, 1, 2, 3):  # change tab mode
                            self.event_log.change_mode(button.event)
                        elif button.event == 4:  # delete tab log button
                            self.event_log.clear_tab()
                        elif button.event == 5:  # delete all tab log button
                            self.event_log.clear_tab(all_tab=True)
                break

    if self.current_selected.state != 100:
        self.current_selected.player_input(self.command_mouse_pos, mouse_left_up, mouse_right_up, mouse_left_down,
                                           mouse_right_down, double_mouse_right, self.last_mouseover, key_state)
