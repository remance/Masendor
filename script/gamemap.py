import pygame
import pygame.freetype

from RTS import mainmenu

main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

class map(pygame.sprite.Sprite):
    images = []

    def __init__(self):
        """Scrollable and zoomable map, image file of map should be at 1000x1000 then it will be scaled in game"""
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.scale = 10
        MAP_WIDTH = self.image.get_width() * self.scale
        MAP_HEIGHT = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(MAP_WIDTH, MAP_HEIGHT)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.rect = self.image.get_rect(center=(SCREENRECT.width/2,SCREENRECT.height/2))
        self.pos = self.rect.center

    # def update(self, dt, pos, zoom):
    #     self.image = self.image_original
    #     self.pos = pygame.Vector2(pos[0], pos[1])

    # def draw(self, gamescreen):
    #     # self.image = pygame.transform.scale(self.battlemap.image_original, (self.dim[0], self.dim[1]))
    #     gamescreen.blit(self.image, self.pos)

class mapfeature(pygame.sprite.Sprite):
    images = []

    def __init__(self, x, y, image):
        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.containers)
# Surface.get_at((x, y)) ##get colour at pos maybe can be used to create map from just picture?
