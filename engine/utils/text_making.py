import datetime
from random import randint

from PIL import Image
from pygame import Color, Surface, image


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


def minimise_number_text(text):
    num_text = int(text)
    if num_text >= 1000000:
        return str(round(num_text / 1000000, 1)) + "M"
    elif num_text >= 1000:
        return str(round(num_text / 1000, 1)) + "K"
    else:
        return str(num_text)


def number_to_minus_or_plus(number):
    """Number should not be 0"""
    if number > 0:
        return "+"
    else:  # assuming number is not 0
        return "-"


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


def text_render_with_bg(text, font, gf_colour=Color("black"), o_colour=(255, 255, 255), opx=2):
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


def text_render_with_texture(text, font, texture):
    """
    Render text with custom texture
    :param text: Text strings
    :param font: Pygame font
    :param texture: Texture for font
    :return: Text surface
    """
    text_surface = font.render(text, True, (0, 0, 0))
    size = text_surface.get_size()
    data = image.tobytes(text_surface, "RGBA")  # convert image to string data for filtering effect
    text_surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data

    surface = Image.new("RGBA", size, (0, 0, 0, 0))
    texture_size = texture.size
    pos = (randint(0, texture_size[0] - size[0]), randint(0, texture_size[1] - size[1]))
    new_texture = texture.crop((pos[0], pos[1], pos[0] + size[0], pos[1] + size[1]))
    surface.paste(new_texture, box=(0, 0), mask=text_surface)
    size = surface.size
    surface = surface.tobytes()
    surface = image.frombytes(surface, size, "RGBA")  # convert image back to a pygame surface

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
