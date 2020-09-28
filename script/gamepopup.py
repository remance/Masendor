import pygame
import pygame.freetype

class terrainpopup(pygame.sprite.Sprite):
    def __init__(self, X, Y, input):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.X, self.Y = X, Y
        # self.image = image
        self.rect = self.image.get_rect(center=(self.X, self.Y))
