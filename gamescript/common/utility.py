import ast
import csv
import datetime
import inspect
import math
import os
import re

import pygame
import pygame.freetype
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


def change_group(item, group, change):
    if change == "add":
        group.add(item)
    elif change == "remove":
        group.remove(item)


def load_image(main_dir, screen_scale, file, subfolder=""):
    """loads an image, prepares it for play"""
    new_subfolder = subfolder
    if isinstance(new_subfolder, list):
        new_subfolder = ""
        for folder in subfolder:
            new_subfolder = os.path.join(new_subfolder, folder)
    this_file = os.path.join(main_dir, "data", new_subfolder, file)
    surface = pygame.image.load(this_file).convert_alpha()
    surface = pygame.transform.scale(surface,
                                     (surface.get_width() * screen_scale[0], surface.get_height() * screen_scale[1]))
    return surface


def load_images(main_dir, screen_scale, subfolder=None, load_order=True, return_order=False):
    """loads all images(files) in folder using loadorder list file use only png file"""
    images = {}
    dir_path = os.path.join(main_dir, "data")
    if subfolder is not None:
        for folder in subfolder:
            dir_path = os.path.join(dir_path, folder)

    if load_order:  # load in the order of load_order file
        load_order_file = open(os.path.join(dir_path, "load_order.txt"), "r")
        load_order_file = ast.literal_eval(load_order_file.read())
    else:  # load every file
        load_order_file = [f for f in os.listdir(dir_path) if f.endswith("." + "png")]  # read all file
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


def load_textures(main_dir, subfolder=None, scale=(1, 1)):
    """loads all body sprite part image"""
    imgs = {}
    dir_path = os.path.join(main_dir, "data")
    if subfolder is not None:
        for folder in subfolder:
            dir_path = os.path.join(dir_path, folder)
    try:
        load_order_file = [f for f in os.listdir(dir_path) if f.endswith("." + "png")]  # read all file
        load_order_file.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
        for file in load_order_file:
            imgs[file.split(".")[0]] = load_image(main_dir, scale, file,
                                                  dir_path)  # no need to scale at this point, will scale when in complete sprite
    except FileNotFoundError:
        pass

    return imgs


def convert_str_time(event):
    """Convert text string of time to datetime"""
    for index, item in enumerate(event):
        new_time = datetime.datetime.strptime(item[1], "%H:%M:%S").time()
        new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
        event[index] = [item[0], new_time]
        if len(item) == 3:  # weather strength
            event[index].append(item[2])


def csv_read(main_dir, file, subfolder=(), output_type=0, header_key=False, language=None):
    """output type 0 = dict, 1 = list"""
    return_output = {}
    if output_type == 1:
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
            if output_type == 0:  # return as dict
                if header_key:
                    if row_index > 0:  # skip header row
                        return_output[row[0]] = {header[index + 1]: item for index, item in enumerate(row[1:])}
                else:
                    return_output[row[0]] = row[1:]
            elif output_type == 1:  # return as list
                return_output.append(row)
        edit_file.close()
    return return_output


def load_sound(main_dir, file):
    file = os.path.join(main_dir, "data", "sound", file)
    sound = pygame.mixer.Sound(file)
    return sound


def edit_config(section, option, value, filename, config):
    config.set(section, option, str(value))
    with open(filename, "w") as configfile:
        config.write(configfile)


def make_long_text(surface, text, pos, font, color=pygame.Color("black")):
    """Blit long text into separate row of text"""
    if type(text) != list:
        text = [text]
    x, y = pos
    for this_text in text:
        words = [word.split(" ") for word in str(this_text).splitlines()]  # 2D array where each row is a list of words
        space = font.size(" ")[0]  # the width of a space
        max_width, max_height = surface.get_size()
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # reset x
                    y += word_height  # start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # reset x
            y += word_height  # start on new row


def make_bar_list(main_dir, screen_scale, list_to_do, menu_image, updater):
    """Make a drop down bar list option button"""
    bar_list = []
    image = load_image(main_dir, screen_scale, "bar_normal.jpg", "ui\\mainmenu_ui")
    image2 = load_image(main_dir, screen_scale, "bar_mouse.jpg", "ui\\mainmenu_ui")
    image3 = image2
    for index, bar in enumerate(list_to_do):
        bar_image = (image.copy(), image2.copy(), image3.copy())
        bar = menu.MenuButton(screen_scale, bar_image,
                              (menu_image.pos[0], menu_image.pos[1] + image.get_height() * (index + 1)),
                              updater, text=bar)
        bar_list.append(bar)
    return bar_list


