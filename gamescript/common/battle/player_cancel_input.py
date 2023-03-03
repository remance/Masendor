def player_cancel_input(self):
    if self.player_char.alive:
        self.camera_mode = "Follow"
    self.cursor.change_image("normal")
    self.battle_ui_updater.remove(self.single_text_popup)
    self.previous_player_input_state = self.player_input_state
    self.player_input_state = None
    for shoot_line in self.shoot_lines:
        shoot_line.delete()  # reset shoot guide lines
