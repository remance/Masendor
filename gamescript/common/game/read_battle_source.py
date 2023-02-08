def read_battle_source(self, description_text):
    """Change battle source description and add new subunit dot when select new source"""
    self.source_description.change_text(description_text)
    self.main_ui_updater.add(self.source_description)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    unit_info = self.read_selected_map_data(openfolder, "troop_pos.csv", source=True)
    self.team_pos = {row["Team"]: {"Troop": [], "Leader": []} for row in list(unit_info.values())}
    for row in list(unit_info.values()):
        if type(row["Troop ID"]) is str:
            self.team_pos[row["Team"]]["Leader"].append([int(item) for item in row["POS"].split(",")])
        else:
            self.team_pos[row["Team"]]["Troop"].append([int(item) for item in row["POS"].split(",")])

    self.map_show.change_mode(1, team_pos_list=self.team_pos)

    team_army = {row["Team"]: [] for row in list(unit_info.values())}
    team_leader = {row["Team"]: [] for row in list(unit_info.values())}
    for row in list(unit_info.values()):
        if type(row["Troop ID"]) == str:
            team_leader[row["Team"]].append(row["Troop ID"])
        else:
            team_army[row["Team"]].append(int(row["Troop ID"]))
    return team_army, team_leader
