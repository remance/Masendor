import csv
import os
import re
import hashlib
from pathlib import Path

from PIL import Image
from pygame import image
from pygame.mixer import Sound
from pygame.transform import smoothscale, flip


accept_image_types = ("png", "jpg", "jpeg", "svg", "gif", "bmp")


def load_image(directory, screen_scale, file, subfolder="", no_alpha=False, as_pillow_image=False):
    """
    loads an image and prepares it for game
    :param directory: Directory folder path
    :param screen_scale: Resolution scale of game
    :param file: File name
    :param subfolder: List of sub1_folder path
    :param no_alpha: Indicate if surface require alpha or not
    :param as_pillow_image: return surface as Pillow image instead of pygame surface
    :return: Pygame Surface
    """
    new_subfolder = subfolder
    if isinstance(new_subfolder, list) or isinstance(new_subfolder, tuple):
        new_subfolder = ""
        for folder in subfolder:
            new_subfolder = os.path.join(new_subfolder, folder)
    this_file = os.path.join(directory, new_subfolder, file)
    if not no_alpha:
        surface = image.load(this_file).convert_alpha()
    else:
        surface = image.load(this_file).convert()
    if screen_scale[0] != 1 and screen_scale[1] != 1:  # scale to screen scale
        surface = smoothscale(surface, (surface.get_width() * screen_scale[0],
                                        surface.get_height() * screen_scale[1]))
    if as_pillow_image:
        size = surface.get_size()
        data = image.tobytes(surface, "RGBA")  # convert image to string data for filtering effect
        surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data

    return surface


def load_images(directory, screen_scale=(1, 1), subfolder=(), key_file_name_readable=False, no_alpha=False,
                as_pillow_image=False):
    """
    loads all images(only png files) in folder
    :param directory: Directory folder path
    :param screen_scale: Resolution scale of game
    :param subfolder: List of sub1_folder path
    :param key_file_name_readable: Convert key name from file name into data readable
    :param no_alpha: Indicate if all loaded surfaces require alpha or not
    :param as_pillow_image: return surfaces as Pillow image instead of pygame surface
    :return: Dict of loaded and scaled images as Pygame Surface
    """
    images = {}
    dir_path = directory
    for folder in subfolder:
        dir_path = os.path.join(dir_path, folder)

    try:
        load_order_file = [f for f in os.listdir(dir_path) if
                           any(f.endswith(item) for item in accept_image_types)]  # read all image file
        try:  # sort file name if all in number only
            load_order_file.sort(
                key=lambda var: [int(x) if x.lstrip("-").isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
        except TypeError:  # has character in file name
            pass
        for file in load_order_file:
            file_name = file
            if "." in file_name:  # remove extension from name
                file_name = file.split(".")[:-1]
                file_name = "".join(file_name)
            if key_file_name_readable:
                file_name = filename_convert_readable(file_name)
            images[file_name] = load_image(directory, screen_scale, file, subfolder=dir_path, no_alpha=no_alpha,
                                           as_pillow_image=as_pillow_image)

        return images

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
    file = os.path.join(main_dir, "../data", "sound", file)
    sound = Sound(file)
    return sound


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
    image_normal = load_image(main_dir, screen_scale, "bar_normal.jpg", ("ui", "mainmenu_ui"))
    image_hover = load_image(main_dir, screen_scale, "bar_mouse.jpg", ("ui", "mainmenu_ui"))
    for index, bar in enumerate(list_to_do):
        bar_image = (image_normal.copy(), image_hover.copy(), image_hover.copy())
        bar = uimenu.MenuButton(bar_image, (menu_image.pos[0],
                                            menu_image.pos[1] + image_normal.get_height() * (index + 1)),
                                key_name=bar)
        bar_list.append(bar)
    return bar_list


def load_base_button(data_dir, screen_scale):
    return (load_image(data_dir, screen_scale, "idle_button.png", ("ui", "mainmenu_ui")),
            load_image(data_dir, screen_scale, "mouse_button.png", ("ui", "mainmenu_ui")),
            load_image(data_dir, screen_scale, "click_button.png", ("ui", "mainmenu_ui")))


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
    :param str_column: list of value header that should be in str type
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
                row[n] = [int(item) if item.lstrip("-").isdigit() else item for item in i.split(",")]
        elif i.lstrip("-").isdigit():
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
                row[n] = tuple([int(item) if item.lstrip("-").isdigit() else item for item in i.split(",")])
        elif i.lstrip("-").isdigit():
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
        # dict column value can be in key:value format or just key, if contains only key it will be assigned TRUE value
        # if it has / and character after the value after / will be the item value
        if i != "":
            new_i = i.split(",")
            result_i = {}
            for item in new_i:
                if ":" in item:
                    new_i2 = item.split(":")
                    result_i[new_i2[0]] = new_i2[1]
                    if new_i2[1] == "true":
                        result_i[new_i2[0]] = True
                    elif new_i2[1] == "false":
                        result_i[new_i2[0]] = False
                else:
                    if "/" not in item:
                        result_i[item] = True
                    else:
                        value = item.split("/")[1]
                        if value.isdigit():
                            value = int(value)
                        elif "." in value and re.search("[a-zA-Z]", i) is None:
                            value = float(value)
                        result_i[item.split("/")[0]] = value
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
        elif (i.lstrip("-").isdigit() or "." in i and re.search("[a-zA-Z]", i) is None) or i == "inf":
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
