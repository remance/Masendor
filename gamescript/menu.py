import ast
import csv
import os

import pygame
import pygame.freetype
import pygame.freetype
import pyperclip
from gamescript import map, commonscript

terrain_colour = map.terrain_colour
feature_colour = map.feature_colour


class EscBox(pygame.sprite.Sprite):
    images = []
    screen_rect = None

    def __init__(self):
        self._layer = 24
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (self.screen_rect.width / 2, self.screen_rect.height / 2)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.mode = 0  # Current menu mode

    def change_mode(self, mode):
        """Change between 0 menu, 1 option, 2 encyclopedia mode"""
        self.mode = mode
        if self.mode != 2:
            self.image = self.images[mode]
            self.rect = self.image.get_rect(center=self.pos)


class EscButton(pygame.sprite.Sprite):
    def __init__(self, images, pos, text="", size=16):
        self._layer = 25
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.images = [image.copy() for image in images]
        self.text = text
        self.font = pygame.font.SysFont("timesnewroman", size)

        if text != "":  # blit menu text into button image
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(text_surface, text_rect)  # button idle image
            self.images[1].blit(text_surface, text_rect)  # button mouse over image
            self.images[2].blit(text_surface, text_rect)  # button click image

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.event = False


class SliderMenu(pygame.sprite.Sprite):
    def __init__(self, bar_image, button_image, pos, value, ui_type=0):
        self._layer = 25
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.ui_type = ui_type
        self.image = bar_image
        self.button_image_list = button_image
        self.button_image = self.button_image_list[0]
        self.slider_size = self.image.get_size()[0] - 20
        self.min_value = self.pos[0] - (self.image.get_width() / 2) + 10.5  # min value position of the scroll bar
        self.max_value = self.pos[0] + (self.image.get_width() / 2) - 10.5  # max value position
        self.value = value
        self.mouse_value = (self.slider_size * value / 100) + 10.5  # mouse position on the scroll bar convert to value
        self.image_original = self.image.copy()
        button_rect = self.button_image_list[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.button_image, button_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, mouse_pos, value_box, forced_value=False):
        """Update slider value and position"""
        if forced_value is False:
            self.mouse_value = mouse_pos[0]
            if self.mouse_value > self.max_value:
                self.mouse_value = self.max_value
            elif self.mouse_value < self.min_value:
                self.mouse_value = self.min_value
            self.value = (self.mouse_value - self.min_value) / 2
            self.mouse_value = (self.slider_size * self.value / 100) + 10.5
        else:  # for revert, cancel or esc in the option menu
            self.value = mouse_pos
            self.mouse_value = (self.slider_size * self.value / 100) + 10.5
        self.image = self.image_original.copy()
        button_rect = self.button_image_list[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.button_image, button_rect)
        value_box.update(self.value)


class InputUI(pygame.sprite.Sprite):
    def __init__(self, screen_scale, image, pos):
        self._layer = 30
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[0]),
                                                    int(image.get_height() * screen_scale[1])))

        self.image_original = self.image.copy()

        self.font = pygame.font.SysFont("timesnewroman", int(30 * screen_scale[1]))

        self.rect = self.image.get_rect(center=pos)

    def change_instruction(self, text):
        self.image = self.image_original.copy()
        self.text = text
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 4))
        self.image.blit(text_surface, text_rect)


