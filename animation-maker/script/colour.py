import pygame
from PIL import Image, ImageOps


def apply_sprite_colour(surface, colour=None, white_colour=True):
    """Colorise body part sprite"""
    if surface is not None:
        size = surface.get_size()
        data = pygame.image.tobytes(surface, "RGBA")  # convert image to string data for filtering effect
        surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
        alpha = surface.split()[-1]  # save alpha
        surface = surface.convert("L")  # convert to grey scale for colourise
        if colour is not None:
            mid_colour = "white"
            if white_colour is False:
                max_colour = 255  # - (colour[0] + colour[1] + colour[2])
                mid_colour = [int(c - ((max_colour - c) / 2)) for c in colour]

            surface = ImageOps.colorize(surface, black="black", mid=colour, white=mid_colour).convert("RGB")
        surface.putalpha(alpha)  # put back alpha
        surface = surface.tobytes()
        surface = pygame.image.frombytes(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface
