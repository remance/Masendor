import pygame
import pygame.freetype


class TerrainPopup(pygame.sprite.Sprite):
    images = {}
    screen_rect = None

    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self)
        self.scale_adjust = (
                self.screen_rect.width * self.screen_rect.height / (
                1366 * 768))  # For adjusting the image and text according to screen size
        self.image = self.images["base"].copy()
        self.image_original = self.image.copy()

        self.font = pygame.font.SysFont("helvetica", int(24 * self.scale_adjust))
        self.height_font = pygame.font.SysFont("helvetica", int(18 * self.scale_adjust))
        self.img_pos = (
        (24 * self.scale_adjust, 34 * self.scale_adjust), (24 * self.scale_adjust, 53 * self.scale_adjust),
        # inf speed, inf atk
        (24 * self.scale_adjust, 70 * self.scale_adjust), (58 * self.scale_adjust, 34 * self.scale_adjust),
        # inf def, cav speed
        (58 * self.scale_adjust, 53 * self.scale_adjust), (58 * self.scale_adjust, 70 * self.scale_adjust),
        # cav atk, cav def
        (90 * self.scale_adjust, 34 * self.scale_adjust),
        (90 * self.scale_adjust, 53 * self.scale_adjust))  # range def, discipline
        self.mod_list = {0.5: "best", 0.3: "better", 0.1: "good", 0: "none", -0.1: "bad", -0.3: "worse", -1000: "worst"}  # Stat effect level from terrain
        self.bonus_list = {40: "best", 20: "better", 1: "good", 0: "none",  -1: "bad", -50: "worse", -2000: "worst"}  # Stat bonus level from terrain

    def pop(self, pos, feature, height):
        """pop out into screen, blit input into the image"""
        self.image = self.image_original.copy()  # reset image to default empty one
        self.pos = pos  # position to draw the image on screen

        # Terrain feature name
        text_surface = self.font.render(feature["Name"], True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(5, 5))
        self.image.blit(text_surface, text_rect)

        # Height number
        text_surface = self.height_font.render(str(height), True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(self.image.get_width() - (self.image.get_width() / 5), 5))
        self.image.blit(text_surface, text_rect)

        # Text for each stat modifier
        for index, img_pos in enumerate(self.img_pos[:6]):
            for mod in self.mod_list:  # loop to find ^v arrow icon for the modifier
                if tuple(feature.values())[
                    index + 1] >= mod:  # draw appropriate icon if modifier is higher than the number of list item
                    image_rect = self.images[self.mod_list[mod]].get_rect(center=img_pos)
                    self.image.blit(self.images[self.mod_list[mod]], image_rect)
                    break  # found arrow image to blit end loop

        # Range def modifier for both infantry and cavalry
        for mod in self.bonus_list:
            if feature["Range Defense Bonus"] >= mod:
                image_rect = self.images[self.bonus_list[mod]].get_rect(center=self.img_pos[6])
                self.image.blit(self.images[self.bonus_list[mod]], image_rect)
                break

        # Discipline modifier for both infantry and cavalry
        for mod_index, mod in enumerate(self.bonus_list):
            if feature["Discipline Bonus"] >= mod:
                image_rect = self.images[self.bonus_list[mod]].get_rect(center=self.img_pos[7])
                self.image.blit(self.images[self.bonus_list[mod]], image_rect)
                break

        self.rect = self.image.get_rect(bottomleft=self.pos)


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
