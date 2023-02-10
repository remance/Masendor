import pygame
import pygame.freetype


class TextPopup(pygame.sprite.Sprite):
    def __init__(self, screen_scale, screen_size):
        self._layer = 15
        pygame.sprite.Sprite.__init__(self)
        self.font_size = int(24 * screen_scale[1])
        self.font = pygame.font.SysFont("helvetica", self.font_size)
        self.screen_size = screen_size
        self.pos = (0, 0)
        self.text_input = ""

    def pop(self, pos, text_input):
        """Pop out text box with input text list in multiple line, one item equal to one line"""
        if self.pos != pos or self.text_input != text_input:
            self.text_input = text_input
            if type(text_input) == str:
                self.text_input = [text_input]
            self.pos = pos

            text_surface = []
            max_width = 0
            max_height = 0
            for text in self.text_input:
                surface = self.font.render(text, True, (0, 0, 0))
                text_surface.append(surface)  # text input font surface
                text_rect = surface.get_rect(topleft=(1, 1))  # text input position at (1,1) on white box image
                if text_rect.width > max_width:
                    max_width = text_rect.width
                max_height += self.font_size + int(self.font_size / 5)

            self.image = pygame.Surface((max_width + 6, max_height + 6))  # black border
            image = pygame.Surface((max_width + 2, max_height + 2))  # white Box
            image.fill((255, 255, 255))
            rect = self.image.get_rect(topleft=(2, 2))  # white box image position at (2,2) on black border image
            self.image.blit(image, rect)

            height = 1
            for surface in text_surface:
                text_rect = surface.get_rect(topleft=(4, height))
                image.blit(surface, text_rect)
                self.image.blit(surface, text_rect)  # blit text
                height += self.font_size + int(self.font_size / 10)
            if self.pos[0] + self.image.get_width() > self.screen_size[0]:  # exceed screen width
                self.rect = self.image.get_rect(topright=self.pos)
                if self.pos[1] + self.image.get_height() > self.screen_size[1]:  # also exceed height screen
                    self.rect = self.image.get_rect(bottomright=self.pos)
            elif self.pos[1] - self.image.get_height() < 0:  # exceed top screen
                self.rect = self.image.get_rect(topleft=self.pos)
            else:
                self.rect = self.image.get_rect(bottomleft=self.pos)
