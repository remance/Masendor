def change_source(self, description_text, scale_value):
    """Change source description, add new subunit dot, change army stat when select new source"""
    self.source_description.change_text(description_text)
    self.main_ui.add(self.source_description)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    unit_info = self.read_selected_map_data(openfolder, "unit_pos.csv", source=True)

    team1_pos = {row[8]: [int(item) for item in row[8].split(",")] for row in list(unit_info.values()) if
                 row[15] == 1}
    team2_pos = {row[8]: [int(item) for item in row[8].split(",")] for row in list(unit_info.values()) if
                 row[15] == 2}
    self.map_show.change_mode(1, team1_pos_list=team1_pos, team2_pos_list=team2_pos)

    team1_army = []
    team2_army = []
    team1_commander = []
    team2_commander = []
    for row in list(unit_info.values())[1:]:
        if row[15] == 1:
            list_add = team1_army
        elif row[15] == 2:
            list_add = team2_army
        for small_row in row[0:7]:
            for item in small_row.split(","):
                list_add.append(int(item))

        for item in row[9].split(","):
            if row[15] == 1:
                team1_commander.append(int(item))
            elif row[15] == 2:
                team2_commander.append(int(item))

    team_total_troop = [0, 0]  # total troop number in army
    troop_type_list = [[0, 0, 0, 0], [0, 0, 0, 0]]  # total number of each troop type
    leader_name_list = (team1_commander, team2_commander)
    army_team_list = (team1_pos, team2_pos)  # for finding how many subunit in each team

    army_loop_list = (team1_army, team2_army)
    for index, team in enumerate(army_loop_list):
        for this_unit in team:
            if this_unit != 0:
                team_total_troop[index] += int(self.troop_data.troop_list[this_unit]["Troop"] * scale_value[index])
                troop_type = 0
                if self.troop_data.troop_list[this_unit]["Troop Class"] in (2, 4):  # range subunit
                    troop_type += 1  # range weapon and accuracy higher than melee attack
                if self.troop_data.troop_list[this_unit]["Troop Class"] in (3, 4, 5, 6, 7):  # cavalry
                    troop_type += 2
                troop_type_list[index][troop_type] += int(
                    self.troop_data.troop_list[this_unit]["Troop"] * scale_value[index])
        troop_type_list[index].append(len(army_team_list[index]))

    army_loop_list = ["{:,}".format(troop) + " Troops" for troop in team_total_troop]
    army_loop_list = [self.leader_stat.leader_list[leader_name_list[index][0]]["Name"] + ": " + troop for index, troop in enumerate(army_loop_list)]

    for index, army in enumerate(self.army_stat):
        army.add_stat(troop_type_list[index], army_loop_list[index])