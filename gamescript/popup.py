import pygame
import pygame.freetype


class TerrainPopup(pygame.sprite.Sprite):
    images = []
    screen_rect = None

    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.scaleadjust = (
                self.screen_rect.width * self.screen_rect.height / (1366 * 768))  # For adjusting the image and text according to screen size
        self.image = pygame.transform.scale(self.images[0], (int(self.images[0].get_width() * self.scaleadjust),
                                                             int(self.images[0].get_height() * self.scaleadjust)))
        self.font = pygame.font.SysFont("helvetica", int(16 * self.scaleadjust))
        self.heightfont = pygame.font.SysFont("helvetica", int(12 * self.scaleadjust))
        self.img_pos = ((24 * self.scaleadjust, 34 * self.scaleadjust), (24 * self.scaleadjust, 53 * self.scaleadjust),  # inf speed, inf atk
                        (24 * self.scaleadjust, 70 * self.scaleadjust), (58 * self.scaleadjust, 34 * self.scaleadjust),  # inf def, cav speed
                        (58 * self.scaleadjust, 53 * self.scaleadjust), (58 * self.scaleadjust, 70 * self.scaleadjust),  # cav atk, cav def
                        (90 * self.scaleadjust, 34 * self.scaleadjust), (90 * self.scaleadjust, 53 * self.scaleadjust))  # range def, discipline
        self.mod_list = (1.5, 1.2, 1, 0.7, 0.5, 0)  # Stat effect level from terrain, used for select what mod image to use
        self.bonus_list = (40, 20, 10, -20, -50, -2000)  # Stat bonus level from terrain, used for select what mod image to use

        self.image_original = self.image.copy()

    def pop(self, pos, feature, height):
        """pop out into screen, blit input into the image"""
        self.image = self.image_original.copy()  # reset image to default empty one
        self.pos = pos  # position to draw the image on screen

        # v Terrain feature name
        text_surface = self.font.render(feature[0], True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(5, 5))
        self.image.blit(text_surface, text_rect)
        # ^ End terrain feature

        # v Height number
        text_surface = self.heightfont.render(str(height), True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(self.image.get_width() - (self.image.get_width() / 5), 5))
        self.image.blit(text_surface, text_rect)
        # End height

        for index, imgpos in enumerate(self.img_pos[0:6]):  # text for each stat modifier
            if feature[index + 1] == 1:  # draw circle if modifier is 1 (no effect to stat)
                imagerect = self.images[7].get_rect(center=imgpos)  # images[7] is circle icon image
                self.image.blit(self.images[7], imagerect)
            else:  # upper or lower (^v) arrow icon to indicate modifier level
                for modindex, mod in enumerate(self.mod_list):  # loop to find ^v arrow icon for the modifier
                    if feature[index + 1] >= mod:  # draw appropiate icon if modifier is higher than the number of list item
                        imagerect = self.images[modindex + 1].get_rect(center=imgpos)
                        self.image.blit(self.images[modindex + 1], imagerect)
                        break  # found arrow image to blit end loop

        # v range def modifier for both infantry and cavalry
        if feature[7] == 0:  # no bonus, draw circle
            imagerect = self.images[7].get_rect(center=self.img_pos[6])
            self.image.blit(self.images[7], imagerect)
        else:
            for modindex, mod in enumerate(self.bonus_list):
                if feature[7] >= mod:
                    imagerect = self.images[modindex + 1].get_rect(center=self.img_pos[6])
                    self.image.blit(self.images[modindex + 1], imagerect)
                    break
        # ^ End range def modifier

        # v discipline modifier for both infantry and cavalry
        if feature[9] == 0:
            imagerect = self.images[7].get_rect(center=self.img_pos[7])
            self.image.blit(self.images[7], imagerect)
        else:
            for modindex, mod in enumerate(self.bonus_list):
                if feature[9] >= mod:
                    imagerect = self.images[modindex + 1].get_rect(center=self.img_pos[7])
                    self.image.blit(self.images[modindex + 1], imagerect)
                    break
        # ^ End discipline modifier

        self.rect = self.image.get_rect(bottomleft=self.pos)


class OnelinePopup(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 15
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", 18)
        self.pos = (0, 0)
        self.textinput = ""

    def pop(self, pos, textinput):
        """Pop out text box with input text in one line"""
        if self.pos != pos or self.textinput != textinput:
            self.textinput = textinput
            self.pos = pos
            text_surface = self.font.render(self.textinput, True, (0, 0, 0))  # text input font surface
            text_rect = text_surface.get_rect(topleft=(1, 1))  # text input position at (1,1) on white box image
            self.image = pygame.Surface((text_rect.width + 6, text_rect.height + 6))  # black border
            image = pygame.Surface((text_rect.width + 2, text_rect.height + 2))  # white Box
            image.fill((255, 255, 255))
            image.blit(text_surface, text_rect)  # blit text into white box
            rect = self.image.get_rect(topleft=(2, 2))  # white box image position at (2,2) on black border image
            self.image.blit(image, rect)  # blit white box into black border image to create text box image
            self.rect = self.image.get_rect(bottomleft=self.pos)


class EffecticonPopup(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.headfont = pygame.font.SysFont("helvetica", 16)
        self.font = pygame.font.SysFont("helvetica", 12)
        self.pos = (0, 0)
        self.textinput = ""

    def pop(self, pos, textinput):
        if self.pos != pos or self.textinput != textinput:
            self.textinput = textinput
            self.pos = pos
            name_surface = self.headfont.render(self.textinput[0], True, (0, 0, 0))  # name font surface
            name_rect = name_surface.get_rect(topleft=(1, 1))  # text input position at (1,1) on white box image
            # text_surface = self.font.render(self.textinput[-1], 1, (0, 0, 0))  ## description
            # text_rect = text_surface.get_rect(topleft=(1, text_rect.height + 1))
            self.image = pygame.Surface((name_rect.width + 6, name_rect.height + 6))  # black border
            image = pygame.Surface((name_rect.width + 2, name_rect.height + 2))  # white Box for text
            # self.image = pygame.Surface((namerect.width + 6, text_rect.height + namerect.height + 6)) ## Black border
            # image = pygame.Surface((namerect.width + 2, text_rect.height + namerect.height + 2)) ## White Box for text
            image.fill((255, 255, 255))
            image.blit(name_surface, name_rect)  # blit text into white box
            # image.blit(text_surface, text_rect)
            rect = self.image.get_rect(topleft=(2, 2))  # white box image position at (2,2) on black border image
            self.image.blit(image, rect)  # blit white box into black border image to create text box image
            self.rect = self.image.get_rect(bottomleft=self.pos)
