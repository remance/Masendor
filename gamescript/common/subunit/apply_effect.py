def apply_effect(self, effect, effect_stat, status_effect_list, duration_list):
    if effect not in duration_list:
        status_effect_list[effect] = effect_stat
    duration_list[effect] = effect_stat["Duration"]

    self.effect_frame = 0
    self.max_effect_frame = 0
    self.current_effect = effect_stat["Type"]
    if self.effectbox not in self.battle.battle_camera:
        self.battle.battle_camera.add(self.effectbox)
