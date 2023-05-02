from gamescript import menu
from gamescript.common import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll


def change_battle_source(self):
    """change army stat when select new source"""

    try:
        self.source_list = self.read_selected_map_data(self.preset_map_folder, "source" + ".csv")
        self.source_lore_list = self.read_selected_map_data(self.preset_map_folder, "source_" + self.language + ".csv")
        self.source_name_list = [value["Source"] for value in self.source_lore_list.values()]
        self.source_scale_text = [value["Number Text"] for value in self.source_lore_list.values()]
        self.source_text = [value["Description"] for value in self.source_lore_list.values()]

        self.camp_pos = [{int(key[-1]): value} for
                         key, value in self.source_list[self.map_source].items() if "Camp" in key]
        for value in self.camp_pos:
            for team, pos_list in value.items():
                if ";" in pos_list:
                    pos_list = pos_list.split(";")
                else:
                    pos_list = [pos_list]
                for index, pos in enumerate(pos_list):
                    pos_list[index] = pos.replace("(", "").replace(")", "").split(",")
                    pos_list[index] = ((int(pos_list[index][0]), int(pos_list[index][1])), int(pos_list[index][2]))
                value[team] = pos_list
    except FileNotFoundError:  # no source file, crash game
        self.error_log.write("\n No source for map: " + str(self.map_title.name))
        no_source

    self.source_description.change_text(self.source_text)

    setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.source_name_list,
               self.source_namegroup, self.source_list_box, self.main_ui_updater)

    unit_info = self.read_selected_map_data(self.preset_map_folder, "troop_pos.csv", source=True)
    self.team_pos = {row["Team"]: [] for row in list(unit_info.values())}
    for row in list(unit_info.values()):
        self.team_pos[row["Team"]].append([int(item) for item in row["POS"].split(",")])

    # reset preview mini map
    self.map_preview.change_mode(1, team_pos_list=self.team_pos, camp_pos_list=self.camp_pos[self.map_source])

    # Reset character selection UI
    self.unit_select_row = 0

    for icon in self.preview_unit:
        icon.kill()
    self.preview_unit.empty()

    self.setup_battle_unit(self.preview_unit, preview=self.team_selected, custom_data=None)

    self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

    for index, icon in enumerate(self.unit_icon):  # select first unit
        self.unit_selected = icon.who.map_id
        icon.selection()
        who_todo = {key: value for key, value in self.leader_data.leader_list.items() if key == icon.who.troop_id}
        preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True)
        self.map_preview.change_mode(1, team_pos_list=self.team_pos, camp_pos_list=self.camp_pos[self.map_source],
                                     selected=icon.who.base_pos)
        self.unit_model_room.add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"],
                                               icon.who.coa)
        break
