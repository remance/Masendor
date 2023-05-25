import networkx as nx
import pygame
import pygame.transform
import pyperclip
from functools import lru_cache

from engine.battlemap.battlemap import BattleMap

from engine.utility import keyboard_mouse_press_check, text_render, minimise_number_text, make_long_text


def make_image_by_frame(frame: pygame.Surface, final_size):
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

    image = pygame.Surface(final_size, pygame.SRCALPHA)

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
    pygame.draw.rect(image, bc, (css + o[0], css, fs[0] - css * 2 + o[2] - o[0], fs[1] - css * 2))

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


class UIMenu(pygame.sprite.Sprite):
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
        self.screen_size = Game.screen_size
        self.localisation = Game.localisation
        self.cursor = Game.cursor
        self.updater = Game.main_ui_updater
        self.player_interact = player_interact
        if has_containers:
            pygame.sprite.Sprite.__init__(self, self.containers)
        else:
            pygame.sprite.Sprite.__init__(self)
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
        UIMenu.__init__(self, has_containers=True)
        self.images = images
        self.image = images["normal"]
        self.pos = (0, 0)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.is_select_just_down = False
        self.is_select_down = False
        self.is_select_just_up = False
        self.is_mouse_right_just_down = False
        self.is_mouse_right_down = False
        self.is_mouse_right_just_up = False
        self.scroll_up = False
        self.scroll_down = False

    def update(self):
        """Update cursor position based on mouse position and mouse button click"""
        self.pos = pygame.mouse.get_pos()
        self.rect.topleft = self.pos
        self.is_select_just_down, self.is_select_down, self.is_select_just_up = keyboard_mouse_press_check(
            pygame.mouse, 0, self.is_select_just_down, self.is_select_down, self.is_select_just_up)

        self.is_mouse_right_just_down, self.is_mouse_right_down, self.is_mouse_right_just_up = keyboard_mouse_press_check(
            pygame.mouse, 0, self.is_mouse_right_just_down, self.is_mouse_right_down, self.is_mouse_right_just_up)

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

        self.font = pygame.font.Font(self.ui_font["main_button"], int(48 * self.screen_scale[1]))

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
        self.font = pygame.font.Font(self.ui_font["main_button"], int(30 * self.screen_scale[1]))
        self.pos = pos
        self.image = pygame.Surface((width - 10, int(34 * self.screen_scale[1])))
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
        UIMenu.__init__(self, player_interact=False)

        self.font = pygame.font.Font(self.ui_font["main_button"], int(36 * self.screen_scale[1]))
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

        self.font = pygame.font.Font(self.ui_font["main_button"], int(font_size * self.screen_scale[1]))
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

    def get_adjusted_rect_to_be_inside_container(self, container):
        rpic = self.get_relative_position_inside_container()
        rsic = self.get_relative_size_inside_container()
        pivot = rpic["pivot"]
        origin = rpic["origin"]

        if rsic is None:
            return pygame.rect.Rect(
                *[container.get_rect()[i] - (self.get_size()[i] * (origin[i] + 1)) // 2 + (pivot[i] + 1) * container.get_rect()[i + 2] // 2 for i in
                  range(2)], *self.get_size())
        else:
            size = [container.get_size()[i] * rsic[i] for i in range(2)]
            return pygame.rect.Rect(
                *[container.get_rect()[i] - (size[i] * (origin[i] + 1)) // 2 + (pivot[i] + 1) * container.get_rect()[i + 2] // 2 for i in range(2)],
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
        pygame.draw.rect(hover_button, "#DD0000", hover_button.get_rect(), 1)

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
        self.font = pygame.font.Font(self.ui_font["main_button"], 17)
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
        self.font = pygame.font.Font(self.ui_font["main_button"], text_size)
        self.image = text_render(text, self.font, pygame.Color("black"))
        self.rect = self.image.get_rect(center=(self.pos[0] - (self.image.get_width() / 2), self.pos[1]))


class ControllerIcon(UIMenu):
    def __init__(self, pos, images, control_type):
        UIMenu.__init__(self)
        self.pos = pos
        self.font = pygame.font.Font(self.ui_font["main_button"], int(46 * self.screen_scale[1]))
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
        self.font = pygame.font.Font(self.ui_font["main_button"], text_size)
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
        self.image = pygame.Surface((image_size, size[1] * 2), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (50, 50, 50), (0, 0, image_size, size[1] * 2), border_radius=2)
        pygame.draw.rect(self.image, (255, 255, 255),
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
        self.image = pygame.Surface((image_size, size[1] * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (self.image.get_width() / 2, self.image.get_height() / 2),
                           self.image.get_width() / 2)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class ValueBox(UIMenu):
    def __init__(self, image, pos, value, text_size):
        self._layer = 26
        UIMenu.__init__(self, player_interact=False)
        self.font = pygame.font.Font(self.ui_font["main_button"], text_size)
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
        UIMenu.__init__(self, has_containers=True)

        self.selected = False
        self.coa_size = (int(60 * self.screen_scale[0]), int(60 * self.screen_scale[1]))
        self.selected_coa_size = (int(120 * self.screen_scale[0]), int(120 * self.screen_scale[1]))
        self.not_selected_image_base = pygame.Surface((self.coa_size[0], self.coa_size[1]))
        self.not_selected_image_base.fill((0, 0, 0))  # black border when not selected
        self.selected_image_base = pygame.Surface((self.coa_size[0] * 5, self.coa_size[1] * 2))
        self.selected_image_base.fill((0, 0, 0))  # black border when selected

        team_body = pygame.Surface((self.not_selected_image_base.get_width() * 0.95,
                                    self.not_selected_image_base.get_height() * 0.95))
        team_body.fill(team_colour)
        white_rect = team_body.get_rect(
            center=(self.not_selected_image_base.get_width() / 2, self.not_selected_image_base.get_height() / 2))
        self.not_selected_image_base.blit(team_body, white_rect)
        team_body = pygame.Surface((self.selected_image_base.get_width() * 0.95,
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
            coa_image = pygame.transform.smoothscale(tuple(self.coa_images.values())[0],
                                                     (int(self.coa_size[0] * 0.7), int(self.coa_size[1] * 0.7)))
            coa_rect = coa_image.get_rect(
                center=(self.not_selected_image.get_width() / 2, self.not_selected_image.get_height() / 2))
            self.not_selected_image.blit(coa_image, coa_rect)

            # All Coat of arms to selected image and main faction name
            small_coa_pos = [int(self.selected_coa_size[0] * 0.2), int(self.selected_coa_size[1] * 0.2)]
            for index, image in enumerate(self.coa_images.values()):
                if image:
                    if index == 0:  # first one as main faction coa
                        coa_image = pygame.transform.smoothscale(image, (
                            int(self.selected_coa_size[0] * 0.65), int(self.selected_coa_size[1] * 0.65)))
                        coa_rect = coa_image.get_rect(
                            midtop=(self.selected_image.get_width() / 2, self.selected_coa_size[1] * 0.05))
                    else:
                        coa_image = pygame.transform.smoothscale(image,
                                                                 (int(self.selected_coa_size[0] * 0.3),
                                                                  int(self.selected_coa_size[1] * 0.3)))
                        coa_rect = coa_image.get_rect(center=small_coa_pos)
                        small_coa_pos[1] += int(self.selected_coa_size[1] * 0.3)
                        if index % 3 == 0:
                            small_coa_pos = [small_coa_pos[0] + int(self.selected_coa_size[0] * 0.4),
                                             int(self.selected_coa_size[1] * 0.2)]
                        if index == 6:
                            small_coa_pos[0] = int(self.selected_coa_size[0] * 1.8)
                    self.selected_image.blit(coa_image, coa_rect)

        self.name = name
        font_size = int(self.selected_image_base.get_height() / 5)
        font = pygame.font.Font(self.ui_font["name_font"], font_size)
        text_surface = text_render(str(self.name), font, pygame.Color("black"))
        text_rect = text_surface.get_rect(
            center=(int(self.selected_image.get_width() / 2), self.selected_image.get_height() - font_size))
        self.selected_image.blit(text_surface, text_rect)
        self.change_select(False)


class LeaderModel(UIMenu):
    def __init__(self, pos, image):
        self._layer = 1
        UIMenu.__init__(self, player_interact=False)
        self.font_size = int(32 * self.screen_scale[1])

        self.leader_font = pygame.font.Font(self.ui_font["text_paragraph"], int(36 * self.screen_scale[1]))
        self.font = pygame.font.Font(self.ui_font["text_paragraph"], self.font_size)

        self.base_image = image.copy()
        self.image = self.base_image.copy()

        self.type_number_pos = ((self.image.get_width() / 4.5, self.image.get_height() / 3),  # infantry melee
                                (self.image.get_width() / 4.5, self.image.get_height() / 1.8),  # infantry range
                                (self.image.get_width() / 1.4, self.image.get_height() / 3),  # cav melee
                                (self.image.get_width() / 1.4, self.image.get_height() / 1.8),  # cav range
                                (self.image.get_width() / 3, self.image.get_height() / 1.32))  # total unit number

        self.rect = self.image.get_rect(topleft=pos)

    def add_preview_model(self, model=None, coa=None):
        """Add coat of arms as background and/or leader model"""
        self.image = self.base_image.copy()
        if coa:
            new_coa = pygame.transform.smoothscale(coa, (200 * self.screen_scale[0],
                                                         200 * self.screen_scale[1]))
            rect = new_coa.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
            self.image.blit(new_coa, rect)
        if model:
            rect = model.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
            self.image.blit(model, rect)


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
            self.image.get_height() / (image_height + (6 * self.screen_scale[1])))  # max number of map on list can be shown


class NameList(UIMenu):
    def __init__(self, box, pos, name, text_size=26, layer=15):
        self._layer = layer
        UIMenu.__init__(self)
        self.font = pygame.font.Font(self.ui_font["main_button"], int(self.screen_scale[1] * text_size))
        self.name = str(name)

        self.image = pygame.Surface(
            (box.image.get_width() - int(18 * self.screen_scale[0]),
             int((text_size + 4) * self.screen_scale[1])))  # black corner
        self.image.fill((0, 0, 0))
        self.selected_image = self.image.copy()
        self.selected = False

        # White body square
        small_image = pygame.Surface(
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


class MapOptionBox(UIMenu):
    def __init__(self, pos, image):
        self._layer = 13
        UIMenu.__init__(self, player_interact=False)
        self.image = image.copy()

        self.font = pygame.font.Font(self.ui_font["main_button"], int(20 * self.screen_scale[1]))

        text_surface = self.font.render("Night Battle", True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 5))
        self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect(topleft=pos)


class MapPreview(UIMenu, BattleMap):
    def __init__(self, pos):
        UIMenu.__init__(self, player_interact=False)
        BattleMap.__init__(self)

        self.pos = pos

        self.image = pygame.Surface((450 * self.screen_scale[0], 450 * self.screen_scale[1]))
        self.leader_dot = {team: {True: None, False: None} for team in self.team_colour.keys()}

        self.map_scale_width = 1
        self.map_scale_height = 1

        leader_dot = pygame.Surface((10 * self.screen_scale[0], 10 * self.screen_scale[1]))  # dot for team unit
        leader_dot.fill((0, 0, 0))  # black corner
        leader_colour_dot = pygame.Surface((8 * self.screen_scale[0], 8 * self.screen_scale[1]))
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

        new_base_map = pygame.transform.scale(base_map, (300, 300))
        new_feature_map = pygame.transform.scale(feature_map, (300, 300))
        new_height_map = topology_map_creation(pygame.transform.scale(height_map, (300, 300)), 4)

        self.map_scale_width = base_map.get_width() / (450 * self.screen_scale[0])
        self.map_scale_height = base_map.get_height() / (450 * self.screen_scale[1])

        map_image = pygame.Surface((300, 300))
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
                rect = pygame.Rect(row_pos, col_pos, 1, 1)
                map_image.fill(new_colour, rect)

        map_image.blit(new_height_map, map_image.get_rect(topleft=(0, 0)))

        map_image = pygame.transform.scale(map_image, (450 * self.screen_scale[0], 450 * self.screen_scale[1]))
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
                        pygame.draw.circle(self.image, colour,
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
                        scaled_pos = pygame.Vector2(pos[0] * ((450 * self.screen_scale[0]) / 1000),
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
            except (nx.exception.NetworkXError, ZeroDivisionError) as b:  # has only one leader
                pos = {selected: (self.image.get_width() / 2, self.image.get_width() / 2)}
                image_size = (self.image.get_width() / 2, self.image.get_height() / 2)

            for unit in pos:
                for unit_index, icon in enumerate(preview_unit):
                    if unit_index == unit:
                        image = pygame.transform.smoothscale(icon.portrait, image_size)
                        self.node_rect[unit] = image.get_rect(center=pos[unit])
                        self.image.blit(image, self.node_rect[unit])
                        break

            for unit in pos:
                if type(unit_data[unit]["Temp Leader"]) is int:
                    line_width = int(self.image.get_width() / 100)
                    if line_width < 1:
                        line_width = 1
                    pygame.draw.line(self.image, (0, 0, 0), self.node_rect[unit_data[unit]["Temp Leader"]].midbottom,
                                     self.node_rect[unit].midtop, width=line_width)


class TextPopup(UIMenu):
    def __init__(self):
        self._layer = 15
        UIMenu.__init__(self, player_interact=False)
        self.font_size = int(24 * self.screen_scale[1])
        self.font = pygame.font.Font(self.ui_font["main_button"], self.font_size)
        self.pos = (0, 0)
        self.text_input = ""

    def popup(self, cursor_rect, text_input, width_text_wrapper=0):
        """Pop out text box with input text list in multiple line, one item equal to one line"""
        if self.text_input != text_input:
            self.text_input = text_input
            if type(text_input) == str:
                self.text_input = [text_input]

            text_surface = []
            if width_text_wrapper:
                max_height = 0
                max_width = 0
                for text in self.text_input:
                    text_image = pygame.Surface((width_text_wrapper, (len(text) * (self.font_size ** 2 / 1.3) / width_text_wrapper)))
                    text_image.fill((255, 255, 255))
                    print(text_image)
                    make_long_text(text_image, text, (self.font_size, self.font_size), self.font)
                    text_surface.append(text_image)
                    max_width = text_image.get_width()
                    max_height += text_image.get_height() + self.font_size + int(self.font_size / 5)
            else:
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
        self.image = pygame.Surface(self.rect[2:], pygame.SRCALPHA)
        self.image.fill("#302d2ce0")

    def update(self):
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.image = pygame.Surface(self.rect[2:], pygame.SRCALPHA)
        self.image.fill("#bbbbaabb")

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

    def __init__(self, origin, pivot, size, items, parent, item_size):

        from engine.game.game import Game
        from engine.utility import load_image
        game = Game.game

        UIMenu.__init__(self)
        self.pivot = pivot
        self.origin = origin
        self.frame = load_image(game.module_dir, (1, 1), "list_frame.png", ("ui", "mainmenu_ui"))
        self.scroll_box_frame = load_image(game.module_dir, (1, 1), "scroll_box_frame.png", ("ui", "mainmenu_ui"))

        self.item_size = item_size

        self.relative_size_inside_container = size

        self.items = items

        self.in_scroll_box = False
        self.hold_scroll_box = None
        self.selected_index = None

        self.rect = self.get_adjusted_rect_to_be_inside_container(parent)

        self.scroll_bar_height = self.rect[3] - 12
        self.scroll_box_height = int(self.scroll_bar_height * (item_size / len(self.items)))
        self.scroll_step_height = (self.scroll_bar_height - self.scroll_box_height) / self.get_number_of_items_outside_visible_list()

        self.scroll_box = make_image_by_frame(self.scroll_box_frame, (14, self.scroll_box_height))
        self.scroll_box_index = 0
        self.image = self.get_refreshed_image()

    def get_number_of_items_outside_visible_list(self):
        r = len(self.items) - self.item_size
        if r <= 0:
            raise Exception("At the moment ListUI can only handle list that have enough items to require a scroll bar")
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
        font = pygame.font.Font(self.ui_font["main_button"], 18)
        item_height = self.get_item_height()

        # draw items
        for i in range(self.item_size):
            item_index = i + self.scroll_box_index
            if item_index == self.selected_index or item_index == self.items.get_highlighted_index():

                color = "#181617"
                if item_index == self.items.get_highlighted_index():
                    color = "#551617"

                pygame.draw.rect(self.image, color, (6, 6 + i * item_height, size[0] - 25, item_height))
            self.image.blit(font.render(self.items[item_index], True, (255 if item_index == self.selected_index else 178,) * 3),
                            (20, item_height // 2 + 6 - 9 + i * item_height))

        # draw scroll bar
        pygame.draw.rect(self.image, "black", self.get_scroll_bar_rect())

        # draw scroll box
        scroll_box_rect = self.get_scroll_box_rect()
        self.image.blit(self.scroll_box, scroll_box_rect)
        if self.in_scroll_box or self.hold_scroll_box is not None:
            pygame.draw.rect(self.image, (220, 190, 110) if self.hold_scroll_box is not None else (150,) * 3, scroll_box_rect, 1)

        return self.image

    def get_scroll_bar_rect(self):
        return pygame.Rect(self.rect[2] - 18, 6, 14, self.scroll_bar_height)

    def get_scroll_box_rect(self):
        return pygame.Rect(self.rect[2] - 18, self.scroll_box_index * self.scroll_step_height + 6, *self.scroll_box.get_size())

    def update(self):

        mouse_pos = self.cursor.pos
        relative_mouse_pos = [mouse_pos[i] - self.rect[i] for i in range(2)]

        size = tuple(map(int, self.rect[2:]))
        self.mouse_over = False
        self.selected_index = None
        mljd = self.cursor.is_select_just_down
        mld = self.cursor.is_select_down

        # detect if in list or over scroll box
        self.in_scroll_box = False
        in_list = False
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if self.get_scroll_bar_rect().collidepoint(relative_mouse_pos):
                if self.get_scroll_box_rect().collidepoint(relative_mouse_pos):
                    self.in_scroll_box = True
            else:
                in_list = True

        # scroll box drag handler
        if not mld:
            self.hold_scroll_box = None
        if mljd and self.in_scroll_box:
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
        if in_list and mljd and self.selected_index is not None:
            self.items.on_select(self.selected_index, self.items[self.selected_index])

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
