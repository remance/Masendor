import pygame

from gamescript import menu
from gamescript.common import utility
from gamescript.common.game import menu_preset_map_select
from gamescript.common.game import menu_unit_setup

unit_change_team_unit = menu_unit_setup.unit_change_team_unit
leader_change_team_unit = menu_unit_setup.leader_change_team_unit

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image


def menu_leader_setup(self, mouse_left_up, mouse_left_down, mouse_right_up, mouse_right_down,
                      mouse_scroll_up, mouse_scroll_down, esc_press):
    self.main_ui_updater.remove(self.single_text_popup)
    if self.unit_selector.rect.collidepoint(self.mouse_pos):
        if mouse_scroll_up:
            if self.unit_selector.current_row > 0:
                self.unit_selector.current_row -= 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                for this_team in self.team_coa:
                    if this_team.selected:
                        preview_char = [char for char in self.preview_unit if "Temp Leader" not in
                                        self.custom_map_data["unit"][this_team.team][char.index] or
                                        self.custom_map_data["unit"][this_team.team][char.index]["Temp Leader"] == ""]
                        self.unit_selector.setup_unit_icon(self.unit_icon, preview_char)
                        break

        elif mouse_scroll_down:
            if self.unit_selector.current_row < self.unit_selector.row_size:
                self.unit_selector.current_row += 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                for this_team in self.team_coa:
                    if this_team.selected:
                        preview_char = [char for char in self.preview_unit if "Temp Leader" not in
                                        self.custom_map_data["unit"][this_team.team][char.index] or
                                        self.custom_map_data["unit"][this_team.team][char.index]["Temp Leader"] == ""]
                        self.unit_selector.setup_unit_icon(self.unit_icon, preview_char)
                        break

        elif self.unit_selector.scroll.rect.collidepoint(self.mouse_pos):
            if mouse_left_down or mouse_left_up:
                new_row = self.unit_selector.scroll.player_input(self.mouse_pos)
                if self.unit_selector.current_row != new_row:
                    self.unit_selector.current_row = new_row
                    self.unit_selector.scroll.change_image(new_row=new_row, row_size=self.unit_selector.row_size)
                    for this_team in self.team_coa:
                        if this_team.selected:
                            preview_char = [char for char in self.preview_unit if "Temp Leader" not in
                                            self.custom_map_data["unit"][this_team.team][char.index] or
                                            self.custom_map_data["unit"][this_team.team][char.index][
                                                "Temp Leader"] == ""]
                            self.unit_selector.setup_unit_icon(self.unit_icon, preview_char)
                            break

        else:
            for char in self.unit_icon:  # select unit
                if char.rect.collidepoint(self.mouse_pos):
                    if char.who.name != "+":  # add popup showing leader and troop in unit
                        popup_text = [self.leader_data.leader_list[
                                          self.custom_map_data["unit"][char.who.team][char.who.index]["Leader ID"]][
                                          "Name"]]
                        for troop in self.custom_map_data["unit"][char.who.team][char.who.index]["Troop"]:
                            popup_text += [self.troop_data.troop_list[troop]["Name"] + ": " +
                                           str(self.custom_map_data["unit"][char.who.team][char.who.index]["Troop"][
                                                   troop][0]) + " + " +
                                           str(self.custom_map_data["unit"][char.who.team][char.who.index]["Troop"][
                                                   troop][1])]
                        self.single_text_popup.pop(self.mouse_pos, popup_text)
                        self.main_ui_updater.add(self.single_text_popup)
                    if mouse_left_up:
                        for other_icon in self.unit_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        char.selection()
                        if char.who.team in self.custom_map_data["unit"]["pos"] and \
                                char.who.index in self.custom_map_data["unit"]["pos"][char.who.team]:
                            # highlight unit in preview map
                            self.map_preview.change_mode(1, team_pos_list=self.custom_map_data["unit"]["pos"],
                                                         camp_pos_list=self.camp_pos[0],
                                                         selected=
                                                         self.custom_map_data["unit"]["pos"][char.who.team][
                                                             char.who.index])
                        self.org_chart.add_chart(self.custom_map_data["unit"][char.who.team], self.preview_unit,
                                                 selected=char.who.index)
                    elif mouse_right_up:
                        for other_icon in self.unit_icon:
                            if other_icon.right_selected:  # unselected all others first
                                other_icon.selection(how="right")
                        char.selection(how="right")
                    break

    elif self.org_chart.rect.collidepoint(self.mouse_pos):
        mouse_pos = pygame.Vector2((self.mouse_pos[0] - self.org_chart.rect.topleft[0]),
                                   (self.mouse_pos[1] - self.org_chart.rect.topleft[1]))
        for rect in self.org_chart.node_rect:  # check for mouse on node in org chart
            if self.org_chart.node_rect[rect].collidepoint(mouse_pos):
                not_in_list = True
                for subunit_index, subunit in enumerate(self.preview_unit):  # check for unit in icon
                    if subunit_index == rect:  # found unit for data
                        popup_text = [self.leader_data.leader_list[
                                          self.custom_map_data["unit"][subunit.team][subunit.index]["Leader ID"]][
                                          "Name"]]
                        for troop in self.custom_map_data["unit"][subunit.team][subunit.index]["Troop"]:
                            popup_text += [self.troop_data.troop_list[troop]["Name"] + ": " +
                                           str(self.custom_map_data["unit"][subunit.team][subunit.index]["Troop"][
                                                   troop][0]) + " + " +
                                           str(self.custom_map_data["unit"][subunit.team][subunit.index]["Troop"][
                                                   troop][1])]
                        self.single_text_popup.pop(self.mouse_pos, popup_text)
                        self.main_ui_updater.add(self.single_text_popup)

                        if mouse_right_up:
                            for subunit2 in self.unit_icon:
                                if subunit2.right_selected and subunit2 is not subunit:
                                    not_in_list = False
                                    self.custom_map_data["unit"][subunit2.who.team][subunit2.who.index][
                                        "Temp Leader"] = subunit.index
                                    for subunit3_index, subunit3 in enumerate(self.unit_icon):
                                        if subunit3.selected:
                                            unit_change_team_unit(self, add_plus=False, old_selected=subunit3.who.index)
                                            self.org_chart.add_chart(self.custom_map_data["unit"][subunit.team],
                                                                     self.preview_unit,
                                                                     selected=subunit3.who.index)
                                            break
                                    break
                        break

                if mouse_right_up and not_in_list:  # remove unit's leader in org chart
                    self.custom_map_data["unit"][subunit.team][rect]["Temp Leader"] = ""
                    for subunit3_index, subunit3 in enumerate(self.unit_icon):
                        if subunit3.selected:
                            unit_change_team_unit(self, add_plus=False, old_selected=subunit3.who.index)
                            self.org_chart.add_chart(self.custom_map_data["unit"][subunit.team],
                                                     self.preview_unit,
                                                     selected=subunit3_index)
                            break
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
                self.org_chart.add_chart([], self.preview_unit)
                break

    if self.map_back_button.event or esc_press:
        self.main_ui_updater.remove(self.single_text_popup)
        self.menu_state = "unit_setup"
        self.map_back_button.event = False
        self.current_map_row = 0
        self.main_ui_updater.remove(self.org_chart)

        for subunit in self.preview_unit:  # reset leader
            self.custom_map_data["unit"][subunit.team][subunit.index]["Temp Leader"] = ""
        leader_change_team_unit(self)
        self.org_chart.add_chart([], self.preview_unit)  # reset chart

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
        self.team_pos = {team: [pos for pos in self.custom_map_data["unit"]["pos"][team].values()] for
                         team in self.custom_map_data["unit"]["pos"]}

        subunit_index = 1
        for team in self.custom_map_data["unit"]:
            if team != "pos":
                for index, subunit in enumerate(self.custom_map_data["unit"][team]):
                    subunit["ID"] = subunit_index
                    subunit["Angle"] = 0
                    subunit["Start Health"] = 100
                    subunit["Start Stamina"] = 100
                    subunit["Team"] = team
                    subunit["POS"] = self.custom_map_data["unit"]["pos"][team][index]
                    subunit_index += 1

        for team in self.custom_map_data["unit"]:
            if team != "pos":
                for subunit in self.custom_map_data["unit"][team]:  # assign leader based on ID instead
                    temp_leader = subunit["Temp Leader"]
                    subunit["Leader"] = 0
                    if temp_leader != "":
                        subunit["Leader"] = self.custom_map_data["unit"][team][temp_leader]["ID"]

        for icon in self.preview_unit:
            icon.kill()
        self.preview_unit.empty()
        self.main_ui_updater.remove(self.org_chart)

        self.custom_map_data["battle"] = []
        for team, team_data in self.custom_map_data["unit"].items():
            if team != "pos":
                for value in team_data:
                    new_value = {key: {key2: val2.copy() for key2, val2 in val.items()} if type(val) is dict else val
                                 for key, val in value.items()}
                    for troop in new_value["Troop"]:
                        troop_value = new_value["Troop"][troop]
                        new_value["Troop"][troop] = str(troop_value[0]) + "/" + str(troop_value[1])
                    self.custom_map_data["battle"].append(new_value)

        change_to_char_select_menu(self, custom_data=self.custom_map_data["battle"])