def load_base_button(main_dir, screen_scale):
    image = load_image(main_dir, screen_scale, "idle_button.png", ["ui", "mainmenu_ui"])
    image2 = load_image(main_dir, screen_scale, "mouse_button.png", ["ui", "mainmenu_ui"])
    image3 = load_image(main_dir, screen_scale, "click_button.png", ["ui", "mainmenu_ui"])
    return [image, image2, image3]


def text_objects(text, font):
    text_surface = font.render(text, True, (200, 200, 200))
    return text_surface, text_surface.get_rect()


def rotation_xy(origin, point, angle):
    """
    Rotate point to the new pos
    :param origin: origin pos
    :param point: target point pos
    :param angle: angle of rotation
    :return:
    """
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x, y)


def set_rotate(self, set_target=None):
    """
    set base_target and new angle for sprite rotation
    :param self: sprite object
    :param set_target: pos for target position to rotate to
    :return: new angle
    """
    if set_target is None:  # Use base target variable
        my_radians = math.atan2(self.base_target[1] - self.base_pos[1], self.base_target[0] - self.base_pos[0])
    else:  # use set_target parameter
        my_radians = math.atan2(set_target[1] - self.base_pos[1], set_target[0] - self.base_pos[0])
    new_angle = math.degrees(my_radians)

    # """upper left -"""
    if -180 <= new_angle <= -90:
        new_angle = -new_angle - 90

    # """upper right +"""
    elif -90 < new_angle < 0:
        new_angle = (-new_angle) - 90

    # """lower right -"""
    elif 0 <= new_angle <= 90:
        new_angle = -(new_angle + 90)

    # """lower left +"""
    elif 90 < new_angle <= 180:
        new_angle = 270 - new_angle
    return round(new_angle)


def setup_list(screen_scale, item_class, current_row, show_list, item_group, box, ui_class, layer=15):
    """generate list of subsection of the left side of encyclopedia"""
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


def popout_lorebook(self, section, game_id):
    """open and draw enclycopedia at the specified subsection,
    used for when user right click at icon that has encyclopedia section"""
    self.game_state = "menu"
    self.battle_menu.mode = "encyclopedia"
    self.battle_ui_updater.add(self.encyclopedia, self.lore_name_list, self.lore_name_list.scroll, *self.lore_button_ui)

    self.encyclopedia.change_section(section, self.lore_name_list, self.subsection_name, self.lore_name_list.scroll,
                                     self.page_button,
                                     self.battle_ui_updater)
    self.encyclopedia.change_subsection(game_id, self.page_button, self.battle_ui_updater)
    self.lore_name_list.scroll.change_image(new_row=self.encyclopedia.current_subsection_row)


def popup_list_open(self, new_rect, new_list, ui_type):
    """Move popup_listbox and scroll sprite to new location and create new name list based on type"""
    self.current_popup_row = 0

    if ui_type == "leader" or ui_type == "genre":
        self.popup_list_box.rect = self.popup_list_box.image.get_rect(topleft=new_rect)
    else:
        self.popup_list_box.rect = self.popup_list_box.image.get_rect(midbottom=new_rect)

    setup_list(self.screen_scale, menu.NameList, 0, new_list, self.popup_namegroup,
               self.popup_list_box, self.battle_ui_updater, layer=19)

    self.popup_list_box.scroll.pos = self.popup_list_box.rect.topright  # change position variable
    self.popup_list_box.scroll.rect = self.popup_list_box.image.get_rect(topleft=self.popup_list_box.rect.topright)  #
    self.popup_list_box.scroll.change_image(new_row=0, row_size=len(new_list))

    if ui_type == "genre":
        self.main_ui_updater.add(self.popup_list_box, *self.popup_namegroup, self.popup_list_box.scroll)
    else:
        self.battle_ui_updater.add(self.popup_list_box, *self.popup_namegroup,
                                   self.popup_list_box.scroll)  # add the option list to screen

    self.popup_list_box.type = ui_type


def stat_convert(row, n, i, percent_column=(), mod_column=(), list_column=(), tuple_column=(), int_column=(),
                 float_column=(), boolean_column=(), true_empty=False):
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
    :param boolean_column: list of value header that should be in boolean value
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
    for group in groups:
        if len(group) > 0:
            if type(group) == pygame.sprite.Group or type(group) == list or type(group) == tuple:
                for stuff in group:
                    stuff.kill()
                    for attribute in tuple(stuff.__dict__.keys()):
                        stuff.__delattr__(attribute)
                    del stuff
            elif type(group) == dict:
                for stuff in group.values():
                    for item in stuff:
                        item.kill()
                        for attribute in tuple(stuff.__dict__.keys()):
                            stuff.__delattr__(attribute)
                        del item
            else:
                group.kill()
                group.delete()
                del group
