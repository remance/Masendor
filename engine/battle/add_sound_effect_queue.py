def add_sound_effect_queue(self, sound_name, sound_base_pos, sound_distance_power, shake_power, volume_mod=1):
    screen_shake_power = self.cal_shake_value(sound_base_pos, shake_power)
    self.screen_shake_value += screen_shake_power

    if self.play_effect_volume:
        distance = sound_base_pos.distance_to(self.true_camera_pos)
        if distance < 1:
            distance = 1
        if sound_base_pos[0] > self.true_camera_pos[0]:  # sound to the right of center camera
            left_distance = distance + abs(sound_base_pos[0] - self.battle.true_camera_pos[0])
            right_distance = distance
        elif sound_base_pos[0] < self.true_camera_pos[0]:  # sound to the left of center camera
            left_distance = distance
            right_distance = distance + abs(sound_base_pos[0] - self.battle.true_camera_pos[0])
        else:  # sound at the center camera
            left_distance = distance
            right_distance = distance

        left_sound_power = sound_distance_power / left_distance
        if left_sound_power < 0:
            left_sound_power = 0
        elif left_sound_power > 1:
            left_sound_power = 1

        right_sound_power = sound_distance_power / right_distance
        if right_sound_power < 0:
            right_sound_power = 0
        elif right_sound_power > 1:
            right_sound_power = 1

        left_effect_volume = left_sound_power * volume_mod * self.play_effect_volume
        right_effect_volume = right_sound_power * volume_mod * self.play_effect_volume
        final_effect_volume = [left_effect_volume, right_effect_volume]  # left right sound volume

        if right_effect_volume or left_effect_volume:
            if sound_name not in self.sound_effect_queue:
                self.sound_effect_queue[sound_name] = final_effect_volume
            else:
                self.sound_effect_queue[sound_name][0] += final_effect_volume[0]
                self.sound_effect_queue[sound_name][1] += final_effect_volume[1]
