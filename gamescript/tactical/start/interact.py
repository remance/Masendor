def read_source(self, description_text):
    """Change source description and add new subunit dot when select new source"""
    self.source_description.change_text(description_text)
    self.main_ui_updater.add(self.source_description)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    unit_info = self.read_selected_map_data(openfolder, "unit_pos.csv", source=True)

    team_pos = {row[15]: [] for row in list(unit_info.values())[1:]}
    for row in list(unit_info.values())[1:]:
        team_pos[row[15]].append([int(item) for item in row[8].split(",")])

    self.map_show.change_mode(1, team_pos_list=team_pos)

    team_army = {row[15]: [] for row in list(unit_info.values())[1:]}
    team_leader = {row[15]: [] for row in list(unit_info.values())[1:]}
    for row in list(unit_info.values())[1:]:
        for small_row in row[0:7]:
            for item in small_row.split(","):
                team_army[row[15]].append(int(item))

        for item in row[9].split(","):
            team_leader[row[15]].append(int(item))

    return team_army, team_leader

