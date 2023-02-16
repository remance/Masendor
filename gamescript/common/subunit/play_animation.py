import pygame


def play_animation(self, dt, hold_check):
    """
    Play troop sprite animation
    :param self: Object of the animation sprite
    :param speed: Play speed
    :param dt: Time
    :param hold_check: Check if holding animation frame or not
    :return: Boolean of animation finish playing or not and just start
    """
    done = False
    frame_start = False  # check if new frame just start playing this call
    current_animation = self.current_animation[self.sprite_direction]
    if hold_check is False:  # not holding current frame
        self.animation_timer += dt
        if self.animation_timer >= self.animation_play_speed:
            self.animation_timer = 0
            frame_start = True
            if self.show_frame < self.max_show_frame:
                self.show_frame += 1
            else:
                if "repeat" in self.current_action:
                    self.show_frame = 0
                else:
                    frame_start = False
                    done = True
            if done is False:  # check if new frame has play speed mod
                if "play_time_mod" in self.current_animation[self.show_frame]["frame_property"]:
                    self.animation_play_speed = self.default_animation_play_speed * \
                                                self.current_animation[self.show_frame]["frame_property"]["play_time_mod"]
                elif "play_time_mod" in self.current_animation[self.show_frame]["animation_property"]:
                    self.animation_play_speed = self.default_animation_play_speed * \
                                                self.current_animation[self.show_frame]["animation_property"]["play_time_mod"]

    self.image = current_animation[self.show_frame]["sprite"]

    self.offset_pos = self.pos - current_animation[self.show_frame]["center_offset"]
    self.rect = self.image.get_rect(center=self.offset_pos)

    return done, frame_start


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
