import networkx as nx

import pyperclip
import types
from functools import lru_cache

import pygame
from pygame import Surface, SRCALPHA, Rect, Color, Vector2, draw, mouse
from pygame.sprite import Sprite
from pygame.font import Font
from pygame.transform import smoothscale, scale

from engine.battlemap.battlemap import BattleMap

from engine.utility import keyboard_mouse_press_check, text_render, make_long_text

@lru_cache(maxsize=2**8)
def draw_text(text, font, color):
    # NOTE: this can be very slow. Imagine you have a very long text it has to step down each
    #       character till it find the a character length that works.
    #       if this method's performance becomes a big issue try make a better estimate on the length
    #       and start from there and move up or down in length.
    #
    #       we have cache in place so hopefully it will be enough to save performance.

    # TODO: add ellipsis_length to argument

    ellipsis_length = 220

    if ellipsis_length is not None:
        for i in range(len(text)):
            text_surface = font.render(text[:len(text)-i]+('...' if i > 0 else ''), True, color)
            if text_surface.get_size()[0] > ellipsis_length: continue
            return text_surface
        raise Exception()
    else:
        return font.render(text, True, color)


def make_image_by_frame(frame: Surface, final_size):
    """
        Makes a bigger frame based image out of a frame surface.

        A frame surface is the smallest possible surface of a frame.
        It contain all corners and sides and a pixel in the center.
        The pixel in will be the color of the content of the image.

        It is required that every corner has the same size. If not
        the final image will not look correct.

        And each side must have the same size.
    """

    fs = final_size

    assert frame.get_size()[0] == frame.get_size()[1]
    assert frame.get_size()[0] % 2 == 1

    css = corner_side_size = (frame.get_size()[0] - 1) // 2

    image = Surface(final_size, SRCALPHA)

    # offsets
    # ---
    # if the corners has alpha they can appear to make the final image uneven.
    # that is why we need to adjust the thresholds with some offsets.
    # these offsets are being calculated by check the margins on each side.

    # NOTE/TODO: this is only being implemented on left/right because that is
    #            where we had issues on some image. when we have issues on top/bottom
    #            let us then implement it on it then.
    offsets = o = [0] * 4  # left, up, right, down

    # left margin
    lm = frame.get_size()[0]
    for y in range(frame.get_size()[1]):
        for x in range(lm):
            if frame.get_at((x, y)).a != 0:
                lm = x
                break
    o[0] = -lm

    # right margin
    rm = frame.get_size()[0]
    for y in range(frame.get_size()[1]):
        for x in range(rm):
            if frame.get_at((frame.get_size()[0] - x - 1, y)).a != 0:
                rm = x
                break
    o[2] = rm
    # ---

    # background color
    bc = background_color = frame.get_at((css, css))
    draw.rect(image, bc, (css + o[0], css, fs[0] - css * 2 + o[2] - o[0], fs[1] - css * 2))

    # corners
    image.blit(frame, (0 + o[0], 0), (0, 0, css, css))
    image.blit(frame, (0 + o[0], fs[1] - css), (0, css + 1, css, css * 2 + 1))
    image.blit(frame, (fs[0] - css + o[2], 0), (css + 1, 0, css * 2 + 1, css))
    image.blit(frame, (fs[0] - css + o[2], fs[1] - css), (css + 1, css + 1, css * 2 + 1, css * 2 + 1))

    # sides
    for x in range(css + o[0], fs[0] - css + o[2]):
        image.blit(frame, (x, 0), (css, 0, 1, css))
        image.blit(frame, (x, fs[1] - css), (css, css + 1, 1, css * 2 + 1))
    for y in range(css, fs[1] - css):
        image.blit(frame, (0 + o[0], y), (0, css, css, 1))
        image.blit(frame, (fs[0] - css + o[2], y), (css + 1, css, css * 2 + 1, 1))

    return image


class UIMenu(Sprite):
    containers = None

    def __init__(self, player_interact=True, has_containers=False):
        """
        Parent class for all menu user interface
        """
        from engine.game.game import Game
        self.game = Game.game
        self.screen_scale = Game.screen_scale
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.font_dir = Game.font_dir
        self.ui_font = Game.ui_font
        self.screen_rect = Game.screen_rect
        self.screen_size = Game.screen_size
        self.localisation = Game.localisation
        self.cursor = Game.cursor
        self.updater = Game.main_ui_updater
        self.player_interact = player_interact
        if has_containers:
            Sprite.__init__(self, self.containers)
        else:
            Sprite.__init__(self)
        self.event = False
        self.event_press = False
        self.event_hold = False
        self.mouse_over = False

    def update(self):
        self.event = False
        self.event_press = False
        self.event_hold = False  # some UI differentiates between press release or holding, if not just use event
        self.mouse_over = False
        if self.rect.collidepoint(self.cursor.pos):
            self.mouse_over = True
            if self.player_interact:
                if self.cursor.is_select_just_up or self.cursor.is_select_down:
                    self.event = True
                    if self.cursor.is_select_just_up:
                        self.event_press = True
                        self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
                    elif self.cursor.is_select_down:
                        self.event_hold = True
                        self.cursor.is_select_just_down = False  # reset select button to prevent overlap interaction


class MenuCursor(UIMenu):
    def __init__(self, images):
        """Game menu cursor"""
        self._layer = 1000000  # as high as possible, always blit last
        UIMenu.__init__(self, player_interact=False, has_containers=True)
        self.images = images
        self.image = images["normal"]
        self.pos = (0, 0)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.is_select_just_down = False
        self.is_select_down = False
        self.is_select_just_up = False
        self.is_alt_select_just_down = False
        self.is_alt_select_down = False
        self.is_alt_select_just_up = False
        self.scroll_up = False
        self.scroll_down = False

    def update(self):
        """Update cursor position based on mouse position and mouse button click"""
        self.pos = mouse.get_pos()
        self.rect.topleft = self.pos
        self.is_select_just_down, self.is_select_down, self.is_select_just_up = keyboard_mouse_press_check(
            mouse, 0, self.is_select_just_down, self.is_select_down, self.is_select_just_up)

        # Alternative select press button, like mouse right
        self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up = keyboard_mouse_press_check(
            mouse, 2, self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up)

    def change_image(self, image_name):
        """Change cursor image to whatever input name"""
        self.image = self.images[image_name]
        self.rect = self.image.get_rect(topleft=self.pos)


