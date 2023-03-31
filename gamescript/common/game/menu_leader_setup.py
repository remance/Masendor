import pygame

from gamescript import menu, battleui
from gamescript.common import utility
from gamescript.common.game import menu_preset_team_select

from gamescript.common.game import menu_unit_setup

unit_change_team_unit = menu_unit_setup.unit_change_team_unit
leader_change_team_unit = menu_unit_setup.leader_change_team_unit

change_to_char_select_menu = menu_preset_team_select.change_to_char_select_menu

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image


def menu_leader_setup(self, mouse_left_up, mouse_left_down, mouse_right_up, mouse_right_down,
                      mouse_scroll_up, mouse_scroll_down, esc_press):
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
                        self.org_chart.add_chart(self.custom_map_data["unit"][icon.who.team], self.preview_char,
                                                 selected=icon.who.index)
                    elif mouse_right_up:
                        for other_icon in self.char_icon:
                            if other_icon.right_selected:  # unselected all others first
                                other_icon.selection(how="right")
                        icon.selection(how="right")
                    break

    elif self.org_chart.rect.collidepoint(self.mouse_pos):
        mouse_pos = pygame.Vector2((self.mouse_pos[0] - self.org_chart.rect.topleft[0]),
                                   (self.mouse_pos[1] - self.org_chart.rect.topleft[1]))
        for rect in self.org_chart.node_rect:
            if self.org_chart.node_rect[rect].collidepoint(mouse_pos):
                for icon_index, icon in enumerate(self.char_icon):  # select unit
                    if icon_index == rect:
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

                        if mouse_right_up:
                            for icon2 in self.char_icon:
                                if icon2.right_selected and icon2 is not icon:
                                    self.custom_map_data["unit"][icon2.who.team][icon2.who.index]["Leader"] = icon_index
                                    self.org_chart.add_chart(self.custom_map_data["unit"][icon.who.team],
                                                             self.preview_char,
                                                             selected=icon.who.index)

                        break

    elif mouse_left_up:
        for this_team in self.team_coa:  # User select any team by clicking on coat of arm
            if this_team.rect.collidepoint(self.mouse_pos):
                self.team_selected = this_team.team
                this_team.change_select(True)

                for this_team2 in self.team_coa:
                    if self.team_selected != this_team2.team and this_team2.selected:
                        this_team2.change_select(False)

                leader_change_team_unit(self)
                self.org_chart.add_chart([], self.char_icon)
                break

    if self.map_back_button.event or esc_press:
        self.menu_state = "unit_setup"
        self.map_back_button.event = False
        self.current_map_row = 0
        self.main_ui_updater.remove(self.org_chart)

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

        unit_change_team_unit(self)

    elif self.select_button.event:  # go to character select screen
        change_to_char_select_menu(self)


