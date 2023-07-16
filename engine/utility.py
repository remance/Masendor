import csv
import datetime
import hashlib
import os
import re
from ast import literal_eval
from inspect import stack
from math import cos, sin, atan2, degrees, radians
from pathlib import Path

import pygame
import pygame.freetype
from PIL import Image, ImageOps
from pygame import Vector2, Color, Surface
from pygame.mixer import Sound
from pygame.transform import smoothscale

accept_image_types = ("png", "jpg", "jpeg", "svg", "gif", "bmp")
direction_angle = {"r_side": radians(90), "l_side": radians(270), "back": radians(180),
                   "front": radians(0), "r_sidedown": radians(135), "l_sidedown": radians(225),
                   "r_sideup": radians(45), "l_sideup": radians(315)}


def empty_method(self, *args):
    if hasattr(self, 'error_log'):
        error_text = "{0} -- {1}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                           "Empty method is called") + \
                     str(stack()[1][1]) + "At Line" + str(stack()[1][2]) + ":" + \
                     str(stack()[1][3])
        # print(error_text)
        self.error_log.write(error_text)


def empty_function(*args):
    """Empty function that does nothing"""
    pass


def change_group(item, group, change):
    """Change group of the item, use for multiple change in loop"""
    if change == "add":
        group.add(item)
    elif change == "remove":
        group.remove(item)


def keyboard_mouse_press_check(button_type, button, is_button_just_down, is_button_down, is_button_just_up, ):
    """
    Check for button just press, holding, and release for keyboard or mouse
    :param button_type: pygame.key, pygame.mouse, or pygame.
    :param button: button index
    :param is_button_just_down: button is just press last update
    :param is_button_down: button is pressing after first update
    :param is_button_just_up: button is just release last update
    :return: new state of is_button_just_down, is_button_down, is_button_just_up
    """
    if button_type.get_pressed()[button]:  # press left click
        if not is_button_just_down:
            if not is_button_down:  # fresh press
                is_button_just_down = True
        else:  # already press in previous frame, now hold until release
            is_button_just_down = False
            is_button_down = True
    else:  # no longer press
        is_button_just_down = False
        if is_button_just_down or is_button_down:
            is_button_just_up = True
            is_button_just_down = False
            is_button_down = False
        elif is_button_just_up:
            is_button_just_up = False
    return is_button_just_down, is_button_down, is_button_just_up


def load_image(directory, screen_scale, file, subfolder="", no_alpha=False):
    """
    loads an image and prepares it for game
    :param directory: Directory folder path
    :param screen_scale: Resolution scale of game
    :param file: File name
    :param subfolder: List of sub1_folder path
    :param no_alpha: Indicate if surface require alpha or not
    :return: Pygame Surface
    """
    new_subfolder = subfolder
    if isinstance(new_subfolder, list) or isinstance(new_subfolder, tuple):
        new_subfolder = ""
        for folder in subfolder:
            new_subfolder = os.path.join(new_subfolder, folder)
    this_file = os.path.join(directory, new_subfolder, file)
    if not no_alpha:
        surface = pygame.image.load(this_file).convert_alpha()
    else:
        surface = pygame.image.load(this_file).convert()
    if screen_scale[0] != 1 and screen_scale[1] != 1:  # scale to screen scale
        surface = smoothscale(surface, (surface.get_width() * screen_scale[0],
                                        surface.get_height() * screen_scale[1]))
    return surface


