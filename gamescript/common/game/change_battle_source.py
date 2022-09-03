def change_battle_source(self, scale_value, team_army, team_commander):
    """change army stat when select new source"""

    self.unit_scale = scale_value

    team_total_troop = {key: 0 for key in team_army.keys()}  # total troop number in army
    troop_type_list = {key: [0, 0, 0, 0] for key in team_army.keys()}  # total number of each troop type
    leader_name_list = {key: leader[0] for key, leader in team_commander.items()}

    for index, team in team_army.items():
        for this_unit in team:
            if this_unit != 0 and type(this_unit) != str:
                team_total_troop[index] += self.troop_data.troop_list[this_unit]["Troop"] * scale_value[index]
                troop_type = 0
                if self.troop_data.troop_list[this_unit]["Troop Class"] in (2, 4):  # range subunit
                    troop_type += 1  # range weapon and accuracy higher than melee melee_attack
                if self.troop_data.troop_list[this_unit]["Troop Class"] in (3, 4, 5, 6, 7):  # cavalry
                    troop_type += 2
                troop_type_list[index][troop_type] += int(
                    self.troop_data.troop_list[this_unit]["Troop"] * scale_value[index])
        troop_type_list[index].append(len(team))

    army_loop_list = {key: "{:,}".format(troop) + " Troops" for key, troop in team_total_troop.items()}
    army_loop_list = {key: self.leader_data.leader_list[leader_name_list[index]]["Name"] + ": " + troop for key, troop
                      in
                      army_loop_list.items()}

    for index, army in enumerate(self.army_stat):  # + 1 index to skip neutral unit in stat
        army.add_army_stat(troop_type_list[index + 1], army_loop_list[index + 1])
