import pygame

from PIL import Image, ImageOps, ImageFilter, ImageEnhance


def play_animation(self, speed, dt, scale=1, replace_image=True):
    """
    Play sprite animation
    :param self: Object of the animation sprite
    :param speed: Play speed
    :param dt: Time
    :param scale: Sprite scale
    :param replace_image: Further zoom level does not show sprite animation even when it play
    :return: Boolean of animation finish playing or not
    """
    done = False
    current_animation = self.current_animation[self.sprite_direction]
    if not self.current_action or ("hold" in self.current_action and "hold" in current_animation[self.show_frame]["frame_property"] and
                                   "hold" in self.action_list[self.weapon_name[self.equipped_weapon][int(self.current_action[0][-1])]]["Properties"]) is False:  # not holding current frame
        self.animation_timer += dt
        if self.animation_timer >= speed:
            self.animation_timer = 0
            if self.show_frame < len(current_animation) - 1:
                self.show_frame += 1
            else:  # TODO add property
                done = True
        if replace_image:  # replace image sprite
            self.image = current_animation[self.show_frame]["sprite"]
    # if scale == 1:
    # else:
    #     self.image = pygame.transform.scale(current_animation[self.show_frame]["sprite"].copy(),
    #                                         (self.image.get_width() * scale, self.image.get_height() * scale))
    return done


def reset_animation(self):
    """
    Reset animation variable
    :param self: Object of the animation sprite
    """
    self.show_frame = 0
    self.animation_timer = 0
    self.interrupt_animation = True

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
