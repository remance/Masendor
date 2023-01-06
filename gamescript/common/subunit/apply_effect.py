def apply_effect(self, effect, effect_list, status_effect_list):
    if effect not in status_effect_list:
        status_effect_list[effect] = effect_list[effect].copy()
    else:  # reset duration of current exist effect
        status_effect_list[effect]["Duration"] = effect_list[effect]["Duration"]
