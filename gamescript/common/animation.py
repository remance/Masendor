import pygame

from PIL import Image, ImageOps, ImageFilter, ImageEnhance


def play_animation(self, speed, dt, scale=1, replace_image=True):
    done = False
    self.animation_timer += dt
    current_animation = self.current_animation[self.sprite_direction]
    if self.animation_timer >= speed:
        if self.show_frame < len(current_animation):
            self.show_frame += 1
        self.animation_timer = 0
        if self.show_frame >= len(current_animation):  # TODO add property
            done = True
            self.show_frame = 0

    if replace_image:
        self.image = current_animation[self.show_frame]["sprite"]
    # if scale == 1:
    # else:
    #     self.image = pygame.transform.scale(current_animation[self.show_frame]["sprite"].copy(),
    #                                         (self.image.get_width() * scale, self.image.get_height() * scale))
    return done


def apply_colour(surface, colour=None, colour_list=None):
    """Colorise body part sprite"""
    if colour is not None and colour != "none":
        max_colour = 255  # - (colour[0] + colour[1] + colour[2])
        if colour_list is not None:
            mid_colour = colour_list[colour]
        else:
            mid_colour = [int(c - ((max_colour - c) / 2)) for c in colour]

        size = (surface.get_width(), surface.get_height())
        data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
        surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
        alpha = surface.split()[-1]  # save alpha
        surface = surface.convert("L")  # convert to grey scale for colourise
        surface = ImageOps.colorize(surface, black="black", mid=mid_colour, white=colour).convert("RGB")
        surface.putalpha(alpha)  # put back alpha
        surface = surface.tobytes()
        surface = pygame.image.fromstring(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface
