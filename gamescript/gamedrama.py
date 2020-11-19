import pygame
import pygame.freetype

class Textdrama(pygame.sprite.Sprite):
    images = []
    SCREENRECT = None

    def __init__(self):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.body = self.images[0]
        self.leftcorner = self.images[1]
        self.rightcorner = self.images[2]
        self.pos = (self.SCREENRECT.width / 2, self.SCREENRECT.height / 4) # The center pos of the drama popup on screen
        self.font = pygame.font.SysFont("helvetica", 70)
        self.queue = [] # Text list to popup

    def processqueue(self):
        """Initiate the first text in list and remove it"""
        self.slowdrama(self.queue[0]) # Process the first item in list
        self.queue = self.queue[1:] # Delete already processed item

    def slowdrama(self, input):
        self.textblit = False
        self.currentlength = 20 # Current unfolded length
        self.textinput = input
        self.leftcornerrect = self.leftcorner.get_rect(topleft=(0, 0)) # The starting point
        self.textsurface = self.font.render(self.textinput, 1, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(topleft=(30, 1))
        self.image = pygame.Surface((self.textrect.width + 70, self.textrect.height), pygame.SRCALPHA)
        self.image.blit(self.leftcorner, self.leftcornerrect)
        self.rect = self.image.get_rect(center=self.pos)
        self.maxlength = self.image.get_width() - 20 # Max length of the body, not counting the end corner

    def playanimation(self):
        """Play unfold animation and blit drama text at the end"""
        if self.currentlength < self.maxlength: # Keep unfolding if not yet reach max length
            bodyrect = self.body.get_rect(topleft=(self.currentlength, 0)) # Body of the drama popup
            self.image.blit(self.body, bodyrect)
            rightcornerrect = self.rightcorner.get_rect(topleft=(self.currentlength + 30, 0)) # Right corner end
            self.image.blit(self.rightcorner, rightcornerrect)
            self.currentlength += self.body.get_width()
        elif self.currentlength >= self.maxlength and self.textblit is False: # Blit text when finish unfold and only once
            self.image.blit(self.textsurface, self.textrect)
            self.textblit = True
