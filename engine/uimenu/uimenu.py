import networkx as nx
import pygame
import pygame.transform
import pyperclip
from functools import lru_cache

from engine import utility


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

    css = corner_side_size = (frame.get_size()[0]-1)//2

    image = pygame.Surface(final_size)

    # background color
    image.fill(frame.get_at((css, css)))

    # corners
    image.blit(frame, (0, 0), (0, 0, css, css))
    image.blit(frame, (0, fs[1]-css), (0, css+1, css, css*2+1))
    image.blit(frame, (fs[0]-css, 0), (css+1, 0, css*2+1, css))
    image.blit(frame, (fs[0]-css, fs[1]-css), (css+1, css+1, css*2+1, css*2+1))

    # sides
    for x in range(css, fs[0]-css):
        image.blit(frame, (x, 0), (css, 0, 1, css))
        image.blit(frame, (x, fs[1]-css), (css, css+1, 1, css*2+1))
    for y in range(css, fs[1]-css):
        image.blit(frame, (0, y), (0, css, css, 1))
        image.blit(frame, (fs[0]-css, y), (css+1, css, css*2+1, 1))

    return image


class UIMenu(pygame.sprite.Sprite):
    def __init__(self):
        """
        Parent class for all menu user interface
        """
        from engine.game.game import Game
        self.screen_scale = Game.screen_scale
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.font_dir = Game.font_dir
        self.ui_font = Game.ui_font
        self.screen_size = Game.screen_size
        self.localisation = Game.localisation
        pygame.sprite.Sprite.__init__(self)


class Cursor(UIMenu):
    def __init__(self, images):
        """Game cursor"""
        self._layer = 100  # as high as possible, always blit last
        UIMenu.__init__(self)
        self.images = images
        self.image = images["normal"]
        self.pos = (0, 0)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, mouse_pos, mouse_left_up, mouse_left_down, *args):
        """Update cursor position based on mouse position"""
        self.pos = mouse_pos
        self.rect.topleft = self.pos

    def change_image(self, image_name):
        """Change cursor image to whatever input name"""
        self.image = self.images[image_name]
        self.rect = self.image.get_rect(topleft=self.pos)


class EscBox(UIMenu):
    images = {}
    screen_rect = None

    def __init__(self):
        self._layer = 24
        UIMenu.__init__(self)
        self.pos = (self.screen_rect.width / 2, self.screen_rect.height / 2)
        self.mode = "menu"  # Current menu mode
        self.image = self.images[self.mode]
        self.rect = self.image.get_rect(center=self.pos)

    def change_mode(self, mode):
        """Change between 0 menu, 1 option, 2 encyclopedia mode"""
        self.mode = mode
        if self.mode != "encyclopedia":
            self.image = self.images[mode]
            self.rect = self.image.get_rect(center=self.pos)


class EscButton(UIMenu, pygame.sprite.Sprite):
    def __init__(self, images, pos, text="", text_size=16):
        self._layer = 25
        UIMenu.__init__(self)
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.images = [image.copy() for image in list(images.values())]
        self.text = text
        self.font = pygame.font.Font(self.ui_font["main_button"], text_size)

        if text != "":  # blit menu text into button image
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(text_surface, text_rect)  # button idle image
            self.images[1].blit(text_surface, text_rect)  # button mouse over image
            self.images[2].blit(text_surface, text_rect)  # button click image

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.event = False


class SliderMenu(UIMenu, pygame.sprite.Sprite):
    def __init__(self, bar_images, button_images, pos, value):
        """
        Slider UI that let player click or drag the setting point in the bar
        :param bar_images: List of box image and slider box
        :param button_images: List of button or ball clicked/non-clicked image
        :param pos: Position of the ui sprite
        :param value: Value of the setting
        """
        self._layer = 25
        UIMenu.__init__(self)
        pygame.sprite.Sprite.__init__(self, self.containers)
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

    def player_input(self, mouse_pos, value_box, forced_value=False):
        """
        Update slider value and position
        :param mouse_pos: Cursor position
        :param value_box: UI box that show number value
        :param forced_value: forced
        :return:
        """
        if not forced_value:
            self.mouse_value = mouse_pos[0]
            if self.mouse_value > self.max_value:
                self.mouse_value = self.max_value
            elif self.mouse_value < self.min_value:
                self.mouse_value = self.min_value
            self.value = (self.mouse_value - self.min_value) / 2
        else:  # for revert, cancel or esc in the option menu
            self.value = mouse_pos
        self.mouse_value = (self.slider_size * self.value / 100) + self.difference
        self.image = self.base_image.copy()
        button_rect = self.button_image_list[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.button_image, button_rect)
        value_box.change_value(self.value)


