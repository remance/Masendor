def read_battle_source(self, description_text):
    """Change battle source description and add new subunit dot when select new source"""
    self.source_description.change_text(description_text)
    self.main_ui_updater.add(self.source_description)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    unit_info = self.read_selected_map_data(openfolder, "unit_pos.csv", source=True)

    self.team_pos = {row["Team"]: [] for row in list(unit_info.values())}
    for row in list(unit_info.values()):
        self.team_pos[row["Team"]].append([int(item) for item in row["POS"].split(",")])

    self.map_show.change_mode(1, team_pos_list=self.team_pos)

    team_army = {row["Team"]: [] for row in list(unit_info.values())[1:]}
    team_leader = {row["Team"]: [] for row in list(unit_info.values())[1:]}
    for row in list(unit_info.values())[1:]:
        for small_row in [value for key, value in row.items() if "Row" in key]:
            for item in small_row.split(","):
                if item.isdigit():
                    team_army[row["Team"]].append(int(item))
                else:
                    team_army[row["Team"]].append(item)
            if type(row["Leader"]) == str and "," in row["Leader"]:
                for item in row["Leader"].split(","):
                    team_leader[row["Team"]].append(int(item))
            else:
                team_leader[row["Team"]].append(int(row["Leader"]))

    return team_army, team_leader
