def countdown_skill_icon(self):
    """Count down timer on skill icon for activate and cooldown time"""
    for skill in self.skill_icon:
        if skill.icon_type == "skill":  # only do skill icon not trait
            cd = 0
            active_time = 0
            if skill.game_id in self.troop_card_ui.value2["skill cd"]:
                cd = int(self.troop_card_ui.value2["skill cd"][skill.game_id])
            if skill.game_id in self.troop_card_ui.value2["skill effect"]:
                active_time = int(self.troop_card_ui.value2["skill effect"][skill.game_id]["Duration"])
            skill.icon_change(cd, active_time)
    # for effect in self.effect_icon:
    #     cd = 0
    #     if effect.id in self.troop_card_ui.value2[4]:
    #         cd = int(self.troop_card_ui.value2[4][effect.id][3])
    #     effect.iconchange(cd, 0)
