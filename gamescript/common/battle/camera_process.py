import pygame


def camera_process(self):
    if self.camera_mode == "Free":
        if self.player_keyboard_hold["Move Down"] or self.mouse_pos[1] >= self.bottom_corner:  # Camera move down
            self.true_camera_pos[1] += 4
            self.camera_fix()

        elif self.player_keyboard_hold["Move Up"] or self.mouse_pos[1] <= 5:  # Camera move up
            self.true_camera_pos[1] -= 4
            self.camera_fix()

        if self.player_keyboard_hold["Move Left"] or self.mouse_pos[0] <= 5:  # Camera move left
            self.true_camera_pos[0] -= 4
            self.camera_fix()

        elif self.player_keyboard_hold["Move Right"] or self.mouse_pos[0] >= self.right_corner:  # Camera move right
            self.true_camera_pos[0] += 4
            self.camera_fix()

    elif self.camera_mode == "Follow":
        self.true_camera_pos = self.player_char.base_pos
        self.camera_fix()
