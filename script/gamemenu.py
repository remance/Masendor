import pygame
import pygame.freetype
from RTS import mainmenu

main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

class Menubox(pygame.sprite.Sprite):
    images = []

    def __init__(self):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (SCREENRECT.width/2, SCREENRECT.height/2)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.mode = 0

    def changemode(self, mode):
        self.mode = mode
        self.image = self.images[mode]


class Menubutton(pygame.sprite.Sprite):
    def __init__(self, images, pos, text="", size=16):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.images = [image.copy() for image in images]
        self.text = text
        self.font = pygame.font.SysFont("timesnewroman", size)
        if text != "":
            self.textsurface = self.font.render(self.text, 1, (0, 0, 0))
            self.textrect = self.textsurface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(self.textsurface, self.textrect)
            self.images[1].blit(self.textsurface, self.textrect)
            self.images[2].blit(self.textsurface, self.textrect)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.event = False

class Slidermenu(pygame.sprite.Sprite):
    def __init__(self, barimage, buttonimage, pos, value, type):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.type = type
        self.image = barimage
        self.buttonimagelist = buttonimage
        self.buttonimage = self.buttonimagelist[0]
        self.slidersize = self.image.get_size()[0] - 20
        self.min_value = self.pos[0] - (self.image.get_width()/2) + 10.5
        self.max_value = self.pos[0] + (self.image.get_width()/2) - 10.5
        self.value = value
        self.mouse_value = (self.slidersize * value / 100)+10.5
        self.image_original = self.image.copy()
        self.buttonrect = self.buttonimagelist[1].get_rect(center=(self.mouse_value, self.image.get_height()/2))
        self.image.blit(self.buttonimage, self.buttonrect)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, mouse_pos, valuebox, forcedvalue = False):
        if forcedvalue is False:
            self.mouse_value = mouse_pos[0]
            if self.mouse_value > self.max_value:
                self.mouse_value = self.max_value
            if self.mouse_value < self.min_value:
                self.mouse_value = self.min_value
            self.value = (self.mouse_value - self.min_value) / 2
            self.mouse_value = (self.slidersize * self.value / 100)+10.5
        else: ## For revert or cancel
            self.value = mouse_pos
            self.mouse_value = (self.slidersize * self.value / 100) + 10.5
        self.image = self.image_original.copy()
        self.buttonrect = self.buttonimagelist[1].get_rect(center=(self.mouse_value, self.image.get_height()/2))
        self.image.blit(self.buttonimage, self.buttonrect)
        valuebox.update(self.value)

class Valuebox(pygame.sprite.Sprite):
    def __init__(self, textimage, pos, value, textsize=16):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("timesnewroman", textsize)
        self.pos = pos
        self.image = pygame.transform.scale(textimage, (int(textimage.get_size()[0] / 2), int(textimage.get_size()[1] / 2)))
        self.image_original = self.image.copy()
        self.value = value
        self.textsurface = self.font.render(str(self.value), 1, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.textsurface, self.textrect)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, value):
        self.value = value
        self.image = self.image_original.copy()
        self.textsurface = self.font.render(str(self.value), 1, (0, 0, 0))
        self.image.blit(self.textsurface, self.textrect)
