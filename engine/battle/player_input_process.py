def player_input_process(self):
    if self.event_log.rect.collidepoint(self.player1_battle_cursor.pos):  # check mouse collide for event log ui
        if self.event_log.scroll.rect.collidepoint(
                self.player1_battle_cursor.pos):  # Must check mouse collide for scroll before event log ui
            if self.player1_key_hold["Main Weapon Attack"] or self.player1_key_press["Main Weapon Attack"]:
                new_row = self.event_log.scroll.player_input(self.player1_battle_cursor.pos)
                if self.event_log.current_start_row != new_row:
                    self.event_log.current_start_row = new_row
                    self.event_log.recreate_image()

    if self.player_unit and self.player_unit.alive:
        if self.player1_key_press["Toggle Run"]:
            if self.player_unit.toggle_run:
                self.player_unit.toggle_run = False
            else:
                self.player_unit.toggle_run = True
        if self.player1_key_press["Auto Move"]:
            if self.player_unit.auto_move:
                self.player_unit.auto_move = False
            else:
                self.player_unit.auto_move = True
        self.player_unit.player_input(self.command_cursor_pos)

    if self.player1_key_press["Order Menu"]:  # Open unit command wheel ui
        self.add_ui_updater(self.wheel_ui)
        self.previous_player_input_state = self.player_input_state
        self.player_input_state = self.wheel_ui
        self.wheel_ui.generate(self.unit_behaviour_wheel["Main"])