class InputBox(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, width, text="", click_input=False):
        pygame.sprite.Sprite.__init__(self)
        self._layer = 31
        self.font = pygame.font.SysFont("timesnewroman", int(20 * screen_scale[1]))
        self.image = pygame.Surface((width - 10, int(26 * screen_scale[1])))  # already scale from input ui
        self.image.fill((255, 255, 255))

        self.image_original = self.image.copy()

        self.text = text
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.current_pos = 0

        self.active = True
        self.click_input = False
        if click_input:  # active only when click
            self.active = False
            self.click_input = click_input

        self.rect = self.image.get_rect(center=pos)

    def text_start(self, text):
        """Add starting text to input box"""
        self.current_pos = 0
        self.image = self.image_original.copy()
        self.text = text
        show_text = self.text[:self.current_pos] + "|" + self.text[self.current_pos:]
        text_surface = self.font.render(show_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)

    def user_input(self, event, keypress):
        """register user keyboard and mouse input"""
        # if self.clickinput and event.type == pygame.MOUSEBUTTONDOWN:  # only for text box that require click will activate
        #     if self.rect.collidepoint(event.pos):
        #         # Toggle the active variable.
        #         self.active = not self.active
        #     else:
        #         self.active = False
        if event.type == pygame.KEYDOWN and self.active:  # text input
            self.image = self.image_original.copy()
            if event.key == pygame.K_BACKSPACE:
                if self.current_pos > 0:
                    if self.current_pos > len(self.text):
                        self.text = self.text[:-1]
                    else:
                        self.text = self.text[:self.current_pos - 1] + self.text[self.current_pos:]
                    self.current_pos -= 1
                    if self.current_pos < 0:
                        self.current_pos = 0
            elif event.key == pygame.K_RIGHT:
                self.current_pos += 1
                if self.current_pos > len(self.text):
                    self.current_pos = len(self.text)
            elif event.key == pygame.K_LEFT:
                self.current_pos -= 1
                if self.current_pos < 0:
                    self.current_pos = 0
            elif keypress[pygame.K_LCTRL] or keypress[pygame.K_RCTRL]:
                if event.key == pygame.K_c:
                    pyperclip.copy(self.text)
                elif event.key == pygame.K_v:
                    paste_text = pyperclip.paste()
                    self.text = self.text[:self.current_pos] + paste_text + self.text[self.current_pos:]
                    self.current_pos = self.current_pos + len(paste_text)
            elif event.unicode != "":
                self.text = self.text[:self.current_pos] + event.unicode + self.text[self.current_pos:]
                self.current_pos += 1
            # Re-render the text.
            show_text = self.text[:self.current_pos] + "|" + self.text[self.current_pos:]
            text_surface = self.font.render(show_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
            self.image.blit(text_surface, text_rect)


class ProfileBox(pygame.sprite.Sprite):
    def __init__(self, screen_scale, image, pos, name):
        pygame.sprite.Sprite.__init__(self)

        self.font = pygame.font.SysFont("helvetica", int(16 * screen_scale[1]))
        self.image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[0]),
                                                    int(image.get_height() * screen_scale[1])))
        self.image_original = self.image.copy()

        text_surface = self.font.render(name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect(topright=pos)

    def change_name(self, name):
        self.image = self.image_original.copy()

        text_surface = self.font.render(name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class MenuButton(pygame.sprite.Sprite):
    def __init__(self, screen_scale, images, pos, menu_state="any", text="", size=16, layer=15):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.button_normal_image = images[0].copy()
        self.button_over_image = images[1].copy()
        self.button_click_image = images[2].copy()
        self.text = text
        self.font = pygame.font.SysFont("timesnewroman", int(size * screen_scale[1]))
        self.image_original0 = self.button_normal_image.copy()
        self.image_original1 = self.button_over_image.copy()
        self.image_original2 = self.button_click_image.copy()

        if text != "":  # draw text into the button images
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.button_normal_image.get_rect().center)
            self.button_normal_image.blit(text_surface, text_rect)
            self.button_over_image.blit(text_surface, text_rect)
            self.button_click_image.blit(text_surface, text_rect)

        self.image = self.button_normal_image
        self.rect = self.button_normal_image.get_rect(center=self.pos)
        self.event = False
        self.menu_state = menu_state

    def update(self, mouse_pos, mouse_up, mouse_down, menu_state):
        if self.menu_state == menu_state or self.menu_state == "any":
            self.mouse_over = False
            self.image = self.button_normal_image
            if self.rect.collidepoint(mouse_pos):
                self.mouse_over = True
                self.image = self.button_over_image
                if mouse_up:
                    self.event = True
                    self.image = self.button_click_image

    def changestate(self, text):
        if text != "":
            img0 = self.image_original0.copy()
            img1 = self.image_original1.copy()
            img2 = self.image_original2.copy()
            self.images = [img0, img1, img2]
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(text_surface, text_rect)
            self.images[1].blit(text_surface, text_rect)
            self.images[2].blit(text_surface, text_rect)
        self.rect = self.images[0].get_rect(center=self.pos)
        self.event = False


class MenuIcon(pygame.sprite.Sprite):
    def __init__(self, images, pos, text="", image_resize=0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.images = images
        self.image = self.images[0]
        if image_resize != 0:
            self.image = pygame.transform.scale(self.image, (image_resize, image_resize))
        self.text = text
        self.font = pygame.font.SysFont("timesnewroman", 16)
        if text != "":
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.image.get_rect().center)
            self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(center=self.pos)
        self.event = False


class ValueBox(pygame.sprite.Sprite):
    def __init__(self, text_image, pos, value, text_size=16):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("timesnewroman", text_size)
        self.pos = pos
        self.image = pygame.transform.scale(text_image,
                                            (int(text_image.get_size()[0] / 2), int(text_image.get_size()[1] / 2)))
        self.image_original = self.image.copy()
        self.value = value
        text_surface = self.font.render(str(self.value), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, value):
        self.value = value
        self.image = self.image_original.copy()
        text_surface = self.font.render(str(self.value), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class MapTitle(pygame.sprite.Sprite):
    def __init__(self, screen_scale, name, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.font = pygame.font.SysFont("oldenglishtext", int(70 * screen_scale[1]))
        text_surface = self.font.render(str(name), True, (0, 0, 0))

        self.image = pygame.Surface((int(text_surface.get_width() + (20 * screen_scale[0])),
                                     int(text_surface.get_height() + (20 * screen_scale[1]))))
        self.image.fill((0, 0, 0))

        white_body = pygame.Surface((text_surface.get_width(), text_surface.get_height()))
        white_body.fill((239, 228, 176))
        white_rect = white_body.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(white_body, white_rect)

        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(midtop=pos)


class MapDescription(pygame.sprite.Sprite):
    image = None

    def __init__(self, screen_scale, pos, text):
        pygame.sprite.Sprite.__init__(self, self.containers)
        make_long_text = commonscript.make_long_text

        self.font = pygame.font.SysFont("timesnewroman", int(16 * screen_scale[1]))
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * screen_scale[0]),
                                                         int(self.image.get_height() * screen_scale[1])))

        self.image_original = self.image.copy()
        self.image = self.image_original.copy()  # reset self.image to new one from the loaded image

        make_long_text(self.image, text, (int(20 * screen_scale[0]), int(20 * screen_scale[1])), self.font)

        self.rect = self.image.get_rect(center=pos)