def load_images(directory, screen_scale=(1, 1), subfolder=(), load_order=False, return_order=False,
                key_file_name_readable=False, no_alpha=False):
    """
    loads all images(only png files) in folder
    :param directory: Directory folder path
    :param screen_scale: Resolution scale of game
    :param subfolder: List of sub1_folder path
    :param load_order: Using loadorder list file to create ordered list
    :param return_order: Return the order
    :param key_file_name_readable: Convert key name from file name into data readable
    :param no_alpha: Indicate if all loaded surfaces require alpha or not
    :return: Dict of loaded and scaled images as Pygame Surface
    """
    images = {}
    dir_path = directory
    for folder in subfolder:
        dir_path = os.path.join(dir_path, folder)

    try:
        if load_order:  # load in the order of load_order file
            load_order_file = open(os.path.join(dir_path, "load_order.txt"), "r")
            load_order_file = literal_eval(load_order_file.read())
        else:  # load every file
            load_order_file = [f for f in os.listdir(dir_path) if f.endswith(".png")]  # read all file
            try:  # sort file name if all in number only
                load_order_file.sort(
                    key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
            except TypeError:  # has character in file name
                pass
        for file in load_order_file:
            file_name = file
            if "." in file_name:  # remove extension from name
                file_name = file.split(".")[:-1]
                file_name = "".join(file_name)
            if key_file_name_readable:
                file_name = filename_convert_readable(file_name)
            images[file_name] = load_image(directory, screen_scale, file, subfolder=dir_path, no_alpha=no_alpha)

        if return_order is False:
            return images
        else:  # return order of the file as list
            load_order_file = [int(name.replace(".png", "")) for name in load_order_file]
            return images, load_order_file
    except FileNotFoundError as b:
        print(b)
        return images


def filename_convert_readable(filename, revert=False):
    if revert:
        new_filename = filename.replace(" ", "-").lower()  # replace space with - and make name lowercase
    else:
        if "-" in filename:
            new_filename = filename.split("-")
        else:
            new_filename = [filename]

        for index, item in enumerate(new_filename):
            new_filename[index] = item.capitalize()  # capitalise each word divided by -

        new_filename = " ".join(new_filename)  # replace - with space

    return new_filename


def convert_str_time(event):
    """
    Convert text string of time to datetime
    :param event: Event must be in string format
    """
    for index, item in enumerate(event):
        new_time = datetime.datetime.strptime(item[1], "%H:%M:%S").time()
        new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
        event[index][1] = new_time
        event[index] = tuple(event[index])


def csv_read(main_dir, file, subfolder=(), output_type="dict", header_key=False, dict_value_return_as_str=None):
    """
    Read csv file
    :param main_dir: Game directory folder path
    :param file: File name
    :param subfolder: Array of sub1_folder path
    :param output_type: Type of returned object, either dict or list
    :param header_key: Use header as dict key or not
    :param dict_value_return_as_str: Returned dict value is stored as string instead of list
    :return:
    """
    return_output = {}
    if output_type == "list":
        return_output = []

    folder_dir = ""
    for folder in subfolder:
        folder_dir = os.path.join(folder_dir, folder)
    folder_dir = os.path.join(folder_dir, file)
    folder_dir = os.path.join(main_dir, folder_dir)
    try:
        with open(folder_dir, encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row_index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None):
                        row[n] = int(i)
                    elif re.search("[a-zA-Z]", i) is None and "." in i and "," not in i:
                        row[n] = float(i)
                if output_type == "dict":  # return as dict
                    if header_key:
                        if row_index > 0:  # skip header row
                            return_output[row[0]] = {header[index + 1]: item for index, item in enumerate(row[1:])}
                    else:
                        if dict_value_return_as_str:
                            return_output[row[0]] = ",".join(row[1:])
                        else:
                            return_output[row[0]] = row[1:]
                elif output_type == "list":  # return as list
                    return_output.append(row)
            edit_file.close()
    except FileNotFoundError as b:
        print(b)
    return return_output


def lore_csv_read(edit_file, input_dict):
    rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
    rd = [row for row in rd]
    for index, row in enumerate(rd[1:]):
        for n, i in enumerate(row):
            if i.isdigit():
                row[n] = int(i)
        input_dict[row[0]] = [stuff for index, stuff in enumerate(row[1:])]
        while len(input_dict[row[0]]) > 2 and input_dict[row[0]][-1] == "":  # keep remove last empty text
            input_dict[row[0]] = input_dict[row[0]][:-1]
        input_dict[row[0]] = {rd[0][index + 1]: value for index, value in enumerate(input_dict[row[0]])}


def load_sound(main_dir, file):
    """
    Load sound file
    :param main_dir: Game directory folder path
    :param file: File name
    :return: Pygame Sound
    """
    file = os.path.join(main_dir, "data", "sound", file)
    sound = Sound(file)
    return sound


def minimise_number_text(text):
    num_text = int(text)
    if num_text >= 1000000:
        return str(round(num_text / 1000000, 1)) + "M"
    elif num_text >= 1000:
        return str(round(num_text / 1000, 1)) + "K"
    else:
        return str(num_text)


def edit_config(section, option, value, filename, config):
    """
    Edit config file at specific section
    :param section: Section name
    :param option: Part that will be changed
    :param value: Changed value in string text
    :param filename: Config file name
    :param config: Config object
    :return:
    """
    config.set(section, option, str(value))
    with open(filename, "w") as configfile:
        config.write(configfile)


def make_long_text(surface, text, pos, font, color=Color("black")):
    """
    Blit long text into separate row of text
    :param surface: Input Pygame Surface
    :param text: Text in either list or string format
    :param pos: Starting position
    :param font: Pygame Font
    :param color: Text colour
    """
    if type(text) != list:
        text = [text]
    x, y = pos
    for this_text in text:
        words = [word.split(" ") for word in str(this_text).splitlines()]  # 2D array where each row is a list of words
        space = font.size(" ")[0]  # the width of a space
        max_width = surface.get_width()
        for line in words:
            for word in line:
                word_surface = font.render(word, True, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # reset x
                    y += word_height  # start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # reset x
            y += word_height  # start on new row


def text_render(text, font, gf_colour=Color("black"), o_colour=(255, 255, 255), opx=2):
    """
    Render text with background border
    :param text: Text strings
    :param font: Pygame font
    :param gf_colour: Text colour
    :param o_colour: Background colour
    :param opx: Background colour thickness
    :return: Text surface
    """
    text_surface = font.render(text, True, gf_colour).convert_alpha()
    w = text_surface.get_width() + 2 * opx
    h = font.get_height()

    osurf = Surface((w, h + 2 * opx)).convert_alpha()
    osurf.fill((0, 0, 0, 0))

    surface = osurf.copy()

    osurf.blit(font.render(text, True, o_colour).convert_alpha(), (0, 0))

    for dx, dy in circle_points(opx):
        surface.blit(osurf, (dx + opx, dy + opx))

    surface.blit(text_surface, (opx, opx))

    return surface


def circle_points(r):
    """Calculate text point to add background"""
    circle_cache = {}
    r = int(round(r))
    if r in circle_cache:
        return circle_cache[r]
    x, y, e = r, 0, 1 - r
    circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def make_bar_list(main_dir, screen_scale, list_to_do, menu_image):
    """
    Make a drop down bar list option button
    :param main_dir: Game directory folder path
    :param screen_scale: Resolution scale of game
    :param list_to_do: List of text
    :param menu_image: Menu image that will get drop list
    :return: List of bar button objects
    """
    from engine.uimenu import uimenu
    bar_list = []
    image = load_image(main_dir, screen_scale, "bar_normal.jpg", ("ui", "mainmenu_ui"))
    image2 = load_image(main_dir, screen_scale, "bar_mouse.jpg", ("ui", "mainmenu_ui"))
    image3 = image2
    for index, bar in enumerate(list_to_do):
        bar_image = (image.copy(), image2.copy(), image3.copy())
        bar = uimenu.MenuButton(bar_image, (menu_image.pos[0], menu_image.pos[1] + image.get_height() * (index + 1)),
                                key_name=bar)
        bar_list.append(bar)
    return bar_list


def load_base_button(data_dir, screen_scale):
    return (load_image(data_dir, screen_scale, "idle_button.png", ("ui", "mainmenu_ui")),
            load_image(data_dir, screen_scale, "mouse_button.png", ("ui", "mainmenu_ui")),
            load_image(data_dir, screen_scale, "click_button.png", ("ui", "mainmenu_ui")))


def text_objects(text, font):
    text_surface = font.render(text, True, (200, 200, 200))
    return text_surface, text_surface.get_rect()


def rotation_xy(origin, point, angle):
    """
    Rotate point to the new pos
    :param origin: origin pos
    :param point: target point pos
    :param angle: angle of rotation in radians
    :return: Rotated origin pos
    """
    ox, oy = origin
    px, py = point
    x = ox + cos(angle) * (px - ox) - sin(angle) * (py - oy)
    y = oy + sin(angle) * (px - ox) + cos(angle) * (py - oy)
    return Vector2(x, y)


def set_rotate(self, base_target, convert=True):
    """
    find angle using starting pos and base_target
    :param self: any object with base_pos as position attribute
    :param base_target: pos for target position to rotate to
    :param convert: convert degree for rotation
    :return: new angle
    """
    my_radians = atan2(base_target[1] - self.base_pos[1], base_target[0] - self.base_pos[0])
    new_angle = degrees(my_radians)
    if convert:
        # """upper left and upper right"""
        if -180 <= new_angle < 0:
            new_angle = -new_angle - 90

        # """lower right -"""
        elif 0 <= new_angle <= 90:
            new_angle = -(new_angle + 90)

        # """lower left +"""
        elif 90 < new_angle <= 180:
            new_angle = 270 - new_angle
    return round(new_angle)


def convert_degree_to_360(angle):
    """Convert math.degrees to 360 degree with 0 at the top"""
    return 360 - (angle % 360)


def travel_to_map_border(pos, angle, map_size):
    """
    Find target at border of map based on angle
    :param pos: Starting pos
    :param angle: Angle in radians
    :param map_size: Size of map (width, height)
    :return: target pos on map border
    """
    dx = cos(angle)
    dy = sin(angle)

    if dx < 1.0e-16:  # left border
        y = (-pos[0]) * dy / dx + pos[1]

        if 0 <= y <= map_size[1]:
            return Vector2((0, y))

    if dx > 1.0e-16:  # right border
        y = (map_size[0] - pos[0]) * dy / dx + pos[1]
        if 0 <= y <= map_size[1]:
            return Vector2((map_size[0], y))

    if dy < 1.0e-16:  # top border
        x = (-pos[1]) * dx / dy + pos[0]
        if 0 <= x <= map_size[0]:
            return Vector2((x, 0))

    if dy > 1.0e-16:  # bottom border
        x = (map_size[1] - pos[1]) * dx / dy + pos[0]
        if 0 <= x <= map_size[0]:
            return Vector2((x, map_size[1]))


def crop_sprite(sprite_pic):
    low_x0 = float("inf")  # lowest x0
    low_y0 = float("inf")  # lowest y0
    high_x1 = 0  # highest x1
    high_y1 = 0  # highest y1

    # Find optimal cropped sprite size and center offset
    size = sprite_pic.get_size()
    data = pygame.image.tostring(sprite_pic, "RGBA")  # convert image to string data for filtering effect
    data = Image.frombytes("RGBA", size, data)  # use PIL to get image data
    bbox = data.getbbox()
    if low_x0 > bbox[0]:
        low_x0 = bbox[0]
    if low_y0 > bbox[1]:
        low_y0 = bbox[1]
    if high_x1 < bbox[2]:
        high_x1 = bbox[2]
    if high_y1 < bbox[3]:
        high_y1 = bbox[3]

    center = ((sprite_pic.get_width() / 2), (sprite_pic.get_height() / 2))

    # Crop transparent area only of surface
    size = sprite_pic.get_size()
    sprite_pic = pygame.image.tostring(sprite_pic,
                                       "RGBA")  # convert image to string data for filtering effect
    sprite_pic = Image.frombytes("RGBA", size, sprite_pic)  # use PIL to get image data
    sprite_pic = sprite_pic.crop((low_x0, low_y0, high_x1, high_y1))
    size = sprite_pic.size
    sprite_pic = sprite_pic.tobytes()
    sprite_pic = pygame.image.fromstring(sprite_pic, size,
                                         "RGBA")  # convert image back to a pygame surface

    # Find center offset after crop by finding width and height difference of longer side
    center_x_offset = ((low_x0 + high_x1) / 2) + (((100 - low_x0) - (high_x1 - 100)) / 10)
    center_y_offset = ((low_y0 + high_y1) / 2) + (((100 - low_y0) - (high_y1 - 100)) / 10)
    center_offset = (center[0] - center_x_offset, center[1] - center_y_offset)

    # sprite_pic_new = Surface(size)
    # sprite_pic_new.fill((0,0,0))
    # rect = sprite_pic.get_rect(topleft=(0, 0))
    # sprite_pic_new.blit(sprite_pic, rect)
    return sprite_pic, center_offset


def apply_sprite_colour(surface, colour, colour_list=None, keep_white=True, keep_old_colour=False):
    """Colorise body part sprite"""
    if colour is not None and colour != "None":
        if colour_list is None:
            white_colour = colour
        else:
            if "True" in colour:
                white_colour = colour_list[colour.replace("True ", "")]
            else:
                white_colour = colour_list[colour]
        if "True" not in colour:
            mid_colour = [int(c / 2) for c in white_colour]
        else:  # completely specified colour with no shade
            mid_colour = white_colour

        if keep_white:
            if colour_list is None:
                mid_colour = colour
            else:
                mid_colour = white_colour
            white_colour = "white"

        size = surface.get_size()
        data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
        surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
        alpha = surface.split()[-1]  # save alpha
        surface = surface.convert("L")  # convert to grey scale for colourise
        surface = ImageOps.colorize(surface, black="black", mid=mid_colour, white=white_colour).convert("RGB")
        # if any abs(mean(colour[0], colour[1], colour[2]) > 10) is False:
        surface.putalpha(alpha)  # put back alpha
        surface = surface.tobytes()
        surface = pygame.image.fromstring(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface


def setup_list(item_class, current_row, show_list, item_group, box, ui_class, layer=15):
    """generate list of subsection buttons like in the encyclopedia"""
    from engine.game.game import Game
    screen_scale = Game.screen_scale
    row = 5 * screen_scale[1]
    column = 5 * screen_scale[0]
    pos = box.rect.topleft
    if current_row > len(show_list) - box.max_row_show:
        current_row = len(show_list) - box.max_row_show

    for stuff in item_group:  # remove previous sprite in the group before generate new one
        stuff.kill()
        del stuff
    item_group.empty()

    for index, item in enumerate(show_list):
        if index >= current_row:
            new_item = item_class(box, (pos[0] + column, pos[1] + row), item, layer=layer)
            item_group.add(new_item)  # add new subsection sprite to group
            row += (new_item.font.get_height() * 1.4 * screen_scale[1])  # next row
            if len(item_group) > box.max_row_show:
                break  # will not generate more than space allowed

        ui_class.add(*item_group)


def list_scroll(screen_scale, mouse_scroll_up, mouse_scroll_down, scroll, box, current_row, name_list, group, ui_class,
                layer=15):
    """
    Process scroll of subsection list
    :param screen_scale:
    :param mouse_scroll_up: Mouse scrolling up input
    :param mouse_scroll_down: Mouse scrolling down input
    :param scroll: Scroll object
    :param box: UI box of the subsection list
    :param current_row: Current showing subsection row (the last one)
    :param name_list:
    :param group: Group of the
    :param ui_class:
    :param layer: Layer of the scroll
    :return: New current_row after scrolling
    """
    from engine.uimenu import uimenu
    if mouse_scroll_up:
        current_row -= 1
        if current_row < 0:
            current_row = 0
        else:
            setup_list(uimenu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, row_size=len(name_list))

    elif mouse_scroll_down:
        current_row += 1
        if current_row + box.max_row_show - 1 < len(name_list):
            setup_list(uimenu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, row_size=len(name_list))
        else:
            current_row -= 1
    return current_row


def number_to_minus_or_plus(number):
    """Number should not be 0"""
    if number > 0:
        return "+"
    else:  # assuming number is not 0
        return "-"


def stat_convert(row, n, i, percent_column=(), mod_column=(), list_column=(), tuple_column=(), int_column=(),
                 float_column=(), dict_column=(), str_column=()):
    """
    Convert string value to another type
    :param row: row that contains value
    :param n: index of value
    :param i: value
    :param percent_column: list of value header that should be in percentage as decimal value
    :param mod_column: list of value header that should be in percentage as decimal value and use as additive later
    :param list_column: list of value header that should be in list type, in case it needs to be modified later
    :param tuple_column: list of value header that should be in tuple type, for value that is static
    :param int_column: list of value header that should be in int number type
    :param float_column: list of value header that should be in float number type
    :param dict_column: list of value header that should be in dict type
    :param dict_column: list of value header that should be in str type
    :return: converted row
    """
    if n in percent_column:
        if i == "":
            row[n] = 1
        else:
            row[n] = float(i) / 100

    elif n in mod_column:
        if i == "":
            row[n] = 0
        else:
            # Keep only the number higher or lower than 1 (base), as the game will stack modifier before calculate them
            row[n] = float(i)

    elif n in list_column:
        if "," in i:
            if "." in i:
                row[n] = [float(item) if re.search("[a-zA-Z]", item) is None else str(item) for item in i.split(",")]
            else:
                row[n] = [int(item) if item.isdigit() else item for item in i.split(",")]
        elif i.isdigit():
            if "." in i:
                row[n] = [float(i)]
            else:
                row[n] = [int(i)]
        else:
            row[n] = [i]
            if i == "":
                row[n] = []

    elif n in tuple_column:
        if "," in i:
            if "." in i:
                row[n] = tuple(
                    [float(item) if re.search("[a-zA-Z]", item) is None else str(item) for item in i.split(",")])
            else:
                row[n] = tuple([int(item) if item.isdigit() else item for item in i.split(",")])
        elif i.isdigit():
            if "." in i:
                row[n] = tuple([float(i)])
            else:
                row[n] = tuple([int(i)])
        else:
            row[n] = tuple([i])
            if i == "":
                row[n] = ()

    elif n in int_column:
        if i != "":
            row[n] = int(i)
        elif i == "":
            row[n] = 0

    elif n in float_column:
        if i != "":
            row[n] = float(i)
        elif i == "":
            row[n] = 0

    elif n in dict_column:
        if i != "":
            new_i = i.split(",")
            result_i = {}
            for item in new_i:
                new_i2 = item.split(":")
                result_i[new_i2[0]] = new_i2[1]
            row[n] = result_i
        else:
            row[n] = {}
    elif n in str_column:
        row[n] = str(i)

    else:
        if i == "":
            row[n] = 0
        elif i.lower() == "true":
            row[n] = True
        elif i.lower() == "false":
            row[n] = False
        elif i.isdigit() or (("-" in i or "." in i) and re.search("[a-zA-Z]", i) is None) or i == "inf":
            row[n] = float(i)
    return row


def md5_update_from_dir(directory, hash):
    assert Path(directory).is_dir()
    for path in sorted(Path(directory).iterdir(), key=lambda p: str(p).lower()):
        hash.update(path.name.encode())
        if path.is_file():
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash.update(chunk)
        elif path.is_dir():
            hash = md5_update_from_dir(path, hash)
    return hash


def md5_dir(directory):
    return md5_update_from_dir(directory, hashlib.md5()).hexdigest()


def sort_list_dir_with_str(dir_list, str_list):
    sorted_dir = []
    for index in range(len(str_list)):
        for x in dir_list:
            if os.path.normpath(x).split(os.sep)[-1:][0] == str_list[index]:
                sorted_dir.append(x)
    for item in dir_list:  # add item not in already sorted to the end of list
        if item not in sorted_dir:
            sorted_dir.append(item)
    return sorted_dir


def clean_group_object(groups):
    """Clean all attributes of every object in group in list"""
    for group in groups:
        if len(group) > 0:
            if type(group) == pygame.sprite.Group or type(group) == list or type(group) == tuple:
                for stuff in group:
                    clean_object(stuff)
                group.empty()
            elif type(group) == dict:
                for stuff in group.values():
                    for item in stuff:
                        clean_object(item)
            else:
                group.kill()
                group.delete()
                del group


def clean_object(this_object):
    """Clean all attributes of the object and delete it"""
    this_object.kill()
    for attribute in tuple(this_object.__dict__.keys()):
        this_object.__delattr__(attribute)
    del this_object
