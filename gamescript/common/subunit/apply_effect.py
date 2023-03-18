def apply_effect(self, effect, effect_stat, status_effect_list, duration_list):
    if self.alive:
        if effect not in duration_list:
            status_effect_list[effect] = effect_stat
            # play status animation
            self.effect_frame = 0
            self.max_effect_frame = 0
            if "Type" in effect_stat and self.current_effect != effect_stat["Status Sprite"]:
                self.current_effect = effect_stat["Status Sprite"]
                self.max_effect_frame = self.status_animation_pool[self.current_effect]["frame_number"]
                if self.effectbox not in self.battle.battle_camera:
                    self.battle.battle_camera.add(self.effectbox)

        duration_list[effect] = effect_stat["Duration"]
