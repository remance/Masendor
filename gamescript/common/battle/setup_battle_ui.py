from gamescript import battleui
from gamescript.common import utility

change_group = utility.change_group


def setup_battle_ui(self, change):
    """Change can be either 'add' or 'remove' for adding or removing ui"""
    if change == "add":
        self.time_ui.change_pos((self.screen_rect.width - self.time_ui.image.get_width(),
                                 0), self.time_number)

        self.battle_scale_ui.change_pos(self.time_ui.rect.bottomleft)

        if self.player_char:
            change_group(self.command_ui, self.battle_ui_updater, change)

            for icon_index, icon in enumerate(self.skill_icon):  # reset skill icon
                icon.game_id = None
                for index, skill in enumerate(self.player_char.input_skill):
                    if index == icon_index:
                        icon.game_id = skill
                        icon.name = self.player_char.input_skill[skill]["Name"]
                        icon.icon_type = "skill"
                        break
                if not icon.game_id:  # remove from updater if no skill for this icon
                    self.battle_ui_updater.remove(icon)

    change_group(self.battle_scale_ui, self.battle_ui_updater, change)