def change_to_char_select_menu(self, custom_data=None):
    self.menu_state = "char_select"
    self.select_button.event = False
    self.unit_select_row = 0

    self.main_ui_updater.remove(*self.map_select_button, self.map_option_box, self.source_list_box,
                                self.observe_mode_tick_box, self.source_list_box.scroll,
                                self.source_description, self.army_stat)
    self.menu_button.remove(*self.map_select_button)

    for group in (self.source_namegroup,):  # remove no longer related sprites in group
        for stuff in group:
            stuff.kill()
            del stuff

    self.main_ui_updater.remove(self.team_coa)

    self.unit_stat["unit"] = menu.ArmyStat(self.screen_scale,
                                           (self.screen_rect.center[0] / 9, self.screen_rect.height / 8),
                                           load_image(self.main_dir, self.screen_scale,
                                                      "unit_stat.png", ("ui", "mapselect_ui")))  # unit stat
    self.unit_stat["model"] = menu.ArmyStat(self.screen_scale,
                                            (self.screen_rect.center[0] * 1.3, self.screen_rect.height / 8),
                                            load_image(self.main_dir, self.screen_scale,
                                                       "unit_stat.png", ("ui", "mapselect_ui")))  # troop stat

    self.setup_battle_troop(self.preview_unit, specific_team=self.team_selected, custom_data=custom_data)

    self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

    for index, icon in enumerate(self.unit_icon):  # select first unit
        self.unit_selected = icon.who.map_id
        icon.selection()
        self.unit_stat["unit"].add_leader_stat(icon.who, self.leader_data, self.troop_data)
        who_todo = {key: value for key, value in self.leader_data.leader_list.items() if key == icon.who.troop_id}
        preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True)
        self.unit_stat["model"].add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"], icon.who.coa)
        self.map_preview.change_mode(1, team_pos_list=self.team_pos, camp_pos_list=self.camp_pos[self.map_source],
                                     selected=icon.who.base_pos)
        break

    self.main_ui_updater.add(self.unit_selector, self.unit_selector.scroll,
                             tuple(self.unit_stat.values()), *self.unit_select_button)
    self.menu_button.add(*self.unit_select_button)
