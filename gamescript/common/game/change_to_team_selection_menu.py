from gamescript import menu
from gamescript.common import utility

setup_list = utility.setup_list
load_image = utility.load_image


def change_to_team_selection_menu(self):
    self.camp_pos = {}

    setup_list(self.screen_scale, menu.NameList, self.current_source_row, ["None"] +
               self.faction_data.faction_name_list, self.source_namegroup, self.source_list_box, self.main_ui_updater)

    self.menu_button.add(*self.team_select_button)

    self.main_ui_updater.add(*self.team_select_button, self.char_selector, self.char_selector.scroll,
                             self.map_option_box, self.observe_mode_tick_box, self.map_back_button,
                             self.map_select_button, self.source_list_box, self.source_list_box.scroll)

    self.create_team_coa