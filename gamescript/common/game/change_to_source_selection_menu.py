from gamescript import menu
from gamescript.common import utility

setup_list = utility.setup_list
load_image = utility.load_image


def change_to_source_selection_menu(self):
    for team in self.team_coa:
        if self.team_selected == team.team:
            team.change_select(True)

    openfolder = self.preset_map_folder

    try:
        self.source_list = self.read_selected_map_data(openfolder, "source_" + self.language + ".csv")
        self.source_name_list = [value["Source"] for value in self.source_list.values()]
        self.source_scale_text = [value["Number Text"] for value in self.source_list.values()]
        self.source_text = [value["Description"] for value in self.source_list.values()]

        self.camp_pos = [{int(value2[-1]): value[value2] for value2 in value if "Camp" in value2} for
                         value in self.source_list.values()]
        print(self.camp_pos)
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

    setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.source_name_list,
               self.source_namegroup, self.source_list_box, self.main_ui_updater)

    team_troop, team_leader = self.read_battle_source(
        [self.source_scale_text[self.map_source], self.source_text[self.map_source]])
    self.change_battle_source(team_troop, team_leader)

    self.menu_button.add(*self.team_select_button)
    self.main_ui_updater.add(*self.team_select_button, self.map_option_box, self.observe_mode_tick_box,
                             self.source_list_box, self.source_list_box.scroll, self.army_stat)
