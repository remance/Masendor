from PIL import Image, ImageOps

from pygame import image


def crop_sprite(sprite_pic):
    low_x0 = float("inf")  # lowest x0
    low_y0 = float("inf")  # lowest y0
    high_x1 = 0  # highest x1
    high_y1 = 0  # highest y1

    # Find optimal cropped sprite size and center offset
    size = sprite_pic.get_size()
    data = image.tostring(sprite_pic, "RGBA")  # convert image to string data for filtering effect
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
    sprite_pic = image.tostring(sprite_pic, "RGBA")  # convert image to string data for filtering effect
    sprite_pic = Image.frombytes("RGBA", size, sprite_pic)  # use PIL to get image data
    sprite_pic = sprite_pic.crop((low_x0, low_y0, high_x1, high_y1))
    size = sprite_pic.size
    sprite_pic = sprite_pic.tobytes()
    sprite_pic = image.fromstring(sprite_pic, size, "RGBA")  # convert image back to a pygame surface

    # Find center offset after crop by finding width and height difference of longer side
    center_x_offset = ((low_x0 + high_x1) / 2) + (((100 - low_x0) - (high_x1 - 100)) / 10)
    center_y_offset = ((low_y0 + high_y1) / 2) + (((100 - low_y0) - (high_y1 - 100)) / 10)
    center_offset = (center[0] - center_x_offset, center[1] - center_y_offset)

    return sprite_pic, center_offset


def apply_sprite_colour(surface, colour, colour_list=None, keep_white=True):
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
        data = image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
        surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
        alpha = surface.split()[-1]  # save alpha
        surface = surface.convert("L")  # convert to grey scale for colourise
        surface = ImageOps.colorize(surface, black="black", mid=mid_colour, white=white_colour).convert("RGB")
        # if any abs(mean(colour[0], colour[1], colour[2]) > 10) is False:
        surface.putalpha(alpha)  # put back alpha
        surface = surface.tobytes()
        surface = image.fromstring(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface
