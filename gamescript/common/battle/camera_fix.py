import pygame


def camera_fix(self):
    if self.base_camera_pos[0] > self.max_camera[0]:  # camera cannot go further than 999 x
        self.base_camera_pos[0] = self.max_camera[0]
    elif self.base_camera_pos[0] < 0:  # camera cannot go less than 0 x
        self.base_camera_pos[0] = 0

    if self.base_camera_pos[1] > self.max_camera[1]:  # same for y
        self.base_camera_pos[1] = self.max_camera[1]
    elif self.base_camera_pos[1] < 0:
        self.base_camera_pos[1] = 0

    self.true_camera_pos = pygame.Vector2(self.base_camera_pos[0] / self.screen_scale[0],
                                          self.base_camera_pos[1] / self.screen_scale[1])

    self.camera_topleft_corner = (self.camera_pos[0] - self.center_screen[0],
                                  self.camera_pos[1] - self.center_screen[
                                      1])  # calculate top left corner of camera position
