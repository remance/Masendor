import pygame
import pygame.freetype


class TextDrama(pygame.sprite.Sprite):
    images = []
    screen_rect = None

    def __init__(self, screen_scale):
        self._layer = 17
        pygame.sprite.Sprite.__init__(self)
        self.body = self.images["body"]
        self.left_corner = self.images["start"]
        self.right_corner = self.images["end"]
        self.pos = (
            self.screen_rect.width / 2, self.screen_rect.height / 4)  # the center pos of the drama popup on screen
        self.font = pygame.font.SysFont("helvetica", int(70 * screen_scale[1]))
        self.queue = []  # text list to popup
        self.blit_text = False
        self.current_length = 0
        self.text_input = ""
        self.left_corner_rect = self.left_corner.get_rect(topleft=(0, 0))  # The starting point

    def process_queue(self):
        """Initiate the first text in list and remove it"""
        self.slow_drama(self.queue[0])  # Process the first item in list
        self.queue = self.queue[1:]  # Delete already processed item

    def slow_drama(self, text_input):
        """Create text and image to play animation"""
        self.blit_text = False
        self.current_length = self.left_corner.get_width()  # current unfolded length start at 20
        self.text_input = text_input
        self.text_surface = self.font.render(self.text_input, True, (0, 0, 0))
        self.image = pygame.Surface((self.text_surface.get_width() + int(self.left_corner.get_width() * 4),
                                     self.left_corner.get_height()), pygame.SRCALPHA)
        self.image.blit(self.left_corner, self.left_corner_rect)  # start animation with the left corner
        self.rect = self.image.get_rect(center=self.pos)
        self.max_length = self.image.get_width() - self.left_corner.get_width()  # max length of the body, not counting the end corner

    def play_animation(self):
        """Play unfold animation and blit drama text at the end"""
        if self.current_length < self.max_length:  # keep unfolding if not yet reach max length
            body_rect = self.body.get_rect(midleft=(self.current_length,
                                                    int(self.image.get_height() / 2)))  # body of the drama popup
            self.image.blit(self.body, body_rect)
            self.current_length += self.body.get_width()
        elif self.current_length >= self.max_length and not self.blit_text:  # blit text when finish unfold and only once
            text_rect = self.text_surface.get_rect(center=(int(self.image.get_width() / 2),
                                                           int(self.image.get_height() / 2)))
            self.image.blit(self.text_surface, text_rect)
            right_corner_rect = self.right_corner.get_rect(topright=(self.image.get_width(), 0))  # right corner end
            self.image.blit(self.right_corner, right_corner_rect)
            self.blit_text = True
