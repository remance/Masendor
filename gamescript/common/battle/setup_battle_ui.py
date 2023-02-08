from gamescript import battleui
from gamescript.common import utility

change_group = utility.change_group


def setup_battle_ui(self, change):
    """Change can be either 'add' or 'remove' for adding or removing ui"""
    if change == "add":
        self.time_ui.change_pos((self.screen_rect.width - self.time_ui.image.get_width(),
                                 0), self.time_number)

        self.battle_scale_ui.change_pos(self.time_ui.rect.bottomleft)

        change_group(self.command_ui, self.battle_ui_updater, change)

    else:
        change_group(self.unit_selector, self.battle_ui_updater, change)
        change_group(self.unit_selector.scroll, self.battle_ui_updater, change)

    change_group(self.battle_scale_ui, self.battle_ui_updater, change)
