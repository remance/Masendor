def assign_commander(self, replace=None):
    """
    :param self: Unit object
    :param replace: New unit that is replaced as the new commander
    :return:
    """
    if replace is not None:
        self.commander = True
        self.team_commander = replace.leader[0]
    else:
        self.commander = False
        self.team_commander = self.leader[0]
        for this_unit in self.battle.all_team_unit[self.team]:
            this_unit.team_commander = self.leader[0]
