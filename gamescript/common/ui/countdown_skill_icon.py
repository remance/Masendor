def countdown_skill_icon(self):
    """Count down timer on skill icon for activate and cooldown time"""
    for skill in self.skill_icon:
        cd = 0
        active_time = 0
        if skill.game_id in self.player_char.skill_cooldown:
            cd = int(self.player_char.skill_cooldown[skill.game_id])
        if skill.game_id in self.player_char.skill_duration:
            active_time = int(self.player_char.skill_duration[skill.game_id])
        skill.icon_change(cd, active_time)
