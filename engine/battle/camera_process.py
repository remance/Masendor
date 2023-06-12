def camera_process(self):
    if self.camera_mode == "Free":
        if self.player1_key_hold["Move Down"] or self.player1_battle_cursor.pos[1] >= self.bottom_corner:
            self.true_camera_pos[1] += 4
            self.camera_fix()

        elif self.player1_key_hold["Move Up"] or self.player1_battle_cursor.pos[1] <= 5:
            self.true_camera_pos[1] -= 4
            self.camera_fix()

        if self.player1_key_hold["Move Left"] or self.player1_battle_cursor.pos[0] <= 5:
            self.true_camera_pos[0] -= 4
            self.camera_fix()

        elif self.player1_key_hold["Move Right"] or self.player1_battle_cursor.pos[0] >= self.right_corner:
            self.true_camera_pos[0] += 4
            self.camera_fix()

    elif self.camera_mode == "Follow":
        self.true_camera_pos = self.player_unit.base_pos
        self.camera_fix()