class InputUI(UIMenu):
    def __init__(self, image, pos):
        self._layer = 30
        UIMenu.__init__(self)

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
        UIMenu.__init__(self)
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
        UIMenu.__init__(self)

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


class MenuButton(UIMenu, pygame.sprite.Sprite):
    def __init__(self, images, pos, updater=None, key_name="", size=28, layer=1):
        self._layer = layer
        UIMenu.__init__(self)
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.button_normal_image = images[0].copy()
        self.button_over_image = images[1].copy()
        self.button_click_image = images[2].copy()
        self.updater = updater

        self.font = pygame.font.Font(self.ui_font["main_button"], int(size * self.screen_scale[1]))
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
        self.event = False

    def update(self, mouse_pos, mouse_up, mouse_down, *args):
        if not self.updater or self in self.updater:
            self.mouse_over = False
            self.image = self.button_normal_image
            if self.rect.collidepoint(mouse_pos):
                self.mouse_over = True
                self.image = self.button_over_image
                if mouse_up:
                    self.event = True
                    self.image = self.button_click_image

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
            return pygame.rect.Rect(*[container.get_rect()[i] - (self.get_size()[i] * (origin[i]+1)) // 2 + (pivot[i] + 1) * container.get_rect()[i+2] // 2 for i in range(2)], *self.get_size())
        else:
            size = [ container.get_size()[i] * rsic[i] for i in range(2) ]
            return pygame.rect.Rect(*[container.get_rect()[i] - (size[i] * (origin[i]+1)) // 2 + (pivot[i] + 1) * container.get_rect()[i+2] // 2 for i in range(2)], *size)


class BrownMenuButton(UIMenu, Containable):

    @classmethod
    @lru_cache
    def make_buttons(cls, size):
        from engine.game.game import Game
        from engine.utility import load_image
        game = Game.game

        frame = load_image(game.module_dir, (1, 1), "new_button.png", ("ui", "mainmenu_ui"))

        normal_button = make_image_by_frame(frame, size)

        # hover button
        hover_button = normal_button.copy()
        pygame.draw.rect(hover_button, "#CCFF77", hover_button.get_rect(), 1)

        return (normal_button, hover_button)

    def get_relative_size_inside_container(self):
        return (.5,.1)


    def __init__(self, pos, key_name="", width=200, parent=None):
        UIMenu.__init__(self)
        self.pos = pos
        self.parent = parent
        self.key_name = key_name
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.mouse_over = False
        self.event = False
        self.refresh()

    def refresh(self):
        key_name = self.key_name
        images = self.make_buttons(size=tuple(self.rect[2:]))
        button_normal_image = images[0].copy()
        button_over_image = images[1].copy()
        font = pygame.font.Font(self.ui_font["main_button"], 17)

        # draw text into the button images
        text = self.localisation.grab_text(key=("ui", key_name))
        text_surface = font.render(text, True, (200, 180, 200))
        text_rect = text_surface.get_rect(center=button_normal_image.get_rect().center)
        button_normal_image.blit(text_surface, text_rect)
        button_over_image.blit(text_surface, text_rect)

        self.image = button_normal_image
        if self.mouse_over:
            self.image = button_over_image

    def get_relative_position_inside_container(self):
        return {
            "origin": (0, 0),
            "pivot": self.pos,
        }

    def update(self, mouse_pos, mouse_up, mouse_down, *args):
        self.mouse_over = False
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                self.event = True

        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.refresh() 


    def get_size(self):
        return self.image.get_size()

    def change_state(self, text):
        pass


class OptionMenuText(UIMenu):
    def __init__(self, pos, text, text_size):
        text_render = utility.text_render

        UIMenu.__init__(self)
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
        UIMenu.__init__(self)
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


class MapTitle(UIMenu):
    def __init__(self, pos):
        UIMenu.__init__(self)

        self.font = pygame.font.Font(self.ui_font["name_font"], int(70 * self.screen_scale[1]))
        self.pos = pos
        self.name = ""
        text_surface = self.font.render(str(self.name), True, (0, 0, 0))
        self.image = pygame.Surface((int(text_surface.get_width() + (20 * self.screen_scale[0])),
                                     int(text_surface.get_height() + (20 * self.screen_scale[1]))))

    def change_name(self, name):
        self.name = name
        text_surface = self.font.render(str(self.name), True, (0, 0, 0))
        self.image = pygame.Surface((int(text_surface.get_width() + (20 * self.screen_scale[0])),
                                     int(text_surface.get_height() + (20 * self.screen_scale[1]))))
        self.image.fill((0, 0, 0))

        white_body = pygame.Surface((text_surface.get_width(), text_surface.get_height()))
        white_body.fill((239, 228, 176))
        white_rect = white_body.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(white_body, white_rect)

        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(midtop=self.pos)


class TeamCoa(UIMenu, pygame.sprite.Sprite):
    def __init__(self, coa_size, pos, coa_images, team, team_colour, name):
        UIMenu.__init__(self)
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.selected = False
        self.coa_size = coa_size
        self.selected_image_base = pygame.Surface((self.coa_size[0] * 2.5, self.coa_size[1]))
        self.not_selected_image_base = self.selected_image_base.copy()
        self.not_selected_image_base.fill((0, 0, 0))  # black border when not selected
        self.selected_image_base.fill((255, 255, 255))  # white border when selected

        team_body = pygame.Surface((self.selected_image_base.get_width() * 0.95,
                                    self.selected_image_base.get_height() * 0.95))
        team_body.fill(team_colour)
        white_rect = team_body.get_rect(
            center=(self.selected_image_base.get_width() / 2, self.selected_image_base.get_height() / 2))
        self.not_selected_image_base.blit(team_body, white_rect)
        self.selected_image_base.blit(team_body, white_rect)

        self.coa_images = coa_images
        self.change_coa(coa_images, name)

        self.image = self.not_selected_image
        self.rect = self.image.get_rect(center=pos)
        self.team = team

    def change_select(self, selected):
        self.selected = selected
        if self.selected:
            self.image = self.selected_image
        else:
            self.image = self.not_selected_image

    def change_coa(self, coa_images, name):
        self.coa_images = coa_images
        text_render = utility.text_render

        self.not_selected_image = self.not_selected_image_base.copy()
        self.selected_image = self.selected_image_base.copy()

        # Coat of arm image to image
        small_coa_pos = [int(self.coa_size[0] * 0.2), int(self.coa_size[1] * 0.2)]
        for index, image in enumerate(self.coa_images.values()):
            if image:
                if index == 0:  # first one as main faction coa
                    coa_image = pygame.transform.smoothscale(image, (
                        int(self.coa_size[0] * 0.65), int(self.coa_size[1] * 0.65)))
                    coa_rect = coa_image.get_rect(
                        midtop=(self.selected_image.get_width() / 2, self.coa_size[1] * 0.05))
                else:
                    coa_image = pygame.transform.smoothscale(image,
                                                             (int(self.coa_size[0] * 0.3), int(self.coa_size[1] * 0.3)))
                    coa_rect = coa_image.get_rect(center=small_coa_pos)
                    small_coa_pos[1] += int(self.coa_size[1] * 0.3)
                    if index % 3 == 0:
                        small_coa_pos = [small_coa_pos[0] + int(self.coa_size[0] * 0.4), int(self.coa_size[1] * 0.2)]
                    if index == 6:
                        small_coa_pos[0] = int(self.coa_size[0] * 1.8)
                self.not_selected_image.blit(coa_image, coa_rect)
                self.selected_image.blit(coa_image, coa_rect)

        # Faction name to image
        self.name = name
        font_size = int(self.coa_size[1] / 5)
        font = pygame.font.Font(self.ui_font["name_font"], font_size)
        text_surface = text_render(str(self.name), font, pygame.Color("black"))
        text_rect = text_surface.get_rect(
            center=(int(self.selected_image.get_width() / 2), self.selected_image.get_height() - font_size))
        self.not_selected_image.blit(text_surface, text_rect)
        self.selected_image.blit(text_surface, text_rect)
        self.change_select(True)


class ArmyStat(UIMenu):
    def __init__(self, pos, image):
        self._layer = 1
        UIMenu.__init__(self)
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

    def add_army_stat(self, troop_number, leader_name):
        """troop_number need to be in list format as follows:[total, melee infantry, range infantry,
        cavalry, range cavalry]"""
        self.image = self.base_image.copy()

        text_surface = self.font.render(str(leader_name), True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 10, self.image.get_height() / 8))
        self.image.blit(text_surface, text_rect)

        for index, text in enumerate(troop_number):
            text = str(text).replace("[", "").replace("]", "").split(",")
            text = str([utility.minimise_number_text(item) for item in text]).replace("'", "").replace("[", "").replace(
                "]", "").replace(",", " +")
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=self.type_number_pos[index])
            self.image.blit(text_surface, text_rect)

    def add_preview_model(self, model, coa):
        self.image = self.base_image.copy()
        new_coa = pygame.transform.smoothscale(coa, (200 * self.screen_scale[0],
                                                     200 * self.screen_scale[1]))
        rect = new_coa.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(new_coa, rect)
        rect = model.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(model, rect)


class ListBox(UIMenu):
    def __init__(self, pos, image, layer=14):
        self._layer = layer
        UIMenu.__init__(self)
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
    def __init__(self, pos, image, mode):
        self._layer = 13
        UIMenu.__init__(self)
        self.image = image.copy()

        self.font = pygame.font.Font(self.ui_font["main_button"], int(20 * self.screen_scale[1]))

        # Observation mode option text
        text_surface = self.font.render("Observation Mode", True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 5))
        self.image.blit(text_surface, text_rect)

        if mode == 1:  # custom map option
            text_surface = self.font.render("Night Battle", True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 2.5))
            self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect(topright=pos)


