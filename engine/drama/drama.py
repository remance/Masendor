import pygame

from engine.uimenu.uimenu import UIMenu
from engine.utils.text_making import text_render_with_texture


class TextDrama(UIMenu):
    images = {}

    def __init__(self, battle_camera_size):
        self._layer = 17
        UIMenu.__init__(self)
        self.body = self.images["body"]
        self.left_corner = self.images["start"]
        self.right_corner = self.images["end"]
        # drama appear at around center top pos of battle camera
        self.pos = (battle_camera_size[0] / 2, battle_camera_size[1] / 5)
        self.font = pygame.font.Font(self.ui_font["manuscript_font2"], int(60 * self.screen_scale[1]))
        self.queue = []  # text list to popup
        self.blit_text = False
        self.current_length = 0
        self.max_length = 0
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
        self.text_surface = text_render_with_texture(text_input, self.font, self.font_texture["gold"])
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