class SliderMenu(UIMenu):
    def __init__(self, bar_images, button_images, pos, value):
        """
        Slider UI that let player click or drag the setting point in the bar
        :param bar_images: List of box image and slider box
        :param button_images: List of button or ball clicked/non-clicked image
        :param pos: Position of the ui sprite
        :param value: Value of the setting
        """
        self._layer = 25
        UIMenu.__init__(self, has_containers=True)
        self.pos = pos
        self.image = bar_images[0].copy()
        self.slider_size = bar_images[1].get_width()
        self.difference = (self.image.get_width() - self.slider_size) / 2
        self.value_scale = self.slider_size / 100
        rect = bar_images[1].get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(bar_images[1], rect)
        self.button_image_list = button_images
        self.button_image = self.button_image_list[0]
        self.min_value = self.pos[0] - (self.slider_size / self.value_scale)  # min value position of the scroll bar
        self.max_value = self.pos[0] + (self.slider_size / self.value_scale)  # max value position
        self.value = value
        self.mouse_value = (self.slider_size * value / 100) + self.difference  # convert mouse pos on scroll to value
        self.base_image = self.image.copy()
        button_rect = self.button_image_list[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.button_image, button_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def player_input(self, value_box, forced_value=False):
        """
        Update slider value and position
        :param value_box: UI box that show number value
        :param forced_value: forced
        :return:
        """
        if not forced_value:
            self.mouse_value = self.cursor.pos[0]
            if self.mouse_value > self.max_value:
                self.mouse_value = self.max_value
            elif self.mouse_value < self.min_value:
                self.mouse_value = self.min_value
            self.value = (self.mouse_value - self.min_value) / 2
        else:  # for revert, cancel or esc in the option menu
            self.value = self.cursor.pos
        self.mouse_value = (self.slider_size * self.value / 100) + self.difference
        self.image = self.base_image.copy()
        button_rect = self.button_image_list[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.button_image, button_rect)
        value_box.change_value(self.value)


class InputUI(UIMenu):
    def __init__(self, image, pos):
        self._layer = 30
        UIMenu.__init__(self, player_interact=False)

        self.pos = pos
        self.image = image

        self.base_image = self.image.copy()

        self.font = Font(self.ui_font["main_button"], int(48 * self.screen_scale[1]))

        self.rect = self.image.get_rect(center=self.pos)

    def change_instruction(self, text):
        self.image = self.base_image.copy()
        self.text = text
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 4))
        self.image.blit(text_surface, text_rect)


class InputBox(UIMenu):
    def __init__(self, pos, width, text="", click_input=False):
        UIMenu.__init__(self, player_interact=False)
        self._layer = 31
        self.font = Font(self.ui_font["main_button"], int(30 * self.screen_scale[1]))
        self.pos = pos
        self.image = Surface((width - 10, int(34 * self.screen_scale[1])))
        self.max_text = int((self.image.get_width() / int(30 * self.screen_scale[1])) * 2.2)
        self.image.fill((255, 255, 255))

        self.base_image = self.image.copy()

        self.text = text
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.current_pos = 0

        self.hold_key = 0
        self.hold_key_unicode = ""

        self.active = True
        self.click_input = False
        if click_input:  # active only when click
            self.active = False
            self.click_input = click_input

        self.rect = self.image.get_rect(center=self.pos)

    def text_start(self, text):
        """Add starting text to input box"""
        self.image = self.base_image.copy()
        self.text = text
        self.current_pos = len(self.text)  # start input at the end
        show_text = self.text[:self.current_pos] + "|" + self.text[self.current_pos:]
        text_surface = self.font.render(show_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)

    def player_input(self, input_event, key_press):
        """register user keyboard and mouse input"""
        if self.active:  # text input
            self.image = self.base_image.copy()
            event = input_event
            event_key = None
            event_unicode = ""
            if event:
                event_key = input_event.key
                event_unicode = event.unicode
                self.hold_key = event_key  # save last holding press key
                self.hold_key_unicode = event_unicode

            if event_key == pygame.K_BACKSPACE or self.hold_key == pygame.K_BACKSPACE:
                if self.current_pos > 0:
                    if self.current_pos > len(self.text):
                        self.text = self.text[:-1]
                    else:
                        self.text = self.text[:self.current_pos - 1] + self.text[self.current_pos:]
                    self.current_pos -= 1
                    if self.current_pos < 0:
                        self.current_pos = 0
            elif event_key == pygame.K_RETURN or event_key == pygame.K_KP_ENTER:  # use external code instead for enter press
                pass
            elif event_key == pygame.K_RIGHT or self.hold_key == pygame.K_RIGHT:
                self.current_pos += 1
                if self.current_pos > len(self.text):
                    self.current_pos = len(self.text)
            elif event_key == pygame.K_LEFT or self.hold_key == pygame.K_LEFT:
                self.current_pos -= 1
                if self.current_pos < 0:
                    self.current_pos = 0
            elif key_press[pygame.K_LCTRL] or key_press[
                pygame.K_RCTRL]:  # use keypress for ctrl as it has no effect on its own
                if event_key == pygame.K_c:
                    pyperclip.copy(self.text)
                elif event_key == pygame.K_v:
                    paste_text = pyperclip.paste()
                    self.text = self.text[:self.current_pos] + paste_text + self.text[self.current_pos:]
                    self.current_pos = self.current_pos + len(paste_text)
            elif event_unicode != "" or self.hold_key_unicode != "":
                if event_unicode != "":  # input event_unicode first before holding one
                    input_unicode = event_unicode
                elif self.hold_key_unicode != "":
                    input_unicode = self.hold_key_unicode
                self.text = self.text[:self.current_pos] + input_unicode + self.text[self.current_pos:]
                self.current_pos += 1
            # Re-render the text
            show_text = self.text[:self.current_pos] + "|" + self.text[self.current_pos:]
            if self.current_pos > self.max_text:
                show_text = show_text[abs(self.current_pos - self.max_text):]
            text_surface = self.font.render(show_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
            self.image.blit(text_surface, text_rect)


class TextBox(UIMenu):
    def __init__(self, image, pos, text):
        self._layer = 13
        UIMenu.__init__(self)

        self.font = Font(self.ui_font["main_button"], int(36 * self.screen_scale[1]))
        self.image = image

        self.base_image = self.image.copy()

        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect(topright=pos)

    def change_text(self, text):
        self.image = self.base_image.copy()

        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class MenuImageButton(UIMenu):
    def __init__(self, pos, images, layer=1):
        self._layer = layer
        UIMenu.__init__(self)
        self.pos = pos
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)


class MenuButton(UIMenu):
    def __init__(self, images, pos, key_name="", font_size=28, layer=1):
        self._layer = layer
        UIMenu.__init__(self)
        self.pos = pos
        self.button_normal_image = images[0].copy()
        self.button_over_image = images[1].copy()
        self.button_click_image = images[2].copy()

        self.font = Font(self.ui_font["main_button"], int(font_size * self.screen_scale[1]))
        self.base_image0 = self.button_normal_image.copy()
        self.base_image1 = self.button_over_image.copy()
        self.base_image2 = self.button_click_image.copy()

        self.text = ""
        if key_name != "":  # draw text into the button images
            self.text = self.localisation.grab_text(key=("ui", key_name,))
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.button_normal_image.get_rect().center)
            self.button_normal_image.blit(text_surface, text_rect)
            self.button_over_image.blit(text_surface, text_rect)
            self.button_click_image.blit(text_surface, text_rect)

        self.image = self.button_normal_image
        self.rect = self.button_normal_image.get_rect(center=self.pos)

    def update(self):
        self.event = False
        self.event_press = False
        self.mouse_over = False
        self.image = self.button_normal_image
        if self.rect.collidepoint(self.cursor.pos):
            self.mouse_over = True
            self.image = self.button_over_image
            if self.cursor.is_select_just_up:
                self.event = True
                self.event_press = True
                self.image = self.button_click_image
                self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
            elif self.cursor.is_select_down:
                self.event_hold = True
                self.cursor.is_select_just_down = False  # reset select button to prevent overlap interaction

    def change_state(self, key_name):
        if key_name != "":
            self.text = self.localisation.grab_text(key=("ui", key_name))
            self.button_normal_image = self.base_image0.copy()
            self.button_over_image = self.base_image1.copy()
            self.button_click_image = self.base_image2.copy()
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.button_normal_image.get_rect().center)
            self.button_normal_image.blit(text_surface, text_rect)
            self.button_over_image.blit(text_surface, text_rect)
            self.button_click_image.blit(text_surface, text_rect)
        self.rect = self.button_normal_image.get_rect(center=self.pos)
        self.event = False


