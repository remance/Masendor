import ast
import csv
import datetime
import inspect
import math
import os
import re
import numpy as np

import pygame
import pygame.freetype

from PIL import Image, ImageOps

from gamescript import menu

accept_image_types = ("png", "jpg", "jpeg", "svg", "gif", "bmp")


def empty_method(self, *args):
    if hasattr(self, 'error_log'):
        error_text = "{0} -- {1}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                           "Empty method is called") + \
                     str(inspect.stack()[1][1]) + "At Line" + str(inspect.stack()[1][2]) + ":" + \
                     str(inspect.stack()[1][3])
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


def load_image(main_dir, screen_scale, file, subfolder=""):
    """
    loads an image and prepares it for game
    :param main_dir: Game directory folder path
    :param screen_scale: Resolution scale of game
    :param file: File name
    :param subfolder: List of subfolder path
    :return: Pygame Surface
    """
    new_subfolder = subfolder
    if isinstance(new_subfolder, list) or isinstance(new_subfolder, tuple):
        new_subfolder = ""
        for folder in subfolder:
            new_subfolder = os.path.join(new_subfolder, folder)
    this_file = os.path.join(main_dir, "data", new_subfolder, file)
    surface = pygame.image.load(this_file).convert_alpha()
    surface = pygame.transform.scale(surface,
                                     (surface.get_width() * screen_scale[0],
                                      surface.get_height() * screen_scale[1]))
    return surface


def load_images(main_dir, screen_scale=(1, 1), subfolder=(), load_order=False, return_order=False):
    """
    loads all images(only png files) in folder
    :param main_dir: Game directory folder path
    :param screen_scale: Resolution scale of game
    :param subfolder: List of subfolder path
    :param load_order: Using loadorder list file to create ordered list
    :param return_order: Return the order
    :return: Dict of loaded and scaled images as Pygame Surface
    """
    images = {}
    dir_path = os.path.join(main_dir, "data")
    for folder in subfolder:
        dir_path = os.path.join(dir_path, folder)

    try:
        if load_order:  # load in the order of load_order file
            load_order_file = open(os.path.join(dir_path, "load_order.txt"), "r")
            load_order_file = ast.literal_eval(load_order_file.read())
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
            images[file_name] = load_image(main_dir, screen_scale, file, dir_path)

        if return_order is False:
            return images
        else:  # return order of the file as list
            load_order_file = [int(name.replace(".png", "")) for name in load_order_file]
            return images, load_order_file
    except FileNotFoundError as b:
        print(b)
        return images


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


def csv_read(main_dir, file, subfolder=(), output_type="dict", header_key=False, language=None):
    """
    Read csv file
    :param main_dir: Game directory folder path
    :param file: File name
    :param subfolder: Array of subfolder path
    :param output_type: Type of returned object, either dict or list
    :param header_key: Use header as dict key or not
    :param language: File language in acronym such as en for English
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
    if language is not None:
        folder_dir += "_" + language
    with open(folder_dir, encoding="utf-8", mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        rd = [row for row in rd]
        header = rd[0]
        for row_index, row in enumerate(rd):
            for n, i in enumerate(row):
                if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None):
                    row[n] = int(i)
                elif re.search("[a-zA-Z]", i) is None and "." in i:
                    row[n] = float(i)
            if output_type == "dict":  # return as dict
                if header_key:
                    if row_index > 0:  # skip header row
                        return_output[row[0]] = {header[index + 1]: item for index, item in enumerate(row[1:])}
                else:
                    return_output[row[0]] = row[1:]
            elif output_type == "list":  # return as list
                return_output.append(row)
        edit_file.close()
    return return_output


def lore_csv_read(edit_file, input_dict):
    rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
    rd = [row for row in rd]
    for index, row in enumerate(rd):
        for n, i in enumerate(row):
            if i.isdigit():
                row[n] = int(i)
        input_dict[row[0]] = [stuff for index, stuff in enumerate(row[1:])]
        while len(input_dict[row[0]]) > 2 and input_dict[row[0]][-1] == "":  # keep remove last empty text
            input_dict[row[0]] = input_dict[row[0]][:-1]


def load_sound(main_dir, file):
    """
    Load sound file
    :param main_dir: Game directory folder path
    :param file: File name
    :return: Pygame Sound
    """
    file = os.path.join(main_dir, "data", "sound", file)
    sound = pygame.mixer.Sound(file)
    return sound


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


def make_long_text(surface, text, pos, font, color=pygame.Color("black")):
    """
    Blit long text into separate row of text
    :param surface: Input Pygame Surface
    :param text: Bunch of texts
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
        max_width, max_height = surface.get_size()
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


