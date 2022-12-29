def play_animation(self, speed, dt, hold_check):
    """
    Play damage sprite animation
    :param self: Object of the animation sprite
    :param speed: Play speed
    :param dt: Time
    :param hold_check: Check if holding animation frame or not
    :return: Boolean of animation finish playing and just start
    """
    done = False
    just_start = False  # check if new frame just start playing this call
    if hold_check is False:  # not holding current frame
        self.animation_timer += dt
        if self.animation_timer >= speed:
            self.animation_timer = 0
            just_start = True
            if self.show_frame < len(self.current_animation) - 1:
                self.show_frame += 1
                self.image = self.current_animation[self.show_frame]
            else:
                if self.repeat_animation:
                    self.show_frame = 0
                    self.image = self.current_animation[self.show_frame]
                else:
                    done = True
    return done, just_start
