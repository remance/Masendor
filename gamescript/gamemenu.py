import pygame
import pygame.freetype


class Menubox(pygame.sprite.Sprite):
    images = []
    SCREENRECT = None

    def __init__(self):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (self.SCREENRECT.width / 2, self.SCREENRECT.height / 2)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.mode = 0 # Current menu mode

    def changemode(self, mode):
        """Change between 0 menu, 1 option, 2 enclopedia mode"""
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
        if text != "": # blit menu text into button image
            self.textsurface = self.font.render(self.text, 1, (0, 0, 0))
            self.textrect = self.textsurface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(self.textsurface, self.textrect) # button idle image
            self.images[1].blit(self.textsurface, self.textrect) # button mouse over image
            self.images[2].blit(self.textsurface, self.textrect) # button click image
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
        self.minvalue = self.pos[0] - (self.image.get_width() / 2) + 10.5 # min value position of the scroll bar
        self.maxvalue = self.pos[0] + (self.image.get_width() / 2) - 10.5 # max value position
        self.value = value
        self.mouse_value = (self.slidersize * value / 100) + 10.5 # mouse position on the scroll bar convert to value
        self.image_original = self.image.copy()
        self.buttonrect = self.buttonimagelist[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.buttonimage, self.buttonrect)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, mouse_pos, valuebox, forcedvalue=False):
        """Update slider value and position"""
        if forcedvalue == False:
            self.mouse_value = mouse_pos[0]
            if self.mouse_value > self.maxvalue:
                self.mouse_value = self.maxvalue
            if self.mouse_value < self.minvalue:
                self.mouse_value = self.minvalue
            self.value = (self.mouse_value - self.minvalue) / 2
            self.mouse_value = (self.slidersize * self.value / 100) + 10.5
        else:  ## For revert, cancel or esc in the option menu
            self.value = mouse_pos
            self.mouse_value = (self.slidersize * self.value / 100) + 10.5
        self.image = self.image_original.copy()
        self.buttonrect = self.buttonimagelist[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
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
