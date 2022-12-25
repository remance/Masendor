import pygame

from PIL import Image, ImageOps


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
    just_start = False  # check if new frame just start playing this call
    current_animation = self.current_animation[self.sprite_direction]
    hold_check = "hold" in self.current_action and "hold" in current_animation[self.show_frame]["frame_property"] and \
                 "hold" in self.action_list[int(self.current_action["name"][-1])]["Properties"]
    if not self.current_action or hold_check is False:  # not holding current frame:  # not holding current frame
        self.animation_timer += dt
        if self.animation_timer >= speed:
            self.animation_timer = 0
            just_start = True
            if self.show_frame < len(current_animation) - 1:
                self.show_frame += 1
            else:
                if "repeat" in self.current_action:
                    self.show_frame = 0
                else:
                    done = True
    if replace_image:  # replace sprite image
        self.image = current_animation[self.show_frame]["sprite"]
        self.rect = self.image.get_rect(center=self.pos)
    return done, just_start, hold_check


def sprite_fading(self, how, speed=5):
    """
    Fading sprite object in or out of camera, require alpha variable and
    image_clear (original clear image before fading) in object to work properly
    :param self: Any sprite object
    :param how: "In" for fading in and "Out" for fading out
    :param speed: How fast the fading
    """
    if how == "In":
        self.image = self.image_clear.copy()  # fading in require using original alpha image to work
        self.alpha = min(self.alpha + speed, 255)  # alpha should never be higher than 255.
    elif how == "Out":
        self.alpha = max(0, self.alpha - speed)  # alpha should never be < lower than 0.
    self.image.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)


def reset_animation(self):
    """
    Reset animation variable
    :param self: Object of the animation sprite
    """
    self.show_frame = 0
    self.animation_timer = 0
    self.interrupt_animation = True


def apply_colour(surface, colour, colour_list, keep_white=True, keep_old_colour=False):
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
