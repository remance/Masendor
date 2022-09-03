import numpy as np


def check_split(self):
    """Check if unit can be split, if not remove splitting button.
    Can only split if both unit size will be larger than 10 and second leader exist"""
    # Split by middle column
    if np.array_split(self.subunit_id_array, 2, axis=1)[0].size >= 10 and \
            np.array_split(self.subunit_id_array, 2, axis=1)[1].size >= 10 and \
            self.leader[1].name != "None":
        self.battle.battle_ui_updater.add(self.battle.col_split_button)
    elif self.battle.col_split_button in self.battle.battle_ui_updater:
        self.battle.battle_ui_updater.remove(self.battle.col_split_button)

    # Split by middle row
    if np.array_split(self.subunit_id_array, 2)[0].size >= 10 and np.array_split(self.subunit_id_array, 2)[
        1].size >= 10 and \
            self.leader[1].name != "None":
        self.battle.battle_ui_updater.add(self.battle.row_split_button)
    elif self.battle.row_split_button in self.battle.battle_ui_updater:
        self.battle.battle_ui_updater.remove(self.battle.row_split_button)