def text_render(text, font, gf_colour=pygame.Color("black"), o_colour=(255, 255, 255), opx=2):
    """
    Render text with background border
    :param text: Bunch of texts
    :param font: Pygame Font
    :param gf_colour: Text colour
    :param o_colour: Background colour
    :param opx: Background colour thickness
    :return: Text surface
    """
    text_surface = font.render(text, True, gf_colour).convert_alpha()
    w = text_surface.get_width() + 2 * opx
    h = font.get_height()

    osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
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


def make_bar_list(main_dir, screen_scale, list_to_do, menu_image, updater):
    """
    Make a drop down bar list option button
    :param main_dir: Game directory folder path
    :param screen_scale: Resolution scale of game
    :param list_to_do: List of text
    :param menu_image: Menu image that will get drop list
    :param updater: Pygame Updater group
    :return: List of bar button objects
    """
    bar_list = []
    image = load_image(main_dir, screen_scale, "bar_normal.jpg", ("ui", "mainmenu_ui"))
    image2 = load_image(main_dir, screen_scale, "bar_mouse.jpg", ("ui", "mainmenu_ui"))
    image3 = image2
    for index, bar in enumerate(list_to_do):
        bar_image = (image.copy(), image2.copy(), image3.copy())
        bar = menu.MenuButton(screen_scale, bar_image,
                              (menu_image.pos[0], menu_image.pos[1] + image.get_height() * (index + 1)),
                              updater, text=bar)
        bar_list.append(bar)
    return bar_list


def load_base_button(main_dir, screen_scale):
    image = load_image(main_dir, screen_scale, "idle_button.png", ("ui", "mainmenu_ui"))
    image2 = load_image(main_dir, screen_scale, "mouse_button.png", ("ui", "mainmenu_ui"))
    image3 = load_image(main_dir, screen_scale, "click_button.png", ("ui", "mainmenu_ui"))
    return [image, image2, image3]


def text_objects(text, font):
    text_surface = font.render(text, True, (200, 200, 200))
    return text_surface, text_surface.get_rect()


def rotation_xy(origin, point, angle):
    """
    Rotate point to the new pos
    :param origin: origin pos
    :param point: target point pos
    :param angle: angle of rotation in radians
    :return:
    """
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x, y)


def set_rotate(self, base_target):
    """
    set base_target and new angle for sprite rotation
    :param self: any object with base_pos as position attribute
    :param base_target: pos for target position to rotate to
    :return: new angle
    """
    my_radians = math.atan2(base_target[1] - self.base_pos[1], base_target[0] - self.base_pos[0])
    new_angle = math.degrees(my_radians)

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
    if angle > 0:
        angle += 90
    elif -180 <= angle < -90:
        angle = 360 + angle
    else:
        angle = 90 + angle
    return angle


def travel_to_map_border(pos, angle, map_size):
    """
    Find target at border of map based on angle
    :param pos: Starting pos
    :param angle: Angle in radians
    :param map_size: Size of map (width, height)
    :return: target on map border
    """
    x = pos[0]
    y = pos[1]
    cos_angle, sin_angle = math.cos(angle), math.sin(angle)
    if cos_angle == 0:
        if sin_angle < 0:
            distance = y
        else:
            distance = map_size[1] - y
    elif abs(sin_angle) < 1e-12:
        if cos_angle < 0:
            distance = x
        else:
            distance = map_size[0] - x
    else:
        distance_ew = (map_size[0] - x) / cos_angle if cos_angle > 0 else -x / cos_angle
        distance_ns = (map_size[1] - y) / sin_angle if sin_angle > 0 else -y / sin_angle
        distance = min(distance_ew, distance_ns)

    target = pygame.Vector2(x + (distance * math.sin(angle)), y - (distance * math.cos(angle)))
    return target


