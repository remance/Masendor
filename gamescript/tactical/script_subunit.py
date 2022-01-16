import random


def die(who, battle, morale_hit=True):
    """remove subunit when it dies"""
    if who.team == 1:
        group = battle.team1_unit
        enemy_group = battle.team2_unit
        battle.team1_pos_list.pop(who.game_id)
    else:
        group = battle.team2_unit
        enemy_group = battle.team1_unit
        battle.team2_pos_list.pop(who.game_id)

    if morale_hit:
        if who.commander:  # more morale penalty if the unit is a command unit
            for army in group:
                for this_subunit in army.subunit_sprite:
                    this_subunit.base_morale -= 30

        for this_army in enemy_group:  # get bonus authority to the another army
            this_army.authority += 5

        for this_army in group:  # morale dmg to every subunit in army when allied unit destroyed
            for this_subunit in this_army.subunit_sprite:
                this_subunit.base_morale -= 20

    battle.all_unit_list.remove(who)
    battle.all_unit_index.remove(who.game_id)
    group.remove(who)
    who.got_killed = True


def change_leader(self, event):
    """Leader change subunit or gone/die, event can be "die" or "broken" """
    check_state = [100]
    if event == "broken":
        check_state = [99, 100]
    if self.leader is not None and self.leader.state != 100:  # Find new subunit for leader if there is one in this subunit
        for this_subunit in self.nearby_subunit_list:
            if this_subunit != 0 and this_subunit.state not in check_state and this_subunit.leader is None:
                this_subunit.leader = self.leader
                self.leader.subunit = this_subunit
                for index, subunit2 in enumerate(self.unit.subunit_sprite):  # loop to find new subunit pos based on new subunit_sprite list
                    if subunit2 == self.leader.subunit:
                        self.leader.subunit_pos = index
                        if self.unit_leader:  # set leader subunit to new one
                            self.unit.leader_subunit = subunit2
                            subunit2.unit_leader = True
                            self.unit_leader = False
                        break

                self.leader = None
                break

        if self.leader is not None:  # if can't find near subunit to move leader then find from first subunit to last place in unit
            for index, this_subunit in enumerate(self.unit.subunit_sprite):
                if this_subunit.state not in check_state and this_subunit.leader is None:
                    this_subunit.leader = self.leader
                    self.leader.subunit = this_subunit
                    this_subunit.leader.subunit_pos = index
                    self.leader = None
                    if self.unit_leader:  # set leader subunit to new one
                        self.unit.leader_subunit = this_subunit
                        this_subunit.unit_leader = True

                    break

            if self.leader is not None and event == "die":  # Still can't find new subunit so leader disappear with chance of different result
                self.leader.state = random.randint(97, 100)  # captured, retreated, wounded, dead
                self.leader.health = 0
                self.leader.gone()

        self.unit_leader = False
