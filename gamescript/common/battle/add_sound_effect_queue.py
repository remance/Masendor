def add_sound_effect_queue(self, sound_name, sound_base_pos, sound_distance_power, shake_power):
    distance = sound_base_pos.distance_to(self.true_camera_pos)
    if distance < 1:
        distance = 1
    sound_distance = sound_distance_power / distance
    if sound_distance < 0:
        sound_distance = 0
    elif sound_distance > 1:
        sound_distance = 1

    effect_volume = sound_distance * (self.camera_zoom / self.max_camera_zoom) * \
                    self.play_effect_volume

    screen_shake_power = self.cal_shake_value(sound_base_pos, shake_power)

    if effect_volume > 0:
        if sound_name not in self.sound_effect_queue:
            self.sound_effect_queue[sound_name] = [effect_volume, screen_shake_power]
        else:
            self.sound_effect_queue[sound_name][0] += effect_volume

            self.sound_effect_queue[sound_name][1] += screen_shake_power