class MapPreview(UIMenu):
    terrain_colour = None
    feature_colour = None
    battle_map_colour = None
    colour = None
    selected_colour = None

    def __init__(self, pos):
        UIMenu.__init__(self)

        self.pos = pos

        self.image = pygame.Surface((450 * self.screen_scale[0], 450 * self.screen_scale[1]))
        self.leader_dot = {team: {True: None, False: None} for team in self.colour.keys()}

        self.map_scale_width = 1
        self.map_scale_height = 1

        leader_dot = pygame.Surface((10 * self.screen_scale[0], 10 * self.screen_scale[1]))  # dot for team unit
        leader_dot.fill((0, 0, 0))  # black corner
        leader_colour_dot = pygame.Surface((8 * self.screen_scale[0], 8 * self.screen_scale[1]))
        rect = leader_dot.get_rect(topleft=(2 * self.screen_scale[0], 2 * self.screen_scale[1]))

        for team, colour in self.colour.items():
            new_dot = leader_colour_dot.copy()
            new_dot.fill(colour)
            add_dot = leader_dot.copy()
            add_dot.blit(new_dot, rect)
            self.leader_dot[team][False] = add_dot

        for team, colour in self.selected_colour.items():
            new_selected_dot = leader_colour_dot.copy()
            new_selected_dot.fill(colour)
            new_selected_dot.fill(colour)
            add_dot = leader_dot.copy()
            add_dot.blit(new_selected_dot, rect)
            self.leader_dot[team][True] = add_dot

        self.rect = self.image.get_rect(midtop=self.pos)

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
                        colour = self.colour[team]
                        if pos == camp_selected:
                            colour = self.selected_colour[team]
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
        self.rect = self.image.get_rect(midtop=self.pos)


