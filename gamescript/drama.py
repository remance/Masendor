import pygame
import pygame.freetype


class TextDrama(pygame.sprite.Sprite):
    images = []
    screen_rect = None

    def __init__(self, screen_scale):
        self._layer = 17
        pygame.sprite.Sprite.__init__(self)
        self.body = self.images["body.png"]
        self.left_corner = self.images["start.png"]
        self.right_corner = self.images["end.png"]
        self.pos = (self.screen_rect.width / 2, self.screen_rect.height / 4)  # The center pos of the drama popup on screen
        self.font = pygame.font.SysFont("helvetica", int(70 * screen_scale[1]))
        self.queue = []  # Text list to popup
        self.blit_text = False
        self.current_length = 20  # Current unfolded length start at 20
        self.text_input = ""
        self.left_corner_rect = self.left_corner.get_rect(topleft=(0, 0))  # The starting point

    def process_queue(self):
        """Initiate the first text in list and remove it"""
        self.slow_drama(self.queue[0])  # Process the first item in list
        self.queue = self.queue[1:]  # Delete already processed item

    def slow_drama(self, text_input):
        """Create text and image to play animation"""
        self.blit_text = False
        self.current_length = 20  # Current unfolded length start at 20
        self.text_input = text_input
        self.text_surface = self.font.render(self.text_input, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(topleft=(30, 1))
        self.image = pygame.Surface((self.text_rect.width + 70, self.text_rect.height), pygame.SRCALPHA)
        self.image.blit(self.left_corner, self.left_corner_rect)  # start animation with the left corner
        self.rect = self.image.get_rect(center=self.pos)
        self.max_length = self.image.get_width() - 20  # Max length of the body, not counting the end corner

    def play_animation(self):
        """Play unfold animation and blit drama text at the end"""
        if self.current_length < self.max_length:  # Keep unfolding if not yet reach max length
            body_rect = self.body.get_rect(topleft=(self.current_length, 0))  # Body of the drama popup
            self.image.blit(self.body, body_rect)
            right_corner_rect = self.right_corner.get_rect(topleft=(self.current_length + 30, 0))  # Right corner end
            self.image.blit(self.right_corner, right_corner_rect)
            self.current_length += self.body.get_width()
        elif self.current_length >= self.max_length and self.blit_text is False:  # Blit text when finish unfold and only once
            self.image.blit(self.text_surface, self.text_rect)
            self.blit_text = True