class SourceDescription(pygame.sprite.Sprite):
    image = None

    def __init__(self, screen_scale, pos, text):
        pygame.sprite.Sprite.__init__(self, self.containers)
        make_long_text = commonscript.make_long_text

        self.font = pygame.font.SysFont("timesnewroman", int(16 * screen_scale[1]))
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * screen_scale[0]),
                                                         int(self.image.get_height() * screen_scale[1])))

        self.image_original = self.image.copy()
        self.image = self.image_original.copy()  # reset self.image to new one from the loaded image

        make_long_text(self.image, text, (int(15 * screen_scale[0]), int(20 * screen_scale[1])), self.font)

        self.rect = self.image.get_rect(center=pos)


class TeamCoa(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, image, team, name):
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.selected_image = pygame.Surface((int(200 * screen_scale[0]), int(200 * screen_scale[1])))
        self.not_selected_image = self.selected_image.copy()
        self.not_selected_image.fill((0, 0, 0))  # black border when not selected
        self.selected_image.fill((230, 200, 15))  # gold border when selected

        white_body = pygame.Surface((int(196 * screen_scale[0]), int(196 * screen_scale[1])))
        white_body.fill((255, 255, 255))
        white_rect = white_body.get_rect(topleft=(int(2 * screen_scale[0]), int(2 * screen_scale[1])))
        self.not_selected_image.blit(white_body, white_rect)
        self.selected_image.blit(white_body, white_rect)

        # v Coat of arm image to image
        coa_image = pygame.transform.scale(image, (int(100 * screen_scale[0]), int(100 * screen_scale[1])))
        coa_rect = coa_image.get_rect(center=(int(100 * screen_scale[0]), int(70 * screen_scale[1])))
        self.not_selected_image.blit(coa_image, coa_rect)
        self.selected_image.blit(coa_image, coa_rect)
        # ^ End Coat of arm

        # v Faction name to image
        self.name = name
        self.font = pygame.font.SysFont("oldenglishtext", int(32 * screen_scale[1]))
        text_surface = self.font.render(str(self.name), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(int(100 * screen_scale[0]), int(150 * screen_scale[1])))
        self.not_selected_image.blit(text_surface, text_rect)
        self.selected_image.blit(text_surface, text_rect)
        # ^ End faction name

        self.image = self.not_selected_image
        self.rect = self.image.get_rect(center=pos)
        self.team = team
        self.selected = False

    def change_select(self, selected):
        self.selected = selected
        if self.selected:
            self.image = self.selected_image
        else:
            self.image = self.not_selected_image


