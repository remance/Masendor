def player_cancel_input(self):
    if self.player_unit.alive:
        self.camera_mode = "Follow"
    self.player1_battle_cursor.change_image("normal")
    self.remove_ui_updater(self.text_popup)
    self.previous_player_input_state = self.player_input_state
    self.player_input_state = None
    for shoot_line in self.shoot_lines:
        shoot_line.who.manual_shoot = False
        shoot_line.delete()  # reset shoot guide lines
