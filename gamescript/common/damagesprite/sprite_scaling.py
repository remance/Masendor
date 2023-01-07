import pygame


def sprite_scaling(self):
    if self.camera_scale <= 1:
        self.camera_scale = 1
        self.image = self.base_image.copy()
    else:
        self.image = pygame.transform.smoothscale(self.base_image,
                                                  (int(self.base_image.get_width() / self.camera_scale),
                                                   int(self.base_image.get_height() / self.camera_scale)))

    self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                              self.base_pos[1] * self.screen_scale[1]) * self.camera_zoom
    self.rect = self.image.get_rect(center=self.pos)