class OrgChart(UIMenu):
    def __init__(self, image, pos):
        UIMenu.__init__(self)
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


class SelectedPresetBorder(UIMenu):
    def __init__(self, size):
        self._layer = 16
        UIMenu.__init__(self)
        self.image = pygame.Surface((size[0] + 1, size[1] + 1), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (203, 176, 99), (0, 0, self.image.get_width(), self.image.get_height()), 3)
        self.rect = self.image.get_rect(topleft=(0, 0))

    def change_pos(self, pos):
        self.rect = self.image.get_rect(topleft=pos)


class FilterBox(UIMenu):
    def __init__(self, pos, image):
        self._layer = 10
        UIMenu.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)


class TextPopup(UIMenu):
    def __init__(self):
        self._layer = 15
        UIMenu.__init__(self)
        self.font_size = int(24 * self.screen_scale[1])
        self.font = pygame.font.Font(self.ui_font["main_button"], self.font_size)
        self.pos = (0, 0)
        self.text_input = ""

    def pop(self, pos, text_input, width_text_wrapper=0):
        """Pop out text box with input text list in multiple line, one item equal to one line"""
        if self.pos != pos or self.text_input != text_input:
            self.text_input = text_input
            if type(text_input) == str:
                self.text_input = [text_input]
            self.pos = pos

            text_surface = []
            if width_text_wrapper:
                for text in self.text_input:
                    text_image = pygame.Surface((width_text_wrapper, len(text) / width_text_wrapper * int(self.font_size * self.screen_scale[1])))
                    utility.make_long_text(text_image, text,
                                           (int(self.font_size * self.screen_scale[0]), int(self.font_size * self.screen_scale[1])),
                                           self.font)
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
            if self.pos[0] + self.image.get_width() > self.screen_size[0]:  # exceed screen width
                self.rect = self.image.get_rect(topright=self.pos)
                if self.pos[1] + self.image.get_height() > self.screen_size[1]:  # also exceed height screen
                    self.rect = self.image.get_rect(bottomright=self.pos)
            elif self.pos[1] - self.image.get_height() < 0:  # exceed top screen
                self.rect = self.image.get_rect(topleft=self.pos)
            else:
                self.rect = self.image.get_rect(bottomleft=self.pos)


