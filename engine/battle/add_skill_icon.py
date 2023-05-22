def add_skill_icon(self):
    for icon_index, icon in enumerate(self.skill_icon):  # reset skill icon
        icon.game_id = None
        for index, skill in enumerate(self.player_unit.input_skill):
            if index == icon_index:
                icon.game_id = skill
                icon.name = self.player_unit.input_skill[skill]["Name"]
                icon.icon_type = "skill"
                break
        if not icon.game_id:  # remove from updater if no skill for this icon
            self.remove_ui_updater(icon)
        else:
            self.add_ui_updater(icon)
