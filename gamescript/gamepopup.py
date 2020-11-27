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
                       (58*self.scaleadjust, 53*self.scaleadjust), (58*self.scaleadjust, 70*self.scaleadjust)) # cav atk, cav def
        self.modlist = (1.5, 1.2, 1, 0.7, 0.5, 0) # Stat effect level from terrain, used for select what mod image to use
        self.bonuslist = (40, 20, 10, -20, -50, -2000) # Stat bonus level from terrain, used for select what mod image to use

        self.image_original = self.image.copy()

    def pop(self, pos, input):
        self.image = self.image_original.copy()
        self.pos = pos
        self.textsurface = self.font.render(input[0], 1, (0, 0, 0))  ## terrain feature name
        self.textrect = self.textsurface.get_rect(topleft=(5, 5))
        self.image.blit(self.textsurface, self.textrect)
        for index, pos in enumerate(self.imgpos):
            if input[index + 1] == 1:
                self.imagerect = self.images[7].get_rect(center=pos)
                self.image.blit(self.images[7], self.imagerect)
            else:
                for modindex, mod in enumerate(self.modlist):
                    if input[index + 1] >= mod:
                        self.imagerect = self.images[modindex + 1].get_rect(center=pos)
                        self.image.blit(self.images[modindex + 1], self.imagerect)
                        break
        if input[7] == 0: # all range def
            self.imagerect = self.images[7].get_rect(center=(90*self.scaleadjust, 34*self.scaleadjust))
            self.image.blit(self.images[7], self.imagerect)
        else:
            for modindex, mod in enumerate(self.bonuslist):
                if input[7] >= mod:
                    self.imagerect = self.images[modindex + 1].get_rect(center=(90*self.scaleadjust, 34*self.scaleadjust))
                    self.image.blit(self.images[modindex + 1], self.imagerect)
                    break
        if input[9] == 0: # discipline
            self.imagerect = self.images[7].get_rect(center=(90*self.scaleadjust, 53*self.scaleadjust))
            self.image.blit(self.images[7], self.imagerect)
        else:
            for modindex, mod in enumerate(self.bonuslist):
                if input[9] >= mod:
                    self.imagerect = self.images[modindex + 1].get_rect(center=(90*self.scaleadjust, 53*self.scaleadjust))
                    self.image.blit(self.images[modindex + 1], self.imagerect)
                    break
        self.rect = self.image.get_rect(bottomleft=self.pos)


class Onelinepopup(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", 18)
        self.pos = (0, 0)
        self.textinput = ""

    def pop(self, pos, input):
        if self.pos != pos or self.textinput != input:
            self.textinput = input
            self.pos = pos
            textsurface = self.font.render(self.textinput, 1, (0, 0, 0))  ## button name
            textrect = textsurface.get_rect(topleft=(1, 1))
            self.image = pygame.Surface((textrect.width + 6, textrect.height + 6))  ## Black border
            image = pygame.Surface((textrect.width + 2, textrect.height + 2))  ## White Box
            image.fill((255, 255, 255))
            image.blit(textsurface, textrect)
            rect = self.image.get_rect(topleft=(2, 2))
            self.image.blit(image, rect)
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
            namesurface = self.headfont.render(self.textinput[0], 1, (0, 0, 0))  ## name
            namerect = namesurface.get_rect(topleft=(1, 1))
            # textsurface = self.font.render(self.textinput[-1], 1, (0, 0, 0))  ## description
            # textrect = textsurface.get_rect(topleft=(1, textrect.height + 1))
            self.image = pygame.Surface((namerect.width + 6, namerect.height + 6))  ## Black border
            image = pygame.Surface((namerect.width + 2, namerect.height + 2))  ## White Box for text
            # self.image = pygame.Surface((namerect.width + 6, textrect.height + namerect.height + 6)) ## Black border
            # image = pygame.Surface((namerect.width + 2, textrect.height + namerect.height + 2)) ## White Box for text
            image.fill((255, 255, 255))
            image.blit(namesurface, namerect)
            # image.blit(textsurface, textrect)
            rect = self.image.get_rect(topleft=(2, 2))
            self.image.blit(image, rect)
            self.rect = self.image.get_rect(bottomleft=self.pos)
