def destroyed(self, morale_hit=True):
    """remove unit when it dies"""
    group = self.battle.all_team_unit[self.team]
    enemy_group = [this_unit for this_unit in self.battle.all_team_unit["alive"] if this_unit.team != self.team]

    self.battle.team_pos_list[self.team].pop(self)

    if morale_hit:
        if self.commander:  # more morale penalty if the unit is a command unit
            for army in group:
                for this_subunit in army.subunits:
                    this_subunit.base_morale -= 30

        for this_army in enemy_group:  # get bonus authority to the another army
            this_army.authority += 5

        for this_army in group:  # morale dmg to every subunit in army when allied unit destroyed
            for this_subunit in this_army.subunits:
                this_subunit.base_morale -= 20

    self.battle.all_team_unit["alive"].remove(self)
    group.remove(self)
    self.got_killed = True

    self.battle.unit_selector.setup_unit_icon(self.battle.unit_icon,
                                              self.battle.all_team_unit[self.battle.team_selected])  # reset unit icon (remove dead one)