class BoxUI(UIMenu, Containable, Container):

    def __init__(self, size, parent):
        UIMenu.__init__(self)
        self.parent = parent
        self.size = size
        self._layer = -1  # NOTE: not sure if this is good since underscore indicate it is a private variable but it works for now
        self.pos = (0, 0)
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.image = pygame.Surface(self.rect[2:])
        self.image.fill("#222a2e")

    def update(self, *args):
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.image = pygame.Surface(self.rect[2:])
        self.image.fill("#222a2e")



    def get_relative_size_inside_container(self):
        return (0.3,0.5)

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

    def __init__(self, origin, pivot, size, items, parent, on_click):

        from engine.game.game import Game
        from engine.utility import load_image
        game = Game.game

        UIMenu.__init__(self)
        self.pivot = pivot
        self.origin = origin
        self.frame = load_image(game.module_dir, (1, 1), "list_frame.png", ("ui", "mainmenu_ui"))
        self.scroll_box_frame = load_image(game.module_dir, (1, 1), "scroll_box_frame.png", ("ui", "mainmenu_ui"))

        self.scroll_box = make_image_by_frame(self.scroll_box_frame, (14,40))
        self.on_click = on_click
        self.scroll_box_down = 0

        self.click_ready = True
        self.size = size
        self.items = items
        self.hold_scroll_box = False

        self.selected_index = None
        self.image = self.get_refreshed_image()
        self.rect = self.get_adjusted_rect_to_be_inside_container(parent)

    def get_refreshed_image(self):
        self.image = make_image_by_frame(self.frame, self.size)
        font = pygame.font.Font(self.ui_font["main_button"], 18)


        if self.selected_index is not None:
            si = self.selected_index
            pygame.draw.rect(self.image, "#181617", (4, si*36+11, self.size[0]-8, 36))

        for e, item in enumerate(self.items):
            self.image.blit(font.render(item, True, ( 255 if e == self.selected_index else 178,)*3), (20, 20+e*36))


        pygame.draw.rect(self.image, "black", (self.size[0]-18,6,14,self.size[1]-12))

        self.image.blit(self.scroll_box,(self.size[0]-18,self.scroll_box_down+6))

        return self.image


    def update(self, mouse_pos, mouse_up, mouse_down, *args):

        print(mouse_up, mouse_down, args)

        self.mouse_over = False
        self.selected_index = None
        if mouse_up:
            self.click_ready = True
            self.hold_scroll_box = False
        if self.rect.collidepoint(mouse_pos):
            if mouse_pos[0] < self.rect[0] + self.rect[2] - 18:
                self.selected_index = (mouse_pos[1]-11)//36
                self.mouse_over = True
        if self.click_ready and mouse_down and self.selected_index is not None:
            self.click_ready = False
            self.on_click(self.selected_index, self.items[self.selected_index])
        if self.rect.collidepoint(mouse_pos):
            if self.click_ready and mouse_down and mouse_pos[0] >= self.rect[0] + self.rect[2] - 18:
                self.click_ready = False
                self.hold_scroll_box = True

        if self.hold_scroll_box:
            self.scroll_box_down = mouse_pos[1]-self.rect[1]-22


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
