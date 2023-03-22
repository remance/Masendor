from gamescript import menu
from gamescript.common import utility

setup_list = utility.setup_list
load_image = utility.load_image


def change_to_team_selection_menu(self):
    self.camp_pos = {}
    if self.last_select == "custom":
        openfolder = self.custom_map_folder

    self.main_ui_updater.add(*self.team_select_button, self.map_option_box, self.observe_mode_tick_box)