class ArmyStat(pygame.sprite.Sprite):
    image = None

    def __init__(self, screen_scale, pos):
        self._layer = 1

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.leader_font = pygame.font.SysFont("helvetica", int(screen_scale[1] * 30))
        self.font = pygame.font.SysFont("helvetica", int(screen_scale[1] * 20))

        self.image_original = self.image.copy()
        self.image = self.image_original.copy()

        self.type_number_pos = ((self.image.get_width() / 5, self.image.get_height() / 3),  # infantry melee
                                (self.image.get_width() / 5, self.image.get_height() / 1.8),  # infantry range
                                (self.image.get_width() / 1.6, self.image.get_height() / 3),  # cav melee
                                (self.image.get_width() / 1.6, self.image.get_height() / 1.8),  # cav range
                                (self.image.get_width() / 5, self.image.get_height() / 1.4))  # total subunit

        self.rect = self.image.get_rect(center=pos)

    def add_stat(self, troop_number, leader):
        """troop_number need to be in list format as follows:[total,melee infantry, range infantry, cavalry, range cavalry]"""
        self.image = self.image_original.copy()

        text_surface = self.font.render(str(leader), True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 7, self.image.get_height() / 10))
        self.image.blit(text_surface, text_rect)

        for index, text in enumerate(troop_number):
            text_surface = self.font.render("{:,}".format(text), True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=self.type_number_pos[index])
            self.image.blit(text_surface, text_rect)


class ListBox(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, image, layer=14):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[0]),
                                                    int(image.get_height() * screen_scale[1])))
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

        image_height = int(28 * screen_scale[1])
        self.max_show = int(
            self.image.get_height() / (image_height + (6 * screen_scale[1])))  # max number of map on list can be shown


class NameList(pygame.sprite.Sprite):
    def __init__(self, screen_scale, box, pos, name, text_size=16, layer=15):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(screen_scale[1] * text_size))
        self.name = str(name)

        self.image = pygame.Surface(
            (box.image.get_width() - int(15 * screen_scale[0]), int(25 * screen_scale[1])))  # black corner
        self.image.fill((0, 0, 0))
        self.selected_image = self.image.copy()
        self.selected = False

        # v White body square
        small_image = pygame.Surface((box.image.get_width() - int(17 * screen_scale[0]), int(23 * screen_scale[1])))
        small_image.fill((255, 255, 255))
        small_rect = small_image.get_rect(topleft=(int(1 * screen_scale[0]), int(1 * screen_scale[1])))
        self.image.blit(small_image, small_rect)
        small_image.fill((255, 255, 128))
        self.selected_image.blit(small_image, small_rect)
        # ^ End white body

        # v name text
        text_surface = self.font.render(self.name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(int(3 * screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.selected_image.blit(text_surface, text_rect)
        # ^ End name
        self.not_selected_image = self.image.copy()

        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

    def select(self):
        if self.selected:
            self.selected = False
            self.image = self.not_selected_image.copy()
        else:
            self.selected = True
            self.image = self.selected_image.copy()

class TickBox(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, image, tick_image, option):
        """option is in str text for identifying what kind of tick_box it is"""
        self._layer = 14
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.option = option

        self.not_tick_image = image
        self.tick_image = tick_image
        self.tick = False

        self.not_tick_image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[0]),
                                                             int(image.get_height() * screen_scale[1])))
        self.tick_image = pygame.transform.scale(tick_image, (int(tick_image.get_width() * screen_scale[0]),
                                                              int(tick_image.get_height() * screen_scale[1])))

        self.image = self.not_tick_image

        self.rect = self.image.get_rect(topright=pos)

    def change_tick(self, tick):
        self.tick = tick
        if self.tick:
            self.image = self.tick_image
        else:
            self.image = self.not_tick_image


class MapOptionBox(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, image, mode):
        self.font = pygame.font.SysFont("helvetica", int(16 * screen_scale[1]))

        self._layer = 13
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[0]),
                                                    int(image.get_height() * screen_scale[1])))

        # v enactment option text
        text_surface = self.font.render("Enactment Mode", True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 4))
        self.image.blit(text_surface, text_rect)
        # ^ end enactment

        if mode == 0:  # preset map option
            pass
        elif mode == 1:  # custom map option
            # v enactment option text
            text_surface = self.font.render("No Duplicated Leader", True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 3))
            self.image.blit(text_surface, text_rect)
            # ^ end enactment

            # v enactment option text
            text_surface = self.font.render("Restrict Faction Troop Only", True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 2))
            self.image.blit(text_surface, text_rect)
            # ^ end enactment

        self.rect = self.image.get_rect(topright=pos)


class SourceListBox(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, image):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[0]),
                                                    int(image.get_height() * screen_scale[1])))
        self.rect = self.image.get_rect(topleft=pos)
        self.max_show = 5  # max number of map on list can be shown at once


