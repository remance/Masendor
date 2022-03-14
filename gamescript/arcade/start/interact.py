def read_source(self, description_text):
    """Change source description and add new subunit dot when select new source"""
    self.source_description.change_text(description_text)
    self.main_ui_updater.add(self.source_description)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    unit_info = self.read_selected_map_data(openfolder, "unit_pos.csv", source=True)

    team_pos = {row[12]: [] for row in list(unit_info.values())[1:]}
    for row in list(unit_info.values())[1:]:
        team_pos[row[12]].append([int(item) for item in row[5].split(",")])

    self.map_show.change_mode(1, team_pos_list=team_pos)

    team_army = {row[12]: [] for row in list(unit_info.values())[1:]}
    team_leader = {row[12]: [] for row in list(unit_info.values())[1:]}
    for row in list(unit_info.values())[1:]:
        for small_row in row[0:5]:
            for item in small_row.split(","):
                if item.isdigit():
                    team_army[row[12]].append(int(item))
                else:
                    team_army[row[12]].append(item)

            team_leader[row[12]].append(int(row[6]))

    return team_army, team_leader