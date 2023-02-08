import pygame


def sprite_scaling(self):
    self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                              self.base_pos[1] * self.screen_scale[1])
    self.rect = self.image.get_rect(center=self.pos)