class Container:

    def get_rect(self):
        raise NotImplementedError()


class Containable:

    def get_relative_position_inside_container(self):
        raise NotImplementedError()

    def get_relative_size_inside_container(self):
        return None

    def get_size(self):
        raise NotImplementedError()

    def converse_pos_origin(self, pos, container):
        """Convert pos to origin value (-1, 1 scale)"""
        origin = [pos[0], pos[1]]
        for index, this_pos in enumerate(origin):
            container_size = container.get_size()[index]
            this_pos = container_size - this_pos  # some magic to make it appear not too far from pos
            if this_pos > container.get_size()[index] / 2:  # + scale
                origin[index] = round(this_pos / container_size, 2)
            elif this_pos < container.get_size()[index] / 2:  # - scale
                if this_pos == 0:  # 0 value mean at most left/top
                    origin[index] = -1
                else:
                    origin[index] = -1 + round(this_pos / container_size, 2)
            else:  # center
                origin[index] = 0
        return origin

    def change_origin_with_pos(self, pos):
        self.origin = self.converse_pos_origin(pos, self.parent)
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)

    def get_adjusted_rect_to_be_inside_container(self, container):
        rpic = self.get_relative_position_inside_container()
        rsic = self.get_relative_size_inside_container()
        pivot = rpic["pivot"]
        origin = rpic["origin"]

        if rsic is None:
            return Rect(
                *[container.get_rect()[i] - (self.get_size()[i] * (origin[i] + 1)) // 2 + (pivot[i] + 1) *
                  container.get_rect()[i + 2] // 2 for i in
                  range(2)], *self.get_size())
        else:
            size = [container.get_size()[i] * rsic[i] for i in range(2)]
            return Rect(
                *[container.get_rect()[i] - (size[i] * (origin[i] + 1)) // 2 + (pivot[i] + 1) * container.get_rect()[
                    i + 2] // 2 for i in range(2)],
                *size)


class BrownMenuButton(UIMenu, Containable):  # NOTE: the button is not brown anymore, it is white/yellow

    @classmethod
    @lru_cache
    def make_buttons(cls, size, text, font):
        from engine.game.game import Game
        from engine.utility import load_image
        game = Game.game

        frame = load_image(game.module_dir, (1, 1), "new_button.png", ("ui", "mainmenu_ui"))

        normal_button = make_image_by_frame(frame, size)
        text_surface = font.render(text, True, (0,) * 3)
        text_rect = text_surface.get_rect(center=normal_button.get_rect().center)
        normal_button.blit(text_surface, text_rect)

        hover_button = normal_button.copy()
        draw.rect(hover_button, "#DD0000", hover_button.get_rect(), 1)

        return (normal_button, hover_button)

    def get_relative_size_inside_container(self):
        return (.5, .1)  # TODO: base this on a variable

    def __init__(self, pos, key_name="", width=200, parent=None):
        UIMenu.__init__(self)
        self.pos = pos
        self.parent = parent
        self.key_name = key_name
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.mouse_over = False
        self.event = False
        self.font = Font(self.ui_font["main_button"], 17)
        self.text = self.localisation.grab_text(key=("ui", self.key_name))
        self.refresh()

    def refresh(self):
        images = self.make_buttons(size=tuple(self.rect[2:]), text=self.text, font=self.font)

        self.image = images[0]
        if self.mouse_over:
            self.image = images[1]

    def get_relative_position_inside_container(self):
        return {
            "origin": (0, 0),
            "pivot": self.pos,
        }

    def update(self):

        mouse_pos = self.cursor.pos
        sju = self.cursor.is_select_just_up
        self.event = False

        self.mouse_over = False
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if sju:
                self.event = True
                self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction

        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.refresh()

    def get_size(self):
        return self.image.get_size()

    def change_state(self, text):
        pass


class OptionMenuText(UIMenu):
    def __init__(self, pos, text, text_size):
        UIMenu.__init__(self, player_interact=False)
        self.pos = pos
        self.font = Font(self.ui_font["main_button"], text_size)
        self.image = text_render(text, self.font, Color("black"))
        self.rect = self.image.get_rect(center=(self.pos[0] - (self.image.get_width() / 2), self.pos[1]))


