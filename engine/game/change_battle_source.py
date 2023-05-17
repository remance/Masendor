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
    self.play_map_data = self.preset_map_data[self.map_selected]
    self.play_source_data = self.play_map_data[self.map_source]
    self.source_lore = self.localisation.grab_text(("preset_map", self.battle_campaign[self.map_selected],
                                                    self.map_selected))
    self.source_name_list = [self.localisation.grab_text(key=("preset_map", self.battle_campaign[self.map_selected],
                                                              self.map_selected, "source", key, "Source")) for key in
                             self.play_map_data if key != "source"]

    self.camp_pos = {}
    for key, value in self.play_map_data["source"][self.map_source].items():
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

    # self.source_description.change_text(self.source_text, self.mouse_pos)

    setup_list(uimenu.NameList, self.current_source_row, self.source_name_list,
               self.source_namegroup, self.source_list_box, self.main_ui_updater)

    self.team_pos = {row["Team"]: [] for row in self.play_source_data["unit"]}
    for row in self.play_source_data["unit"]:
        self.team_pos[row["Team"]].append([int(item) for item in row["POS"]])

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
    for key2 in self.play_map_data["source"][self.map_source]:
        if "Team " in key2 and "Camp " not in key2:
            if type(self.play_map_data["source"][self.map_source][key2]) == int:
                self.play_map_data["source"][self.map_source][key2] = [self.play_map_data["source"][self.map_source][key2]]
            elif type(self.play_map_data["source"][self.map_source][key2]) == str:
                self.play_map_data["source"][self.map_source][key2] = [int(item) for item in self.play_map_data["source"][self.map_source][key2].split(",")]
            team_coa.append(self.play_map_data["source"][self.map_source][key2])
    self.create_team_coa(team_coa, self.main_ui_updater)
