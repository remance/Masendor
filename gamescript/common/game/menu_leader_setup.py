import pygame

from gamescript import menu, battleui
from gamescript.common import utility
from gamescript.common.game import menu_preset_team_select

change_to_char_select_menu = menu_preset_team_select.change_to_char_select_menu

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image


def menu_leader_setup(self, mouse_left_up, mouse_left_down, mouse_right_up, mouse_scroll_up, mouse_scroll_down, esc_press):
    self.main_ui_updater.remove(self.single_text_popup)
    if self.char_selector.rect.collidepoint(self.mouse_pos):
        if mouse_scroll_up:
            if self.char_selector.current_row > 0:
                self.char_selector.current_row -= 1
                self.char_selector.scroll.change_image(new_row=self.char_selector.current_row,
                                                       row_size=self.char_selector.row_size)
                self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

        elif mouse_scroll_down:
            if self.char_selector.current_row < self.char_selector.row_size:
                self.char_selector.current_row += 1
                self.char_selector.scroll.change_image(new_row=self.char_selector.current_row,
                                                       row_size=self.char_selector.row_size)
                self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

        elif self.char_selector.scroll.rect.collidepoint(self.mouse_pos):
            if mouse_left_down or mouse_left_up:
                new_row = self.char_selector.scroll.player_input(self.mouse_pos)
                if self.char_selector.current_row != new_row:
                    self.char_selector.current_row = new_row
                    self.char_selector.scroll.change_image(new_row=new_row, row_size=self.char_selector.row_size)
                    self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

        else:
            for icon in self.char_icon:  # select unit
                if icon.rect.collidepoint(self.mouse_pos):
                    if icon.who.name != "+":  # add popup showing leader and troop in subunit
                        popup_text = [self.leader_data.leader_list[
                                          self.custom_map_data["unit"][icon.who.team][icon.who.index]["Leader ID"]][
                                          "Name"]]
                        for troop in self.custom_map_data["unit"][icon.who.team][icon.who.index]["Troop"]:
                            popup_text += [self.troop_data.troop_list[troop]["Name"] + ": " +
                                           str(self.custom_map_data["unit"][icon.who.team][icon.who.index]["Troop"][
                                                   troop][0]) + " + " +
                                           str(self.custom_map_data["unit"][icon.who.team][icon.who.index]["Troop"][
                                                   troop][1])]
                        self.single_text_popup.pop(self.mouse_pos, popup_text)
                        self.main_ui_updater.add(self.single_text_popup)
                    if mouse_left_up:
                        for other_icon in self.char_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                        if icon.who.team in self.custom_map_data["unit"]["pos"] and \
                                icon.who.index in self.custom_map_data["unit"]["pos"][icon.who.team]:
                            # highlight unit in preview map
                            self.map_preview.change_mode(1, team_pos_list=self.custom_map_data["unit"]["pos"],
                                                         camp_pos_list=self.camp_pos[0],
                                                         selected=
                                                         self.custom_map_data["unit"]["pos"][icon.who.team][icon.who.index])
                    break

    elif mouse_left_up:
        for this_team in self.team_coa:  # User select any team by clicking on coat of arm
            if this_team.rect.collidepoint(self.mouse_pos):
                self.team_selected = this_team.team
                this_team.change_select(True)

                for this_team2 in self.team_coa:
                    if self.team_selected != this_team2.team and this_team2.selected:
                        this_team2.change_select(False)

                change_team_unit(self)
                break

    if self.map_back_button.event or esc_press:
        self.menu_state = "unit_setup"
        self.map_back_button.event = False
        self.current_map_row = 0
        self.main_ui_updater.remove(*self.menu_button, self.unit_list_box, self.unit_list_box.scroll,
                                    self.char_icon)
        self.menu_button.remove(*self.menu_button)

        self.main_ui_updater.add(self.unit_list_box, self.unit_list_box.scroll)
        for coa in self.team_coa:
            if coa.selected:  # get unit for selected team
                unit_list = []
                for faction in coa.coa_images:
                    if faction == 0:  # all faction
                        for this_faction in self.faction_data.faction_unit_list:
                            unit_list += list(self.faction_data.faction_unit_list[this_faction].keys())
                    else:
                        unit_list += list(self.faction_data.faction_unit_list[faction].keys())

                    unit_list = sorted((set(unit_list)), key=unit_list.index)

                setup_list(self.screen_scale, menu.NameList, self.current_map_row, unit_list,
                           self.map_namegroup, self.unit_list_box, self.main_ui_updater)
                break

    elif self.select_button.event:  # go to character select screen
        change_to_char_select_menu(self)


def change_team_unit(self):
    for this_team in self.team_coa:
        if this_team.selected:
            for icon in self.preview_char:
                icon.kill()
            self.preview_char.empty()

            if this_team.team in self.custom_map_data["unit"]:
                for unit_index, unit in enumerate(self.custom_map_data["unit"][this_team.team]):
                    if unit["Leader ID"] in self.leader_data.images:
                        image = self.leader_data.images[unit["Leader ID"]]
                    else:
                        image = unit["Leader ID"]

                    self.preview_char.add(battleui.TempCharIcon(self.screen_scale, this_team.team, image, unit_index))

            self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

            break
