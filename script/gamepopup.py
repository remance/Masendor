import pygame
import pygame.freetype

class Terrainpopup(pygame.sprite.Sprite):
    images = []

    def __init__(self):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.font = pygame.font.SysFont("helvetica", 12)
        self.imgpos = ((24, 34),(24, 53),(24, 70),(58, 34),(58, 53),(58, 70)) ## inf speed, atk, def, cav speed, atk, def, all range def
        self.modlist = (150,120,100,70,50,0)
        self.bonuslist = (40, 20, 0)
        self.image_original = self.image.copy()

    def pop(self, pos, input):
        self.image = self.image_original.copy()
        self.pos = pos
        self.textsurface = self.font.render(input[0], 1, (0, 0, 0)) ## terrain feature name
        self.textrect = self.textsurface.get_rect(topleft=(5,5))
        self.image.blit(self.textsurface, self.textrect)
        for index, pos in enumerate(self.imgpos):
            if input[index+1] == 100:
                self.imagerect = self.images[7].get_rect(center=pos)
                self.image.blit(self.images[7], self.imagerect)
            else:
                for modindex, mod in enumerate(self.modlist):
                    if input[index + 1] >= mod:
                        self.imagerect = self.images[modindex+1].get_rect(center=pos)
                        self.image.blit(self.images[modindex+1], self.imagerect)
                        break
        if input[7] == 0:
            self.imagerect = self.images[7].get_rect(center=(90, 34))
            self.image.blit(self.images[7], self.imagerect)
        else:
            for modindex, mod in enumerate(self.bonuslist):
                if input[7] >= mod:
                    self.imagerect = self.images[modindex + 1].get_rect(center=(90, 34))
                    self.image.blit(self.images[modindex + 1], self.imagerect)
                    break
        self.rect = self.image.get_rect(bottomleft=self.pos)

class Onelinepopup(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", 18)
        self.pos = (0,0)
        self.textinput = ""

    def pop(self, pos, input):
        if self.pos != pos or self.textinput != input:
            self.textinput = input
            self.pos = pos
            self.textsurface = self.font.render(self.textinput, 1, (0, 0, 0))  ## button name
            self.textrect = self.textsurface.get_rect(topleft=(1, 1))
            self.image = pygame.Surface((self.textrect.width+6, self.textrect.height+6))
            image = pygame.Surface((self.textrect.width+2, self.textrect.height+2))
            image.fill((255,255,255))
            image.blit(self.textsurface, self.textrect)
            rect = self.image.get_rect(topleft=(2,2))
            self.image.blit(image,rect)
            self.rect = self.image.get_rect(bottomleft=self.pos)