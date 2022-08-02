import pygame


def camera_process(self, key_state):
    if self.camera_mode == "Free":
        if key_state[pygame.K_s] or self.mouse_pos[1] >= self.bottom_corner:  # Camera move down
            self.base_camera_pos[1] += 4 * (
                    11 - self.camera_zoom)  # need "11 -" for converting cameral scale so the further zoom camera move faster
            self.camera_pos[1] = self.base_camera_pos[1] * self.camera_zoom  # resize camera pos
            self.camera_fix()

        elif key_state[pygame.K_w] or self.mouse_pos[1] <= 5:  # Camera move up
            self.base_camera_pos[1] -= 4 * (11 - self.camera_zoom)
            self.camera_pos[1] = self.base_camera_pos[1] * self.camera_zoom
            self.camera_fix()

        if key_state[pygame.K_a] or self.mouse_pos[0] <= 5:  # Camera move left
            self.base_camera_pos[0] -= 4 * (11 - self.camera_zoom)
            self.camera_pos[0] = self.base_camera_pos[0] * self.camera_zoom
            self.camera_fix()

        elif key_state[pygame.K_d] or self.mouse_pos[0] >= self.right_corner:  # Camera move right
            self.base_camera_pos[0] += 4 * (11 - self.camera_zoom)
            self.camera_pos[0] = self.base_camera_pos[0] * self.camera_zoom
            self.camera_fix()

    elif self.camera_mode == "Follow":
        self.base_camera_pos = pygame.Vector2(self.player_char.base_pos[0] * self.screen_scale[0],
                                              self.player_char.base_pos[1] * self.screen_scale[1])
        self.camera_pos = self.base_camera_pos * self.camera_zoom
        self.camera_fix()
