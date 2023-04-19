import pygame


def player_input_process(self):
    if self.event_log.rect.collidepoint(self.mouse_pos):  # check mouse collide for event log ui
        if self.event_log.scroll.rect.collidepoint(
                self.mouse_pos):  # Must check mouse collide for scroll before event log ui
            if self.player_keyboard_hold["Main Weapon Attack"] or self.player_keyboard_press["Main Weapon Attack"]:
                new_row = self.event_log.scroll.player_input(self.mouse_pos)
                if self.event_log.current_start_row != new_row:
                    self.event_log.current_start_row = new_row
                    self.event_log.recreate_image()

    if self.player_char and self.player_char.alive:
        self.player_char.player_input(self.command_mouse_pos)

    if self.player_keyboard_press["Order Menu"]:  # Open unit command wheel ui
        self.battle_ui_updater.add(self.wheel_ui)
        self.previous_player_input_state = self.player_input_state
        self.player_input_state = self.wheel_ui
        self.wheel_ui.generate(self.unit_behaviour_wheel["Main"])

