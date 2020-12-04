import pygame
import pygame.freetype


class Terrainpopup(pygame.sprite.Sprite):
    images = []
    SCREENRECT = None

    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.scaleadjust = (self.SCREENRECT.width * self.SCREENRECT.height / (1366 * 768)) # For adjusting the image and text according to screen size
        self.image = pygame.transform.scale(self.images[0], (int(self.images[0].get_width()*self.scaleadjust),
                                                             int(self.images[0].get_height()*self.scaleadjust)))
        self.font = pygame.font.SysFont("helvetica", int(16*self.scaleadjust))
        self.imgpos = ((24*self.scaleadjust, 34*self.scaleadjust), (24*self.scaleadjust, 53*self.scaleadjust), # inf speed, inf atk
                       (24*self.scaleadjust, 70*self.scaleadjust), (58*self.scaleadjust, 34*self.scaleadjust), # inf def, cav speed
                       (58*self.scaleadjust, 53*self.scaleadjust), (58*self.scaleadjust, 70*self.scaleadjust), # cav atk, cav def
                       (90*self.scaleadjust, 34*self.scaleadjust), (90*self.scaleadjust, 53*self.scaleadjust)) # range def, discipline
        self.modlist = (1.5, 1.2, 1, 0.7, 0.5, 0) # Stat effect level from terrain, used for select what mod image to use
        self.bonuslist = (40, 20, 10, -20, -50, -2000) # Stat bonus level from terrain, used for select what mod image to use

        self.image_original = self.image.copy()

    def pop(self, pos, feature, height):
        """pop out into screen, blit input into the image"""
        self.image = self.image_original.copy() # reset image to default empty one
        self.pos = pos # position to draw the image on screen

        #v Terrain feature name
        self.textsurface = self.font.render(feature[0], 1, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(topleft=(5, 5))
        self.image.blit(self.textsurface, self.textrect)
        #^ End terrain feature

        #v Height
        self.textsurface = self.font.render(str(height), 1, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(topleft=(100, 5))
        self.image.blit(self.textsurface, self.textrect)
        # End height

        for index, imgpos in enumerate(self.imgpos[0:6]): # text for each stat modifier
            if feature[index + 1] == 1: # draw circle if modifier is 1 (no effect to stat)
                self.imagerect = self.images[7].get_rect(center = imgpos) # images[7] is circle icon image
                self.image.blit(self.images[7], self.imagerect)
            else: # upper or lower (^v) arrow icon to indicate modifier level
                for modindex, mod in enumerate(self.modlist): # loop to find ^v arrow icon for the modifier
                    if feature[index + 1] >= mod: # draw appropiate icon if modifier is higher than the number of list item
                        self.imagerect = self.images[modindex + 1].get_rect(center = imgpos)
                        self.image.blit(self.images[modindex + 1], self.imagerect)
                        break # found arrow image to blit end loop

        #v range def modifier for both infantry and cavalry
        print(feature[7:10])
        if feature[7] == 0: # no bonus, draw circle
            self.imagerect = self.images[7].get_rect(center=self.imgpos[6])
            self.image.blit(self.images[7], self.imagerect)
        else:
            for modindex, mod in enumerate(self.bonuslist):
                if feature[7] >= mod:
                    self.imagerect = self.images[modindex + 1].get_rect(center = self.imgpos[6])
                    self.image.blit(self.images[modindex + 1], self.imagerect)
                    break
        #^ End range def modifier

        #v discipline modifier for both infantry and cavalry
        if feature[9] == 0:
            self.imagerect = self.images[7].get_rect(center=self.imgpos[7])
            self.image.blit(self.images[7], self.imagerect)
        else:
            for modindex, mod in enumerate(self.bonuslist):
                if feature[9] >= mod:
                    print(mod)
                    self.imagerect = self.images[modindex + 1].get_rect(center = self.imgpos[7])
                    self.image.blit(self.images[modindex + 1], self.imagerect)
                    break
        # ^ End discipline modifier

        self.rect = self.image.get_rect(bottomleft=self.pos)

class Onelinepopup(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", 18)
        self.pos = (0, 0)
        self.textinput = ""

    def pop(self, pos, input):
        """Pop out text box with input text in one line"""
        if self.pos != pos or self.textinput != input:
            self.textinput = input
            self.pos = pos
            textsurface = self.font.render(self.textinput, 1, (0, 0, 0))  ## text input font surface
            textrect = textsurface.get_rect(topleft=(1, 1)) # text input position at (1,1) on white box image
            self.image = pygame.Surface((textrect.width + 6, textrect.height + 6))  ## Black border
            image = pygame.Surface((textrect.width + 2, textrect.height + 2))  ## White Box
            image.fill((255, 255, 255))
            image.blit(textsurface, textrect) # blit text into white box
            rect = self.image.get_rect(topleft=(2, 2)) # white box image position at (2,2) on black border image
            self.image.blit(image, rect) # blit white box into black border image to create text box image
            self.rect = self.image.get_rect(bottomleft=self.pos)


class Effecticonpopup(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.headfont = pygame.font.SysFont("helvetica", 16)
        self.font = pygame.font.SysFont("helvetica", 12)
        self.pos = (0, 0)
        self.textinput = ""

    def pop(self, pos, input):
        if self.pos != pos or self.textinput != input:
            self.textinput = input
            self.pos = pos
            namesurface = self.headfont.render(self.textinput[0], 1, (0, 0, 0))  # name font surface
            namerect = namesurface.get_rect(topleft=(1, 1)) # text input position at (1,1) on white box image
            # textsurface = self.font.render(self.textinput[-1], 1, (0, 0, 0))  ## description
            # textrect = textsurface.get_rect(topleft=(1, textrect.height + 1))
            self.image = pygame.Surface((namerect.width + 6, namerect.height + 6))  ## Black border
            image = pygame.Surface((namerect.width + 2, namerect.height + 2))  ## White Box for text
            # self.image = pygame.Surface((namerect.width + 6, textrect.height + namerect.height + 6)) ## Black border
            # image = pygame.Surface((namerect.width + 2, textrect.height + namerect.height + 2)) ## White Box for text
            image.fill((255, 255, 255))
            image.blit(namesurface, namerect) # blit text into white box
            # image.blit(textsurface, textrect)
            rect = self.image.get_rect(topleft=(2, 2)) # white box image position at (2,2) on black border image
            self.image.blit(image, rect) # blit white box into black border image to create text box image
            self.rect = self.image.get_rect(bottomleft=self.pos)