class ControllerIcon(UIMenu):
    def __init__(self, pos, images, control_type):
        UIMenu.__init__(self)
        self.pos = pos
        self.font = Font(self.ui_font["main_button"], int(46 * self.screen_scale[1]))
        self.images = images
        self.image = self.images[control_type].copy()
        self.rect = self.image.get_rect(center=self.pos)

    def change_control(self, control_type):
        if "joystick" in control_type:
            self.image = self.images[control_type[:-1]].copy()
            joystick_num = control_type[-1]
            text_surface = self.font.render(joystick_num, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
            self.image.blit(text_surface, text_rect)
        else:
            self.image = self.images[control_type]


class KeybindIcon(UIMenu):
    controller_icon = {}

    def __init__(self, pos, text_size, control_type, key):
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], text_size)
        self.pos = pos
        self.change_key(control_type, key, keybind_name=None)
        self.rect = self.image.get_rect(center=self.pos)

    def change_key(self, control_type, key, keybind_name):
        if control_type == "keyboard":
            if type(key) is str and "click" in key:
                self.draw_keyboard(key)
            else:
                self.draw_keyboard(pygame.key.name(key))
        elif control_type == "joystick":
            self.draw_joystick(key, keybind_name)
        self.rect = self.image.get_rect(center=self.pos)

    def draw_keyboard(self, text):
        text_surface = self.font.render(text, True, (0, 0, 0))
        size = text_surface.get_size()
        image_size = size[0] * 2
        if size[0] < 40:
            image_size = size[0] * 4
        self.image = Surface((image_size, size[1] * 2), SRCALPHA)
        draw.rect(self.image, (50, 50, 50), (0, 0, image_size, size[1] * 2), border_radius=2)
        draw.rect(self.image, (255, 255, 255),
                  (image_size * 0.1, size[1] * 0.3, image_size * 0.8, size[1] * 1.5),
                  border_radius=2)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

    def draw_joystick(self, key, keybind_name):

        text_surface = self.font.render(keybind_name[key], True, (0, 0, 0))
        size = text_surface.get_size()
        image_size = size[0] * 2
        if size[0] < 40:
            image_size = size[0] * 4
        self.image = Surface((image_size, size[1] * 2), SRCALPHA)
        draw.circle(self.image, (255, 255, 255), (self.image.get_width() / 2, self.image.get_height() / 2),
                    self.image.get_width() / 2)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class ValueBox(UIMenu):
    def __init__(self, image, pos, value, text_size):
        self._layer = 26
        UIMenu.__init__(self, player_interact=False)
        self.font = Font(self.ui_font["main_button"], text_size)
        self.pos = pos
        self.image = image.copy()
        self.base_image = self.image.copy()
        self.value = value
        text_surface = self.font.render(str(self.value), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def change_value(self, value):
        self.value = value
        self.image = self.base_image.copy()
        text_surface = self.font.render(str(self.value), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class TeamCoa(UIMenu):
    def __init__(self, not_selected_pos, selected_pos, coa_images, team, team_colour, name):
        self._layer = 12
        UIMenu.__init__(self, has_containers=True)

        self.selected = False

        self.coa_size = (int(60 * self.screen_scale[0]), int(60 * self.screen_scale[1]))
        self.selected_coa_size = (int(120 * self.screen_scale[0]), int(120 * self.screen_scale[1]))
        self.not_selected_image_base = Surface((self.coa_size[0], self.coa_size[1]))
        self.not_selected_image_base.fill((0, 0, 0))  # black border when not selected
        self.selected_image_base = Surface((400 * self.screen_scale[0], self.coa_size[1] * 2.2))
        self.selected_image_base.fill((0, 0, 0))  # black border when selected

        team_body = Surface((self.not_selected_image_base.get_width() * 0.95,
                             self.not_selected_image_base.get_height() * 0.95))
        team_body.fill(team_colour)
        white_rect = team_body.get_rect(
            center=(self.not_selected_image_base.get_width() / 2, self.not_selected_image_base.get_height() / 2))
        self.not_selected_image_base.blit(team_body, white_rect)
        team_body = Surface((self.selected_image_base.get_width() * 0.98,
                             self.selected_image_base.get_height() * 0.95))
        team_body.fill(team_colour)
        white_rect = team_body.get_rect(
            center=(self.selected_image_base.get_width() / 2, self.selected_image_base.get_height() / 2))
        self.selected_image_base.blit(team_body, white_rect)

        self.coa_images = coa_images

        self.pos = not_selected_pos
        self.not_selected_pos = not_selected_pos
        self.selected_pos = selected_pos
        self.image = None
        self.rect = None
        self.team = team

        self.font_size = int(self.selected_image_base.get_height() / 3.5)
        self.font = Font(self.ui_font["name_font"], self.font_size)

        self.change_coa(coa_images, name)

    def change_select(self, selected):
        self.selected = selected
        if self.selected:
            self.pos = self.selected_pos
            self.image = self.selected_image
        else:
            self.pos = self.not_selected_pos
            self.image = self.not_selected_image
        self.rect = self.image.get_rect(center=self.pos)

    def change_coa(self, coa_images, name):
        self.coa_images = coa_images

        # Only main coat of arms for not selected image
        self.not_selected_image = self.not_selected_image_base.copy()
        self.selected_image = self.selected_image_base.copy()
        if tuple(self.coa_images.values())[0]:  # coa image is not None
            coa_image = smoothscale(tuple(self.coa_images.values())[0],
                                    (int(self.coa_size[0] * 0.7), int(self.coa_size[1] * 0.7)))
            coa_rect = coa_image.get_rect(
                center=(self.not_selected_image.get_width() / 2, self.not_selected_image.get_height() / 2))
            self.not_selected_image.blit(coa_image, coa_rect)

            # All Coat of arms to selected image and main faction name
            small_coa_pos = [int(self.selected_coa_size[0] * 0.2), int(self.selected_coa_size[1] * 0.2)]
            for index, image in enumerate(self.coa_images.values()):
                if image:
                    if index == 0:  # first one as main faction coa
                        coa_image = smoothscale(image, (
                            int(self.selected_coa_size[0] * 0.65), int(self.selected_coa_size[1] * 0.65)))
                        coa_rect = coa_image.get_rect(
                            midtop=(self.selected_image.get_width() / 2, self.selected_coa_size[1] * 0.05))
                    else:
                        coa_image = smoothscale(image,
                                                (int(self.selected_coa_size[0] * 0.3),
                                                 int(self.selected_coa_size[1] * 0.3)))
                        coa_rect = coa_image.get_rect(center=small_coa_pos)
                        small_coa_pos[1] += int(self.selected_coa_size[1] * 0.3)
                        if index % 2 == 0:
                            small_coa_pos = [small_coa_pos[0] + int(self.selected_coa_size[0] * 0.4),
                                             int(self.selected_coa_size[1] * 0.2)]
                        if index == 6:
                            small_coa_pos[0] = int(self.selected_coa_size[0] * 2.3)
                    self.selected_image.blit(coa_image, coa_rect)

        self.name = name
        text_surface = text_render(str(self.name), self.font, Color("black"))
        text_rect = text_surface.get_rect(
            center=(int(self.selected_image.get_width() / 2), self.selected_image.get_height() - self.font_size))
        self.selected_image.blit(text_surface, text_rect)
        self.change_select(self.selected)


class LeaderModel(UIMenu):
    def __init__(self, pos, image):
        self._layer = 1
        UIMenu.__init__(self, player_interact=False)
        self.font_size = int(32 * self.screen_scale[1])

        self.leader_font = Font(self.ui_font["text_paragraph"], int(36 * self.screen_scale[1]))
        self.font = Font(self.ui_font["text_paragraph"], self.font_size)

        self.base_image = image.copy()
        self.image = self.base_image.copy()

        self.type_number_pos = ((self.image.get_width() / 4.5, self.image.get_height() / 3),  # infantry melee
                                (self.image.get_width() / 4.5, self.image.get_height() / 1.8),  # infantry range
                                (self.image.get_width() / 1.4, self.image.get_height() / 3),  # cav melee
                                (self.image.get_width() / 1.4, self.image.get_height() / 1.8),  # cav range
                                (self.image.get_width() / 3, self.image.get_height() / 1.32))  # total unit number

        self.rect = self.image.get_rect(topright=pos)

    def add_preview_model(self, model=None, coa=None):
        """Add coat of arms as background and/or leader model"""
        self.image = self.base_image.copy()
        if coa:
            new_coa = smoothscale(coa, (200 * self.screen_scale[0],
                                        200 * self.screen_scale[1]))
            rect = new_coa.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
            self.image.blit(new_coa, rect)
        if model:
            rect = model.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
            self.image.blit(model, rect)


class MapTitle(UIMenu):
    def __init__(self, pos):
        UIMenu.__init__(self)

        self.font = Font(self.ui_font["name_font"], int(44 * self.screen_scale[1]))
        self.pos = pos
        self.name = ""
        text_surface = self.font.render(str(self.name), True, (0, 0, 0))
        self.image = pygame.Surface((int(text_surface.get_width() + (5 * self.screen_scale[0])),
                                     int(text_surface.get_height() + (5 * self.screen_scale[1]))))

    def change_name(self, name):
        self.name = name
        text_surface = self.font.render(str(self.name), True, (0, 0, 0))
        self.image = pygame.Surface((int(text_surface.get_width() + (5 * self.screen_scale[0])),
                                     int(text_surface.get_height() + (5 * self.screen_scale[1]))))
        self.image.fill((0, 0, 0))

        white_body = pygame.Surface((text_surface.get_width(), text_surface.get_height()))
        white_body.fill((239, 228, 176))
        white_rect = white_body.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(white_body, white_rect)

        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(midtop=self.pos)


class NameTextBox(UIMenu):
    def __init__(self, box_size, pos, name, text_size=26, layer=15, box_colour=(255, 255, 255), center_text=False):
        self._layer = layer
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], int(text_size * self.screen_scale[1]))
        self.name = str(name)

        self.image = Surface(box_size)
        self.image.fill((0, 0, 0))  # black corner

        # White body square
        white_body = Surface((self.image.get_width() - 2, self.image.get_height() - 2))
        white_body.fill(box_colour)
        small_rect = white_body.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(white_body, small_rect)

        self.image_base = self.image.copy()

        # Name text
        text_surface = self.font.render(self.name, True, (0, 0, 0))
        if center_text:
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        else:  # text start at the left
            text_rect = text_surface.get_rect(midleft=(int(3 * self.screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)

        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def rename(self, new_name):
        self.name = new_name
        self.image = self.image_base.copy()
        text_surface = self.font.render(self.name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(int(3 * self.screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)


class ListBox(UIMenu):
    def __init__(self, pos, image, layer=14):
        self._layer = layer
        UIMenu.__init__(self, player_interact=False)
        self.image = image.copy()
        self.name_list_start = (self.image.get_width(), self.image.get_height())
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

        image_height = int(26 * self.screen_scale[1])
        self.max_row_show = int(
            self.image.get_height() / (
                        image_height + (6 * self.screen_scale[1])))  # max number of map on list can be shown

class NameList(UIMenu):
    def __init__(self, box, pos, name, text_size=26, layer=15):
        self._layer = layer
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], int(self.screen_scale[1] * text_size))
        self.name = str(name)

        self.image = Surface(
            (box.image.get_width() - int(18 * self.screen_scale[0]),
             int((text_size + 4) * self.screen_scale[1])))  # black corner
        self.image.fill((0, 0, 0))
        self.selected_image = self.image.copy()
        self.selected = False

        # White body square
        small_image = Surface(
            (box.image.get_width() - int(16 * self.screen_scale[0]), int((text_size + 2) * self.screen_scale[1])))
        small_image.fill((255, 255, 255))
        small_rect = small_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(small_image, small_rect)
        small_image.fill((255, 255, 128))
        self.selected_image.blit(small_image, small_rect)

        self.image_base = self.image.copy()

        # Name text
        text_surface = self.font.render(self.name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(int(3 * self.screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.selected_image.blit(text_surface, text_rect)

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

    def rename(self, new_name):
        self.name = new_name
        self.image = self.image_base.copy()
        text_surface = self.font.render(self.name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(int(3 * self.screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.selected_image.blit(text_surface, text_rect)

        self.not_selected_image = self.image.copy()


class ListAdapter:
    def __init__(self, _list, replace_on_select=None, replace_on_mouse_over=None):
        from engine.game.game import Game
        self.game = Game.game
        self.list = _list
        self.last_index = -1
        if replace_on_select:
            self.on_select = types.MethodType(replace_on_select, self)
        if replace_on_mouse_over:
            self.on_mouse_over = types.MethodType(replace_on_mouse_over, self)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, item):
        return self.list[item]

    def on_select(self, item_index, item_text):
        pass

    def on_mouse_over(self, item_index, item_text):
        pass

    def get_highlighted_index(self):
        return self.last_index


class ListAdapterHideExpand:

    # actual list refer to the origin full list
    # visual list refer to the list after some if any of the elements been hidden

    def __init__(self, _list, _self=None, replace_on_select=None, replace_on_mouse_over=None):
        self.actual_list = actual_list = [ c[1] for c in _list ]
        self.actual_list_open_index = [False for element in actual_list]
        self.actual_list_level = [ element[0] for element in _list ]

        if replace_on_select:
            self.on_select = types.MethodType(replace_on_select, self)
        if replace_on_mouse_over:
            self.on_mouse_over = types.MethodType(replace_on_mouse_over, self)

    def get_actual_index_level(self, index):
        return self.actual_list_level[index]

    def is_actual_index_hidden(self, index):

        level = self.get_actual_index_level(index)

        if level == 0:
            return False

        # scan up in the list till you hit a top level element and check if it is open
        # and if it is, this element should be open
        for i in range(1, len(self.actual_list)): 
            u = index - i
            if self.get_actual_index_level(u) == level - 1:
                break

        if level > 1 and self.is_actual_index_hidden(u):
            return True

        return not self.actual_list_open_index[u]

    def __len__(self):
        return len([i for i in range(len(self.actual_list)) if not self.is_actual_index_hidden(i)])

    def __getitem__(self, item):
        r = list()
        for index, element in enumerate(self.actual_list):
            if self.is_actual_index_hidden(index): continue
            r.append(element)
        if item >= len(r): return None

        actual_index = self.get_visible_index_actual_index()[item]
        if self.actual_list_open_index[actual_index]:
            return r[item].replace(">", "|")
        else:
            return r[item]

    def get_visible_index_actual_index(self):
        r = dict()
        visible_index = -1
        for actual_index in range(len(self.actual_list)):
            if self.is_actual_index_hidden(actual_index): continue
            visible_index += 1
            r[visible_index] = actual_index
        return r

    def get_actual_index_visible_index(self):
        return { v:k for k,v in self.get_visible_index_actual_index().items() }

    def get_highlighted_index(self):
        return -1

    def on_select(self, item_index, item_text):
        actual_index = self.get_visible_index_actual_index().get(item_index)
        if actual_index is None: return
        self.actual_list_open_index[actual_index] = not self.actual_list_open_index[actual_index]


class CampaignListAdapter(ListAdapterHideExpand):

    def __init__(self):
        from engine.game.game import Game
        self.game = Game.game
        self.map_source_index = dict() # stores the map-sources 's list index. ex { ('atestmap', 1): 3, ('varaville1', 0): 6 }
        localisation = Game.localisation
        map_data = self.game.preset_map_data
        actual_level_list = []

        self.campaign_name_index = {}
        self.map_name_index = {}
        self.map_source_name_index = {}

        for campaign_file_name in map_data:  # add campaign
            campaign_name = localisation.grab_text(key=("preset_map", "info", campaign_file_name, "Name"))
            actual_level_list.append((0,campaign_name))
            self.campaign_name_index[campaign_name] = campaign_file_name
            for map_file_name in map_data[campaign_file_name]:  # add map
                map_name = localisation.grab_text(key=("preset_map", campaign_file_name, "info", map_file_name, "Name"))
                actual_level_list.append((1,"> " + map_name))
                self.map_name_index[map_name] = map_file_name
                for source_file_name in map_data[campaign_file_name][map_file_name]["source"]:  # add source
                    source_name = localisation.grab_text(key=("preset_map", campaign_file_name, map_file_name, "source", int(source_file_name), "Source"))
                    self.map_source_name_index[source_name] = source_file_name
                    current_index = len(actual_level_list)
                    self.map_source_index[(map_file_name,source_file_name)] = current_index
                    actual_level_list.append((2,">> " + source_name))

        ListAdapterHideExpand.__init__(self, actual_level_list)

    def get_highlighted_index(self):
        if not hasattr(self.game, 'map_selected'): return None
        return self.get_actual_index_visible_index().get(self.map_source_index[(self.game.map_selected, self.game.map_source_selected)])

    def on_select(self, item_index, item_text):

        actual_index = self.get_visible_index_actual_index()[item_index]

        # if click on a source then load it
        if self.get_actual_index_level(actual_index) == 2: # 2 = source
            _map, source = { v:k for k,v in self.map_source_index.items() }[actual_index]
            self.game.current_map_select = self.game.preset_map_folder.index(_map)
            self.game.map_selected = _map
            self.game.campaign_selected = self.game.battle_campaign[_map]
            self.game.map_source_selected = source
            self.game.change_battle_source()

        else:  # if not fall back to the normal behaviour of a hide-expand elements
            super().on_select(item_index, item_text)

    def on_mouse_over(self, item_index, item_text):
        """
        Method for campaign map list where player hovering over item will display historical information of campaign, map,
        or map source
        :param self: Listui object
        :param item_index: Index of selected item in list
        :param item_text: Text of selected item
        """
        item_name = item_text.replace(">", "")
        item_name = item_name.replace("|", "")
        item_id = (item_text, item_index)
        if item_id != self.game.text_popup.last_shown_id:
            if item_name[0] == " ":  # remove space from subsection name
                item_name = item_name[1:]
            if ">>" in item_text or "||" in item_text:  # source item
                actual_index = self.get_visible_index_actual_index()[item_index]

                _map, source = {v: k for k, v in self.map_source_index.items()}[actual_index]
                popup_text = [value for key, value in
                              self.game.localisation.grab_text(("preset_map",
                                                                self.game.battle_campaign[_map],
                                                                _map, "source",
                                                                source)).items()]
            elif ">" in item_text or "|" in item_text:  # map item
                popup_text = [value for key, value in
                              self.game.localisation.grab_text(("preset_map",
                                                                self.game.battle_campaign[self.map_name_index[item_name]],
                                                                "info", self.map_name_index[item_name])).items()]

            else:  # campaign item
                popup_text = [value for key, value in
                              self.game.localisation.grab_text(("preset_map", "info",
                                                                self.campaign_name_index[item_name])).items()]

            self.game.text_popup.popup(self.game.cursor.rect, popup_text, shown_id=item_id,
                                       width_text_wrapper=1000 * self.game.screen_scale[0])
        else:  # already showing this leader no need to create text again
            self.game.text_popup.popup(self.game.cursor.rect, None, shown_id=item_id,
                                       width_text_wrapper=1000 * self.game.screen_scale[0])
        self.game.add_ui_updater(self.game.text_popup)


class TickBox(UIMenu):
    def __init__(self, pos, image, tick_image, option):
        """option is in str text for identifying what kind of tick_box it is"""
        self._layer = 14
        UIMenu.__init__(self)

        self.option = option

        self.not_tick_image = image
        self.tick_image = tick_image
        self.tick = False

        self.not_tick_image = image
        self.tick_image = tick_image

        self.image = self.not_tick_image

        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def change_tick(self, tick):
        self.tick = tick
        if self.tick:
            self.image = self.tick_image
        else:
            self.image = self.not_tick_image


class BackgroundBox(UIMenu):
    def __init__(self, pos, image, layer=10):
        self._layer = layer
        UIMenu.__init__(self, player_interact=False)
        self.image = image.copy()

        self.font = Font(self.ui_font["main_button"], int(20 * self.screen_scale[1]))

        text_surface = self.font.render("Start Battle At Night", True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 5))
        self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect(topright=pos)


class MapPreview(UIMenu, BattleMap):
    def __init__(self, pos):
        UIMenu.__init__(self, player_interact=False)
        BattleMap.__init__(self)

        self.pos = pos

        self.image = Surface((450 * self.screen_scale[0], 450 * self.screen_scale[1]))
        self.leader_dot = {team: {True: None, False: None} for team in self.team_colour.keys()}

        self.map_scale_width = 1
        self.map_scale_height = 1

        leader_dot = Surface((10 * self.screen_scale[0], 10 * self.screen_scale[1]))  # dot for team unit
        leader_dot.fill((0, 0, 0))  # black corner
        leader_colour_dot = Surface((8 * self.screen_scale[0], 8 * self.screen_scale[1]))
        rect = leader_dot.get_rect(topleft=(2 * self.screen_scale[0], 2 * self.screen_scale[1]))

        for team, colour in self.team_colour.items():
            new_dot = leader_colour_dot.copy()
            new_dot.fill(colour)
            add_dot = leader_dot.copy()
            add_dot.blit(new_dot, rect)
            self.leader_dot[team][False] = add_dot

        for team, colour in self.selected_team_colour.items():
            new_selected_dot = leader_colour_dot.copy()
            new_selected_dot.fill(colour)
            new_selected_dot.fill(colour)
            add_dot = leader_dot.copy()
            add_dot.blit(new_selected_dot, rect)
            self.leader_dot[team][True] = add_dot

        self.rect = self.image.get_rect(topleft=self.pos)

    def change_map(self, base_map, feature_map, height_map):

        from engine.battlemap.battlemap import topology_map_creation

        new_base_map = scale(base_map, (300, 300))
        new_feature_map = scale(feature_map, (300, 300))
        new_height_map = topology_map_creation(scale(height_map, (300, 300)), 4)

        self.map_scale_width = base_map.get_width() / (450 * self.screen_scale[0])
        self.map_scale_height = base_map.get_height() / (450 * self.screen_scale[1])

        map_image = Surface((300, 300))
        for row_pos in range(0, 300):  # recolour the map
            for col_pos in range(0, 300):
                terrain = new_base_map.get_at((row_pos, col_pos))  # get colour at pos to obtain the terrain type
                terrain_index = self.terrain_colour.index(terrain)

                feature = new_feature_map.get_at((row_pos, col_pos))  # get colour at pos to obtain the terrain type
                feature_index = None
                if feature in self.feature_colour:
                    feature_index = self.feature_colour.index(feature)
                    feature_index = feature_index + (terrain_index * len(self.feature_colour))
                new_colour = self.battle_map_colour[feature_index][1]
                rect = Rect(row_pos, col_pos, 1, 1)
                map_image.fill(new_colour, rect)

        map_image.blit(new_height_map, map_image.get_rect(topleft=(0, 0)))

        map_image = scale(map_image, (450 * self.screen_scale[0], 450 * self.screen_scale[1]))
        image_rect = map_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(map_image, image_rect)
        self.base_image = self.image.copy()

    def change_mode(self, mode, team_pos_list=None, camp_pos_list=None, selected=None, camp_selected=None):
        """map mode: 0 = map without army dot, 1 = with army dot"""
        self.image = self.base_image.copy()
        if mode == 1:
            if camp_pos_list:
                for team, pos_list in camp_pos_list.items():
                    for pos in pos_list:
                        colour = self.team_colour[team]
                        if pos == camp_selected:
                            colour = self.selected_team_colour[team]
                        draw.circle(self.image, colour,
                                    (pos[0][0] * ((450 * self.screen_scale[0]) / 1000),
                                     pos[0][1] * ((450 * self.screen_scale[1]) / 1000)),
                                    pos[1] * ((450 * self.screen_scale[0]) / 1000),
                                    int(5 * self.screen_scale[0]))
            if team_pos_list:
                for team, pos_list in team_pos_list.items():
                    if type(pos_list) is dict:
                        new_pos_list = pos_list.values()
                    else:
                        new_pos_list = pos_list
                    for pos in new_pos_list:
                        select = False
                        if pos == selected:
                            select = True
                        scaled_pos = Vector2(pos[0] * ((450 * self.screen_scale[0]) / 1000),
                                             pos[1] * ((450 * self.screen_scale[1]) / 1000))
                        rect = self.leader_dot[team][select].get_rect(center=scaled_pos)
                        self.image.blit(self.leader_dot[team][select], rect)
        self.rect = self.image.get_rect(topleft=self.pos)


class OrgChart(UIMenu):
    def __init__(self, image, pos):
        UIMenu.__init__(self, player_interact=False)
        self.node_rect = {}
        self.image = image
        self.base_image = self.image.copy()
        self.size = self.image.get_size()
        self.rect = self.image.get_rect(topleft=pos)

    def hierarchy_pos(self, graph_input, root=None, width=1., vert_gap=0.2, y_pos=0, x_pos=0, pos=None, parent=None):
        """
        Adapted from Joel's answer at https://stackoverflow.com/a/29597209/2966723.
        Licensed under Creative Commons Attribution-Share Alike

        :param graph_input: the graph (must be a tree)
        :param root: the root node of current branch
        :param width: horizontal space allocated for this branch - avoids overlap with other branches
        :param vert_gap: gap between levels of hierarchy
        :param y_pos: vertical location of node (assign with root)
        :param x_pos: horizontal location of node  (assign with root)
        :param pos: a dict saying where all nodes go if they have been assigned
        :param parent: parent of this branch. - only affects it if non-directed
        :return the positions to plot this in a hierarchical layout
        """

        if pos is None:
            pos = {root: (x_pos, y_pos)}
        else:
            pos[root] = (x_pos, y_pos)
        children = list(graph_input.neighbors(root))
        if not isinstance(graph_input, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = x_pos - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = self.hierarchy_pos(graph_input, root=child, width=dx, vert_gap=vert_gap,
                                         y_pos=y_pos - vert_gap, x_pos=nextx,
                                         pos=pos, parent=root)
        return pos

    def add_chart(self, unit_data, preview_unit, selected=None):
        self.image = self.base_image.copy()
        self.node_rect = {}

        if selected is not None:
            graph_input = nx.Graph()

            edge_list = [(unit["Temp Leader"], index) for index, unit in enumerate(unit_data) if
                         type(unit["Temp Leader"]) is int]
            try:
                graph_input.add_edges_from(edge_list)
                pos = self.hierarchy_pos(graph_input, root=selected, width=self.image.get_width(),
                                         vert_gap=-self.image.get_height() * 0.5 / len(edge_list), y_pos=100,
                                         x_pos=self.image.get_width() / 2)
                image_size = (self.image.get_width() / (len(pos) * 1.5), self.image.get_height() / (len(pos) * 1.5))
            except (nx.exception.NetworkXError, ZeroDivisionError):  # has only one leader
                pos = {selected: (self.image.get_width() / 2, self.image.get_width() / 2)}
                image_size = (self.image.get_width() / 2, self.image.get_height() / 2)

            for unit in pos:
                for unit_index, icon in enumerate(preview_unit):
                    if unit_index == unit:
                        image = smoothscale(icon.portrait, image_size)
                        self.node_rect[unit] = image.get_rect(center=pos[unit])
                        self.image.blit(image, self.node_rect[unit])
                        break

            for unit in pos:
                if type(unit_data[unit]["Temp Leader"]) is int:
                    line_width = int(self.image.get_width() / 100)
                    if line_width < 1:
                        line_width = 1
                    draw.line(self.image, (0, 0, 0), self.node_rect[unit_data[unit]["Temp Leader"]].midbottom,
                              self.node_rect[unit].midtop, width=line_width)


class TextPopup(UIMenu):
    def __init__(self):
        self._layer = 15
        UIMenu.__init__(self, player_interact=False)
        self.font_size = int(24 * self.screen_scale[1])
        self.font = Font(self.ui_font["main_button"], self.font_size)
        self.pos = (0, 0)
        self.last_shown_id = None
        self.text_input = ""

    def popup(self, cursor_rect, text_input, shown_id=None, width_text_wrapper=0):
        """Pop out text box with input text list in multiple line, one item equal to one line"""
        self.last_shown_id = shown_id
        if text_input is not None and (self.text_input != text_input or self.last_shown_id != shown_id):
            self.text_input = text_input
            if type(text_input) == str:
                self.text_input = [text_input]
            text_surface = []
            if width_text_wrapper:
                max_height = 0
                max_width = width_text_wrapper
                for text in self.text_input:
                    image_height = (len(text) * (self.font_size ** 2 / 1.3) / width_text_wrapper)
                    if image_height < self.font_size:  # only one line
                        print(text)
                        text_image = Surface((width_text_wrapper, self.font_size))
                        text_image.fill((255, 255, 255))
                        surface = self.font.render(text, True, (0, 0, 0))
                        text_image.blit(surface, (self.font_size, 0))
                        text_surface.append(text_image)  # text input font surface
                        max_height += self.font_size * 2
                    else:
                        text_image = Surface((width_text_wrapper, image_height))
                        text_image.fill((255, 255, 255))
                        make_long_text(text_image, text, (self.font_size, self.font_size), self.font)
                        text_surface.append(text_image)
                        max_height += text_image.get_height() + self.font_size + int(self.font_size / 5)
            else:
                max_width = 0
                max_height = 0
                for text in self.text_input:
                    surface = self.font.render(text, True, (0, 0, 0))
                    text_surface.append(surface)  # text input font surface
                    text_rect = surface.get_rect(topleft=(self.font_size, self.font_size))  # text input position at (1,1) on white box image
                    if text_rect.width > max_width:
                        max_width = text_rect.width
                    max_height += self.font_size + int(self.font_size / 5)

            self.image = Surface((max_width + 6, max_height + 6))  # black border
            image = Surface((max_width + 2, max_height + 2))  # white Box
            image.fill((255, 255, 255))
            rect = self.image.get_rect(topleft=(2, 2))  # white box image position at (2,2) on black border image
            self.image.blit(image, rect)

            height = 1
            for surface in text_surface:
                text_rect = surface.get_rect(topleft=(4, height))
                image.blit(surface, text_rect)
                self.image.blit(surface, text_rect)  # blit text
                height += surface.get_height()

        self.rect = self.image.get_rect(bottomleft=cursor_rect.bottomright)

        exceed_right = False
        if cursor_rect.bottomright[0] + self.image.get_width() > self.screen_size[0]:  # exceed right screen
            self.rect = self.image.get_rect(topright=cursor_rect.bottomleft)
            exceed_right = True
        elif cursor_rect.bottomleft[0] - self.image.get_width() < 0:  # exceed left side screen
            self.rect = self.image.get_rect(topleft=cursor_rect.bottomright)

        if cursor_rect.bottomright[1] + self.image.get_height() > self.screen_size[1]:  # exceed bottom screen
            self.rect = self.image.get_rect(bottomleft=cursor_rect.topright)
            if exceed_right:
                self.rect = self.image.get_rect(bottomright=cursor_rect.topleft)
        elif cursor_rect.bottomright[1] - self.image.get_height() < 0:  # exceed top screen
            self.rect = self.image.get_rect(topleft=cursor_rect.bottomright)
            if exceed_right:
                self.rect = self.image.get_rect(topright=cursor_rect.bottomleft)


class BoxUI(UIMenu, Containable, Container):

    def __init__(self, size, parent):
        UIMenu.__init__(self, player_interact=False)
        self.parent = parent
        self.size = size
        self._layer = -1  # NOTE: not sure if this is good since underscore indicate it is a private variable but it works for now
        self.pos = (0, 0)
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.image = Surface(self.rect[2:], SRCALPHA)
        # self.image.fill("#302d2ce0")

    def update(self):
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.image = Surface(self.rect[2:], SRCALPHA)
        # self.image.fill("#bbbbaabb")

    def get_relative_size_inside_container(self):
        return (0.3, 0.5)  # TODO: base this on variable

    def get_relative_position_inside_container(self):
        return {
            "pivot": (0, 0),
            "origin": self.pos,
        }

    def get_rect(self):
        return self.rect

    def get_size(self):
        return self.image.get_size()


class ListUI(UIMenu, Containable):

    def __init__(self, origin, pivot, size, items, parent, item_size, layer=0):

        from engine.game.game import Game
        from engine.utility import load_image
        game = Game.game
        self._layer = layer
        UIMenu.__init__(self)
        self.pivot = pivot
        self.origin = origin
        self.parent = parent
        frame_file = "new_button.png"  # "list_frame.png" # using the button frame to test if it looks good
        self.frame = load_image(game.module_dir, (1, 1), frame_file, ("ui", "mainmenu_ui"))
        self.scroll_box_frame = load_image(game.module_dir, (1, 1), "scroll_box_frame.png", ("ui", "mainmenu_ui"))

        self.item_size = item_size

        self.relative_size_inside_container = size

        self.items = items

        self.in_scroll_box = False
        self.hold_scroll_box = None
        self.selected_index = None

        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)

        self.last_length_check = len(self.items)

        self.calc_scroll_bar()
        self.image = self.get_refreshed_image()

    def calc_scroll_bar(self):
        item_size = self.item_size
        self.scroll_bar_height = self.rect[3] - 12
        self.scroll_box_height = int(self.scroll_bar_height * (item_size / len(self.items)))
        divider = self.get_number_of_items_outside_visible_list()

        if divider is not None:
            self.has_scroll = True
            self.scroll_step_height = (self.scroll_bar_height - self.scroll_box_height) / divider
        else:
            self.has_scroll = False

        self.scroll_box = make_image_by_frame(self.scroll_box_frame, (14, self.scroll_box_height))
        self.scroll_box_index = 0

    def get_number_of_items_outside_visible_list(self):
        r = len(self.items) - self.item_size
        if r <= 0:
            return None
        return r

    def get_item_height(self):
        return self.scroll_bar_height // self.item_size

    def get_relative_size_inside_container(self):
        return self.relative_size_inside_container

    def get_refreshed_image(self):
        assert type(self.scroll_box_index) == int, type(self.scroll_box_index)
        item_height = self.get_item_height()
        size = self.rect[2:]
        self.image = make_image_by_frame(self.frame, size)
        item_height = self.get_item_height()

        # draw items
        item_size = self.item_size
        if len(self.items) < item_size:  # For listui with item less than provided size
            item_size = len(self.items)
        for i in range(item_size):
            item_index = i + self.scroll_box_index
            text_color = (47 if item_index == self.selected_index else 0,) * 3
            if item_index == self.selected_index or item_index == self.items.get_highlighted_index():

                background_color = "#cbc2a9"
                if item_index == self.items.get_highlighted_index():
                    background_color = "#776622"
                    text_color = "#eeeeee"
                draw.rect(self.image, background_color, (6, 6 + i * item_height, size[0] - 13 * self.has_scroll - 12, item_height))

            font = Font(self.ui_font["main_button"], 20)
            blit_text = self.items[item_index]
            if self.items[item_index] is not None:  # assuming list ui has only 3 levels
                if ">>" in self.items[item_index] or "||" in self.items[item_index]:
                    font = Font(self.ui_font["main_button"], 14)
                    blit_text = "  " + blit_text
                elif ">" in self.items[item_index] or "|" in self.items[item_index]:
                    font = Font(self.ui_font["main_button"], 18)
                    blit_text = " " + blit_text

            self.image.blit(
                draw_text(blit_text, font, text_color),
                (20, item_height // 2 + 6 - 9 + i * item_height))

        # draw scroll bar
        if scroll_bar_rect := self.get_scroll_bar_rect():
            draw.rect(self.image, "#d2cab4", scroll_bar_rect)

        # draw scroll box
        if scroll_box_rect := self.get_scroll_box_rect():
            self.image.blit(self.scroll_box, scroll_box_rect)
            if self.in_scroll_box or self.hold_scroll_box is not None:
                draw.rect(self.image, (100, 0, 0) if self.hold_scroll_box is not None else (50,) * 3,
                          scroll_box_rect, 1)

        return self.image

    def get_scroll_bar_rect(self):
        if not self.has_scroll: return None
        return Rect(self.rect[2] - 18, 6, 14, self.scroll_bar_height)

    def get_scroll_box_rect(self):
        if not self.has_scroll: return None
        return Rect(self.rect[2] - 18, self.scroll_box_index * self.scroll_step_height + 6, *self.scroll_box.get_size())

    def update(self):

        if self.last_length_check != len(self.items):
            self.last_length_check = len(self.items)
            self.calc_scroll_bar()

        mouse_pos = self.cursor.pos
        relative_mouse_pos = [mouse_pos[i] - self.rect[i] for i in range(2)]

        # size = tuple(map(int, self.rect[2:]))
        self.mouse_over = False
        self.selected_index = None

        # detect if in list or over scroll box
        self.in_scroll_box = False
        if self.rect.collidepoint(mouse_pos):
            in_list = True
            self.mouse_over = True
            if scroll_bar_rect := self.get_scroll_bar_rect():
                if scroll_bar_rect.collidepoint(relative_mouse_pos):
                    if self.get_scroll_box_rect().collidepoint(relative_mouse_pos):
                        self.in_scroll_box = True
                    in_list = False

            # Check for scrolling button
            noiovl = self.get_number_of_items_outside_visible_list()
            if self.cursor.scroll_down and noiovl:
                self.scroll_box_index += 1
                if self.scroll_box_index > noiovl:
                    self.scroll_box_index = noiovl
            elif self.cursor.scroll_up and noiovl:
                self.scroll_box_index -= 1
                if self.scroll_box_index < 0:
                    self.scroll_box_index = 0

            if self.has_scroll and self.get_scroll_bar_rect().collidepoint(relative_mouse_pos):
                if self.get_scroll_box_rect().collidepoint(relative_mouse_pos):
                    self.in_scroll_box = True
            else:
                in_list = True

            # scroll box drag handler
            if not self.cursor.is_select_down:
                self.hold_scroll_box = None
            if self.in_scroll_box and self.cursor.is_select_just_down:
                self.hold_scroll_box = relative_mouse_pos[1]
                self.scroll_box_index_at_hold = self.scroll_box_index

            if self.hold_scroll_box:
                self.scroll_box_index = self.scroll_box_index_at_hold + int(
                    (relative_mouse_pos[1] - self.hold_scroll_box + self.scroll_step_height / 2) / self.scroll_step_height)
                noiovl = self.get_number_of_items_outside_visible_list()
                if self.scroll_box_index > noiovl:
                    self.scroll_box_index = noiovl
                elif self.scroll_box_index < 0:
                    self.scroll_box_index = 0

            # item handler
            if in_list and not self.hold_scroll_box:
                item_height = self.get_item_height()
                relative_index = ((relative_mouse_pos[1] - 6) // item_height)
                if relative_index >= 0 and relative_index < self.item_size:
                    self.selected_index = relative_index + self.scroll_box_index

            if self.selected_index is not None:
                if self.selected_index >= len(self.items): self.selected_index = None

            if in_list and self.selected_index is not None:
                self.items.on_mouse_over(self.selected_index, self.items[self.selected_index])
                if self.cursor.is_select_just_up or self.cursor.is_alt_select_just_up:
                    self.items.on_select(self.selected_index, self.items[self.selected_index])
                    self.cursor.is_select_just_up = False
                    self.cursor.is_alt_select_just_up = False

            # refresh image

            self.image = self.get_refreshed_image()

    def get_relative_position_inside_container(self):
        return {
            "pivot": self.pivot,
            "origin": self.origin,
        }

    def get_rect(self):
        return self.rect

    def get_size(self):
        return self.image.get_size()
