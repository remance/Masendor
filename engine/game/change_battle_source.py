import os
import csv
from datetime import datetime, timedelta
from engine.uimenu import uimenu
from engine import utility

csv_read = utility.csv_read
setup_list = utility.setup_list
list_scroll = utility.list_scroll
stat_convert = utility.stat_convert


def change_battle_source(self):
    """change map data when select new source"""
    self.map_data = self.read_selected_map_data(self.preset_map_folder, "source" + ".csv")[self.map_source]

    try:
        self.source_list = self.read_selected_map_data(self.preset_map_folder, "source" + ".csv")
        self.source_lore_list = self.read_selected_map_data(self.preset_map_folder, "source_" + self.language + ".csv")
        self.source_name_list = [value["Source"] for value in self.source_lore_list.values()]
        self.source_scale_text = [value["Number Text"] for value in self.source_lore_list.values()]
        self.source_text = [value["Description"] for value in self.source_lore_list.values()]

        with open(os.path.join(self.module_dir, "map", "preset", self.map_selected, str(self.map_source),
                               "troop_pos.csv"), encoding="utf-8", mode="r") as unit_file:
            rd = list(csv.reader(unit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID", "Faction", "Team", "Leader")  # value int only
            list_column = ("POS",)  # value in list only
            float_column = ("Angle", "Start Health", "Start Stamina")  # value in float
            dict_column = ("Troop",)
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            float_column = [index for index, item in enumerate(header) if item in float_column]
            dict_column = [index for index, item in enumerate(header) if item in dict_column]

            for data_index, data in enumerate(rd[1:]):  # skip header
                for n, i in enumerate(data):
                    data = stat_convert(data, n, i, list_column=list_column, int_column=int_column,
                                        float_column=float_column, dict_column=dict_column)
                rd[data_index + 1] = {header[index]: stuff for index, stuff in enumerate(data)}
            troop_data = rd[1:]
        unit_file.close()

        self.map_data["unit"] = troop_data

        self.map_data["info"] = {}
        try:
            weather_event = csv_read(self.module_dir, "weather.csv", ("map", "preset", self.map_selected,
                                                                      str(self.map_source)), output_type="list")
            self.map_data["info"]["weather"] = weather_event[1:]
        except (FileNotFoundError,
                TypeError) as b:  # If no weather found or no map use light sunny weather start at 9:00 and wind direction at 0 angle
            print(b)
            self.map_data["info"]["weather"] = [[1, "09:00:00", 0, 0],]  # default weather light sunny all day

        self.camp_pos = {}
        for key, value in self.source_list[self.map_source].items():
            if "Camp " in key:
                self.camp_pos[int(key[-1])] = value

        for team, pos_list in self.camp_pos.items():
            if ";" in pos_list:
                pos_list = pos_list.split(";")
            else:
                pos_list = [pos_list]
            for index, pos in enumerate(pos_list):
                pos_list[index] = pos.replace("(", "").replace(")", "").split(",")
                pos_list[index] = ((int(pos_list[index][0]), int(pos_list[index][1])), int(pos_list[index][2]))
            self.camp_pos[team] = pos_list
    except FileNotFoundError:  # no source file, crash game
        self.error_log.write("\n No source for map: " + str(self.map_title.name))
        no_source

    # self.source_description.change_text(self.source_text, self.mouse_pos)

    setup_list(uimenu.NameList, self.current_source_row, self.source_name_list,
               self.source_namegroup, self.source_list_box, self.main_ui_updater)

    unit_info = self.read_selected_map_data(self.preset_map_folder, "troop_pos.csv", source=True)
    self.team_pos = {row["Team"]: [] for row in list(unit_info.values())}
    for row in list(unit_info.values()):
        self.team_pos[row["Team"]].append([int(item) for item in row["POS"].split(",")])

    # reset preview mini map
    self.create_preview_map()
    self.map_preview.change_mode(1, team_pos_list=self.team_pos, camp_pos_list=self.camp_pos)

    # Reset character selection UI
    self.unit_select_row = 0

    for icon in self.preview_unit:
        icon.kill()
    self.preview_unit.empty()

    self.setup_battle_unit(self.preview_unit, preview=self.team_selected)

    self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

    for index, icon in enumerate(self.unit_icon):  # select first unit
        self.unit_selected = icon.who.map_id
        icon.selection()
        who_todo = {key: value for key, value in self.leader_data.leader_list.items() if key == icon.who.troop_id}
        preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True)
        self.map_preview.change_mode(1, team_pos_list=self.team_pos, camp_pos_list=self.camp_pos,
                                     selected=icon.who.base_pos)
        self.unit_model_room.add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"],
                                               icon.who.coa)
        break

    team_coa = []
    for key2 in self.map_data:
        if "Team " in key2 and "Camp " not in key2:
            if type(self.map_data[key2]) == int:
                self.map_data[key2] = [self.map_data[key2]]
            elif type(self.map_data[key2]) == str:
                self.map_data[key2] = [int(item) for item in self.map_data[key2].split(",")]
            team_coa.append(self.map_data[key2])
    self.create_team_coa(team_coa, self.main_ui_updater)