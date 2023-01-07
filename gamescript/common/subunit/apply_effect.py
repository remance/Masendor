def apply_effect(self, effect, effect_list, status_effect_list, duration_list):
    if effect not in duration_list:
        status_effect_list[effect] = effect_list[effect]
    duration_list[effect] = effect_list[effect]["Duration"]
