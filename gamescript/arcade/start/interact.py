def read_source(self, description_text):
    """Change source description and add new subunit dot when select new source"""
    self.source_description.change_text(description_text)
    self.main_ui.updater.add(self.source_description)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    unit_info = self.read_selected_map_data(openfolder, "unit_pos.csv", source=True)
    print(list(unit_info.values())[1:])
    team1_pos = {row[5]: [int(item) for item in row[5].split(",")] for row in list(unit_info.values()) if
                 row[12] == 1}
    team2_pos = {row[5]: [int(item) for item in row[5].split(",")] for row in list(unit_info.values()) if
                 row[12] == 2}
    self.map_show.change_mode(1, team1_pos_list=team1_pos, team2_pos_list=team2_pos)

    team1_army = []
    team2_army = []
    team1_commander = []
    team2_commander = []
    for row in list(unit_info.values())[1:]:
        if row[12] == 1:
            list_add = team1_army
        elif row[12] == 2:
            list_add = team2_army
        for small_row in row[0:5]:
            for item in small_row.split(","):
                list_add.append(item)

        if row[12] == 1:
            team1_commander.append(row[6])
        elif row[12] == 2:
            team2_commander.append(row[6])

    return team1_army, team2_army, team1_commander, team2_commander