def apply_sprite_colour(surface, colour, colour_list, keep_white=True, keep_old_colour=False):
    """Colorise body part sprite"""
    if colour is not None and colour != "none":
        if colour_list is None:
            white_colour = colour
        else:
            white_colour = colour_list[colour]
        mid_colour = [int(c / 2) for c in white_colour]
        if keep_white:
            if colour_list is None:
                mid_colour = colour
            else:
                mid_colour = colour_list[colour]
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


def setup_list(screen_scale, item_class, current_row, show_list, item_group, box, ui_class, layer=15):
    """generate list of subsection buttons like in the encyclopedia"""
    row = 5 * screen_scale[1]
    column = 5 * screen_scale[0]
    pos = box.rect.topleft
    if current_row > len(show_list) - box.max_row_show:
        current_row = len(show_list) - box.max_row_show

    if len(item_group) > 0:  # remove previous sprite in the group before generate new one
        for stuff in item_group:
            stuff.kill()
            del stuff

    for index, item in enumerate(show_list):
        if index >= current_row:
            new_item = item_class(screen_scale, box, (pos[0] + column, pos[1] + row), item,
                                  layer=layer)
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
    if mouse_scroll_up:
        current_row -= 1
        if current_row < 0:
            current_row = 0
        else:
            setup_list(screen_scale, menu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, row_size=len(name_list))

    elif mouse_scroll_down:
        current_row += 1
        if current_row + box.max_row_show - 1 < len(name_list):
            setup_list(screen_scale, menu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, row_size=len(name_list))
        else:
            current_row -= 1
    return current_row


def popup_list_open(self, new_rect, new_list, ui_type, rect_pos, updater):
    """
    Move popup_listbox and scroll sprite to new location and create new name list
    :param self: Game or Battle object
    :param new_rect: New rect position
    :param new_list: List of texts that will be used in the popup
    :param ui_type: Type of ui that open list
    :param rect_pos: Keyword argument for rect position of get_rect
    :param updater: Updater group
    """
    self.current_popup_row = 0

    new_rect  # use exec here to make rect_pos a keyword argument for get_rect
    exec(f"" + "self.popup_list_box.rect = self.popup_list_box.image.get_rect(" + rect_pos + "= new_rect)")

    setup_list(self.screen_scale, menu.NameList, 0, new_list, self.popup_namegroup,
               self.popup_list_box, self.battle_ui_updater, layer=19)

    self.popup_list_box.scroll.pos = self.popup_list_box.rect.topright  # change position variable
    self.popup_list_box.scroll.rect = self.popup_list_box.image.get_rect(topleft=self.popup_list_box.rect.topright)  #
    self.popup_list_box.scroll.change_image(new_row=0, row_size=len(new_list))

    updater.add(self.popup_list_box, *self.popup_namegroup,
                self.popup_list_box.scroll)  # add the option list to screen

    self.popup_list_box.type = ui_type


def stat_convert(row, n, i, percent_column=(), mod_column=(), list_column=(), tuple_column=(), int_column=(),
                 float_column=(), true_empty=False):
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
    :param true_empty: Value can be empty string
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
        else:  # Keep only the number higher or lower than 1 (base), as the game will stack modifier before calculate them once
            row[n] = (float(i) - 100) / 100

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
            if true_empty:
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
            if true_empty:
                if i == "":
                    row[n] = ()

    elif n in int_column:
        if i != "" and re.search("[a-zA-Z]", i) is None:
            row[n] = int(i)
        elif i == "":
            row[n] = 0

    elif n in float_column:
        if i != "" and re.search("[a-zA-Z]", i) is None:
            row[n] = float(i)
        elif i == "":
            row[n] = 0

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


def clean_group_object(groups):
    """Clean all attributes of every object in group in list"""
    for group in groups:
        if len(group) > 0:
            if type(group) == pygame.sprite.Group or type(group) == list or type(group) == tuple:
                for stuff in group:
                    clean_object(stuff)
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
