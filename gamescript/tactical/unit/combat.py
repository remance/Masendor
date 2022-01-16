def destroyed(self, battle, morale_hit=True):
    """remove unit when it dies"""
    if self.team == 1:
        group = battle.team1_unit
        enemy_group = battle.team2_unit
        battle.team1_pos_list.pop(self.game_id)
    else:
        group = battle.team2_unit
        enemy_group = battle.team1_unit
        battle.team2_pos_list.pop(self.game_id)

    if morale_hit:
        if self.commander:  # more morale penalty if the unit is a command unit
            for army in group:
                for this_subunit in army.subunit_sprite:
                    this_subunit.base_morale -= 30

        for this_army in enemy_group:  # get bonus authority to the another army
            this_army.authority += 5

        for this_army in group:  # morale dmg to every subunit in army when allied unit destroyed
            for this_subunit in this_army.subunit_sprite:
                this_subunit.base_morale -= 20

    battle.all_unit_list.remove(self)
    battle.all_unit_index.remove(self.game_id)
    group.remove(self)
    self.got_killed = True