def destroyed(self, morale_hit=True):
    """remove unit when it dies"""
    group = self.battle.all_team_unit[self.team]
    enemy_group = [this_unit for this_unit in self.battle.all_team_unit["alive"] if this_unit.team != self.team]
    self.battle.team_pos_list[self.team].pop(self)

    if morale_hit:
        if self.commander:  # more morale penalty if the unit is a command unit
            for this_unit in group:
                for this_subunit in this_unit.subunit_list:
                    this_subunit.base_morale -= 30

        for this_unit in enemy_group:  # get bonus authority to the another army
            this_unit.authority += 5

        for this_unit in group:  # morale dmg to every subunit in army when allied unit destroyed
            for this_subunit in this_unit.subunit_list:
                this_subunit.base_morale -= 20

    self.battle.all_team_unit["alive"].remove(self)
    group.remove(self)
    self.got_killed = True
