import pygame


def adjust_sprite(self):
    # if self.scale_size > 1:
    #     self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() * self.scale_size,
    #                                                            self.image.get_height() * self.scale_size))

    if self.angle:
        self.image = pygame.transform.rotate(self.image, self.angle)

    self.rect = self.image.get_rect(center=self.pos)
