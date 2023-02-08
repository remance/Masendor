def change_battle_source(self, scale_value, team_army, team_commander):
    """change army stat when select new source"""

    self.unit_scale = scale_value

    team_total_troop = {key: 0 for key in team_army.keys()}  # total troop number in army
    troop_type_list = {key: [0, 0, 0, 0] for key in team_army.keys()}  # total number of each troop type
    leader_name_list = {key: leader[0] for key, leader in team_commander.items()}

    for index, team in team_army.items():
        for this_troop in team:
            team_total_troop[index] += 1
            troop_type = 0
            if self.troop_data.troop_list[this_troop]["Troop Class"] in ("Range Infantry", "Range Cavalry", "Artillery"):  # range subunit
                troop_type += 1  # range weapon and accuracy higher than melee melee_attack
            if self.troop_data.troop_list[this_troop]["Troop Class"] in ("Light Cavalry", "Heavy Cavalry", "Chariot"):  # cavalry
                troop_type += 2
            troop_type_list[index][troop_type] += 1

    army_loop_list = {key: self.leader_data.leader_list[leader_name_list[key]]["Name"] + ": " +
                           "{:,}".format(int(troop)) + " Troops" for key, troop in team_total_troop.items()}
    for index, army in enumerate(self.army_stat):  # + 1 index to skip neutral unit in stat
        army.add_army_stat(troop_type_list[index + 1], army_loop_list[index + 1])
