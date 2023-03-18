def play_animation(self, dt, hold_check):
    """
    Play troop sprite animation
    :param self: Object of the animation sprite
    :param dt: Time
    :param hold_check: Check if holding animation frame or not
    :return: Boolean of animation finish playing or not and just start
    """
    done = False
    frame_start = False  # check if new frame just start playing this call

    if not hold_check:  # not holding current frame
        self.frame_timer += dt
        if self.frame_timer >= self.animation_play_time:
            self.frame_timer = 0
            frame_start = True
            if self.show_frame < self.max_show_frame:
                self.show_frame += 1
            else:
                if "repeat" in self.current_action:
                    self.show_frame = 0
                else:
                    frame_start = False
                    done = True
            if not done:  # check if new frame has play speed mod
                self.animation_play_time = self.default_animation_play_time
                if "play_time_mod" in self.current_animation[self.show_frame]:
                    self.animation_play_time = self.default_animation_play_time * \
                                               self.current_animation[self.show_frame]["play_time_mod"]

    current_animation = self.current_animation[self.sprite_direction][self.show_frame]
    self.image = current_animation["sprite"]

    if self.current_effect:  # play effect animation
        self.effectbox.image = self.status_animation_pool[self.current_effect]["frame"][self.effect_frame]
        self.effectbox.rect = self.effectbox.image.get_rect(center=self.offset_pos)
        self.effect_timer += dt
        if self.effect_timer >= 0.1:
            self.effect_timer = 0
            if self.effect_frame < self.max_effect_frame:
                self.effect_frame += 1
            else:
                self.effect_frame = 0
                self.max_effect_frame = 0
                self.current_effect = None
                self.battle.battle_camera.remove(self.effectbox)

    self.offset_pos = self.pos - current_animation["center_offset"]
    self.rect = self.image.get_rect(center=self.offset_pos)

    return done, frame_start
