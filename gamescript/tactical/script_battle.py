import numpy as np


def check_split(self, who):
    """Check if unit can be splitted, if not remove splitting button"""
    # v split by middle column
    if np.array_split(who.subunit_list, 2, axis=1)[0].size >= 10 and np.array_split(who.subunit_list, 2, axis=1)[1].size >= 10 and \
            who.leader[1].name != "None":  # can only split if both parentunit size will be larger than 10 and second leader exist
        self.battle_ui.add(self.col_split_button)
    elif self.col_split_button in self.battle_ui:
        self.battle_ui.remove(self.col_split_button)
    # ^ End col

    # v split by middle row
    if np.array_split(who.subunit_list, 2)[0].size >= 10 and np.array_split(who.subunit_list, 2)[1].size >= 10 and \
            who.leader[1].name != "None":
        self.battle_ui.add(self.row_split_button)
    elif self.row_split_button in self.battle_ui:
        self.battle_ui.remove(self.row_split_button)
