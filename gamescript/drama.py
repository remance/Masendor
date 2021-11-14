import pygame
import pygame.freetype


class TextDrama(pygame.sprite.Sprite):
    images = []
    SCREENRECT = None

    def __init__(self):
        self._layer = 17
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.body = self.images[0]
        self.left_corner = self.images[1]
        self.right_corner = self.images[2]
        self.pos = (self.SCREENRECT.width / 2, self.SCREENRECT.height / 4)  # The center pos of the drama popup on screen
        self.font = pygame.font.SysFont("helvetica", 70)
        self.queue = []  # Text list to popup

    def processqueue(self):
        """Initiate the first text in list and remove it"""
        self.slowdrama(self.queue[0])  # Process the first item in list
        self.queue = self.queue[1:]  # Delete already processed item

    def slowdrama(self, textinput):
        """Create text and image to play animation"""
        self.textblit = False
        self.current_length = 20  # Current unfolded length start at 20
        self.textinput = textinput
        self.leftcorner_rect = self.left_corner.get_rect(topleft=(0, 0))  # The starting point
        self.text_surface = self.font.render(self.textinput, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(topleft=(30, 1))
        self.image = pygame.Surface((self.text_rect.width + 70, self.text_rect.height), pygame.SRCALPHA)
        self.image.blit(self.left_corner, self.leftcorner_rect)  # start animation with the left corner
        self.rect = self.image.get_rect(center=self.pos)
        self.max_length = self.image.get_width() - 20  # Max length of the body, not counting the end corner

    def playanimation(self):
        """Play unfold animation and blit drama text at the end"""
        if self.current_length < self.max_length:  # Keep unfolding if not yet reach max length
            bodyrect = self.body.get_rect(topleft=(self.current_length, 0))  # Body of the drama popup
            self.image.blit(self.body, bodyrect)
            rightcorner_rect = self.right_corner.get_rect(topleft=(self.current_length + 30, 0))  # Right corner end
            self.image.blit(self.right_corner, rightcorner_rect)
            self.current_length += self.body.get_width()
        elif self.current_length >= self.max_length and self.textblit is False:  # Blit text when finish unfold and only once
            self.image.blit(self.text_surface, self.text_rect)
            self.textblit = True