class SourceName(pygame.sprite.Sprite):
    def __init__(self, screen_scale, box, pos, name, text_size=16, layer=14):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(text_size * screen_scale[1]))
        self.image = pygame.Surface((box.image.get_width(), int(25 * screen_scale[1])))  # black corner
        self.image.fill((0, 0, 0))

        # v White body square
        small_image = pygame.Surface((box.image.get_width() - int(2 * screen_scale[0]), int(23 * screen_scale[1])))
        small_image.fill((255, 255, 255))
        small_rect = small_image.get_rect(topleft=(int(1 * screen_scale[0]), int(1 * screen_scale[1])))
        self.image.blit(small_image, small_rect)
        # ^ End white body

        # v Source name text
        text_surface = self.font.render(str(name), True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(int(3 * screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        # ^ End source text

        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


class MapShow(pygame.sprite.Sprite):
    def __init__(self, main_dir, screen_scale, pos, base_map, feature_map):
        self.main_dir = main_dir
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.screen_scale = screen_scale
        self.pos = pos
        self.prev_image = pygame.Surface((310, 310))
        self.prev_image.fill((0, 0, 0))  # draw black colour for black corner
        # pygame.draw.rect(self.image, self.colour, (2, 2, self.widthbox - 3, self.heightbox - 3)) # draw block colour

        self.team2_dot = pygame.Surface((8, 8))  # dot for team2 subunit
        self.team2_dot.fill((0, 0, 0))  # black corner
        self.team1_dot = pygame.Surface((8, 8))  # dot for team1 subunit
        self.team1_dot.fill((0, 0, 0))  # black corner
        team2 = pygame.Surface((6, 6))  # size 6x6
        team2.fill((255, 0, 0))  # red rect
        team1 = pygame.Surface((6, 6))
        team1.fill((0, 0, 255))  # blue rect
        rect = self.team2_dot.get_rect(topleft=(1, 1))
        self.team2_dot.blit(team2, rect)
        self.team1_dot.blit(team1, rect)

        self.new_colour_list = {}
        with open(os.path.join(self.main_dir, "data", "map", "colourchange.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    elif "," in i:
                        row[n] = ast.literal_eval(i)
                self.new_colour_list[row[0]] = row[1:]

        self.change_map(base_map, feature_map)
        self.image = pygame.transform.scale(self.prev_image, (int(self.prev_image.get_width() * self.screen_scale[0]),
                                                              int(self.prev_image.get_height() * self.screen_scale[1])))
        self.rect = self.image.get_rect(center=self.pos)

    def change_map(self, base_map, feature_map):
        new_base_map = pygame.transform.scale(base_map, (300, 300))
        new_feature_map = pygame.transform.scale(feature_map, (300, 300))

        map_image = pygame.Surface((300, 300))
        for row_pos in range(0, 300):  # recolour the map
            for col_pos in range(0, 300):
                terrain = new_base_map.get_at((row_pos, col_pos))  # get colour at pos to obtain the terrain type
                terrain_index = terrain_colour.index(terrain)

                feature = new_feature_map.get_at((row_pos, col_pos))  # get colour at pos to obtain the terrain type
                feature_index = None
                if feature in feature_colour:
                    feature_index = feature_colour.index(feature)
                    feature_index = feature_index + (terrain_index * 12)
                new_colour = self.new_colour_list[feature_index][1]
                rect = pygame.Rect(row_pos, col_pos, 1, 1)
                map_image.fill(new_colour, rect)

        image_rect = map_image.get_rect(topleft=(5, 5))
        self.prev_image.blit(map_image, image_rect)
        self.image_original = self.prev_image.copy()

    def change_mode(self, mode, team1_pos_list=None, team2_pos_list=None):
        """map mode: 0 = map without army dot, 1 = with army dot"""
        self.prev_image = self.image_original.copy()
        if mode == 1:
            for team1 in team1_pos_list.values():
                scaled_pos = pygame.Vector2(team1) * 0.3
                rect = self.team1_dot.get_rect(center=scaled_pos)
                self.prev_image.blit(self.team1_dot, rect)
            for team2 in team2_pos_list.values():
                scaled_pos = pygame.Vector2(team2) * 0.3
                rect = self.team2_dot.get_rect(center=scaled_pos)
                self.prev_image.blit(self.team2_dot, rect)

        self.image = pygame.transform.scale(self.prev_image, (int(self.prev_image.get_width() * self.screen_scale[0]),
                                                              int(self.prev_image.get_height() * self.screen_scale[1])))
        self.rect = self.image.get_rect(center=self.pos)