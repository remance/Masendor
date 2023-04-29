from gamescript.common import utility

csv_read = utility.csv_read

stat_convert = utility.stat_convert


def read_battle_source(self, description_text):
    """Change battle source description and add new unit dot when select new source"""
    self.source_description.change_text(description_text)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    unit_info = self.read_selected_map_data(openfolder, "troop_pos.csv", source=True)
    self.team_pos = {row["Team"]: [] for row in list(unit_info.values())}
    for row in list(unit_info.values()):
        self.team_pos[row["Team"]].append([int(item) for item in row["POS"].split(",")])

    self.map_preview.change_mode(1, team_pos_list=self.team_pos, camp_pos_list=self.camp_pos[self.map_source])

    team_troop = {row["Team"]: {} for row in list(unit_info.values())}
    team_leader = {row["Team"]: [] for row in list(unit_info.values())}
    for row in list(unit_info.values()):
        team_leader[row["Team"]].append(row["Leader ID"])
        if row["Troop"]:
            for item in row["Troop"].split(","):
                troop_id = int(item.split(":")[0])
                number = item.split(":")[1].split("/")
                if troop_id not in team_troop[row["Team"]]:
                    team_troop[row["Team"]][troop_id] = [0, 0]
                team_troop[row["Team"]][troop_id][0] += int(number[0])
                team_troop[row["Team"]][troop_id][1] += int(number[1])
    return team_troop, team_leader
