def apply_effect(self, effect, effect_stat, status_effect_list, duration_list):
    if effect not in duration_list:
        status_effect_list[effect] = effect_stat
    duration_list[effect] = effect_stat["Duration"]
