import pygame
from PIL import Image, ImageOps


def apply_colour(surface, colour=None):
    """Colorise body part sprite"""
    size = surface.get_size()
    data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
    surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
    alpha = surface.split()[-1]  # save alpha
    surface = surface.convert("L")  # convert to grey scale for colourise
    if colour is not None:
        max_colour = 255  # - (colour[0] + colour[1] + colour[2])
        mid_colour = [int(c - ((max_colour - c) / 2)) for c in colour]
        surface = ImageOps.colorize(surface, black="black", mid=mid_colour, white=colour).convert("RGB")
    surface.putalpha(alpha)  # put back alpha
    surface = surface.tobytes()
    surface = pygame.image.fromstring(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface
