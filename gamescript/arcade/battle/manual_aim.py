import pygame


def manual_aim(self, key_press, mouse_pos, mouse_left_up, mouse_right_up):
    if key_press == pygame.K_q:  # Cancel manual aim
        self.camera_zoom = 10
        self.camera_zoom_change()
        self.player_input_state = None
        self.cursor.change_image("normal")
    if mouse_left_up:
        pass
