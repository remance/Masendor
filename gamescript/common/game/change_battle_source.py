def change_battle_source(self, team_troop, team_commander):
    """change army stat when select new source"""

    team_total_troop = {key: 0 for key in team_troop.keys()}  # total troop number in army
    troop_type_list = {key: [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]] for key in
                       team_troop.keys()}  # total number of each troop type
    leader_name_list = {key: leader[0] for key, leader in team_commander.items()}

    for index, team in team_troop.items():
        for this_troop in team:
            team_total_troop[index] += team[this_troop][0]
            team_total_troop[index] += team[this_troop][1]
            troop_type = 0
            if self.troop_data.troop_list[this_troop]["Troop Class"] in (
            "Range Infantry", "Range Cavalry", "Artillery"):  # range subunit
                troop_type += 1  # range weapon and accuracy higher than melee melee_attack
            if self.troop_data.troop_list[this_troop]["Troop Class"] in (
            "Light Cavalry", "Heavy Cavalry", "Chariot"):  # cavalry
                troop_type += 2
            troop_type_list[index][troop_type][0] += team[this_troop][0]
            troop_type_list[index][troop_type][1] += int(team[this_troop][1])
            # add total
            troop_type_list[index][-1][0] += team[this_troop][0]
            troop_type_list[index][-1][1] += int(team[this_troop][1])

    army_loop_list = {key: self.leader_data.leader_list[leader_name_list[key]]["Name"]
                      for key in team_total_troop}
    self.army_stat.add_army_stat(troop_type_list[self.team_selected], army_loop_list[self.team_selected])
