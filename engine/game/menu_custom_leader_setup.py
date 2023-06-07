import pygame

from engine.utility import setup_list
from engine.game import menu_custom_unit_setup
from engine.game import menu_preset_map_select
from engine.uimenu import uimenu

leader_popup_text = menu_preset_map_select.leader_popup_text
unit_change_team_unit = menu_custom_unit_setup.unit_change_team_unit
leader_change_team_unit = menu_custom_unit_setup.leader_change_team_unit


def menu_custom_leader_setup(self, esc_press):
    if self.unit_selector.mouse_over:
        if self.cursor.scroll_up:
            if self.unit_selector.current_row > 0:
                self.unit_selector.current_row -= 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                for this_team in self.team_coa:
                    if this_team.selected:
                        preview_char = [char for char in self.preview_unit if "Temp Leader" not in
                                        self.play_map_data["unit"][this_team.team][char.index] or
                                        self.play_map_data["unit"][this_team.team][char.index]["Temp Leader"] == ""]
                        self.unit_selector.setup_unit_icon(self.unit_icon, preview_char)
                        break

        elif self.cursor.scroll_down:
            if self.unit_selector.current_row < self.unit_selector.row_size:
                self.unit_selector.current_row += 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                for this_team in self.team_coa:
                    if this_team.selected:
                        preview_char = [char for char in self.preview_unit if "Temp Leader" not in
                                        self.play_map_data["unit"][this_team.team][char.index] or
                                        self.play_map_data["unit"][this_team.team][char.index]["Temp Leader"] == ""]
                        self.unit_selector.setup_unit_icon(self.unit_icon, preview_char)
                        break

        elif self.unit_selector.scroll.event:
            new_row = self.unit_selector.scroll.player_input(self.cursor.mouse_pos)
            if self.unit_selector.current_row != new_row:
                self.unit_selector.current_row = new_row
                self.unit_selector.scroll.change_image(new_row=new_row, row_size=self.unit_selector.row_size)
                for this_team in self.team_coa:
                    if this_team.selected:
                        preview_char = [char for char in self.preview_unit if "Temp Leader" not in
                                        self.play_map_data["unit"][this_team.team][char.index] or
                                        self.play_map_data["unit"][this_team.team][char.index][
                                            "Temp Leader"] == ""]
                        self.unit_selector.setup_unit_icon(self.unit_icon, preview_char)
                        break

        else:
            for unit in self.unit_icon:
                if unit.mouse_over:
                    popup_text = leader_popup_text(self, unit)
                    self.text_popup.popup(self.cursor.rect, popup_text)
                    self.add_ui_updater(self.text_popup)
                    if unit.event_press:  # select unit
                        for other_icon in self.unit_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        unit.selection()
                        self.unit_selected = unit.who.map_id
                        print(self.unit_selected)
                        if unit.who.team in self.play_map_data["unit"]["pos"] and \
                                unit.who.index in self.play_map_data["unit"]["pos"][unit.who.team]:
                            # highlight unit in preview map
                            self.map_preview.change_mode(1, team_pos_list=self.play_map_data["unit"]["pos"],
                                                         camp_pos_list=self.play_map_data["camp_pos"],
                                                         selected=
                                                         self.play_map_data["unit"]["pos"][unit.who.team][
                                                             unit.who.index])
                        self.org_chart.add_chart([unit2 for unit2 in self.play_source_data["unit"] if
                                                  unit2["Team"] == unit.team], self.preview_unit,
                                                 selected=unit.who.index)
                    elif self.cursor.is_alt_select_just_up:
                        for other_icon in self.unit_icon:
                            if other_icon.right_selected:  # unselected all others first
                                other_icon.selection(how="right")
                        unit.selection(how="right")
                    break

    elif self.org_chart.mouse_over:
        mouse_pos = pygame.Vector2((self.cursor.pos[0] - self.org_chart.rect.topleft[0]),
                                   (self.cursor.pos[1] - self.org_chart.rect.topleft[1]))
        for rect in self.org_chart.node_rect:  # check for mouse on node in org chart
            if self.org_chart.node_rect[rect].collidepoint(mouse_pos):
                not_in_list = True
                for subunit_index, subunit in enumerate(self.preview_unit):  # check for unit in icon
                    if subunit_index == rect:  # found unit for data
                        popup_text = [self.leader_data.leader_list[
                                          self.play_map_data["unit"][subunit.team][subunit.index]["Leader ID"]][
                                          "Name"]]
                        for troop in self.play_map_data["unit"][subunit.team][subunit.index]["Troop"]:
                            popup_text += [self.troop_data.troop_list[troop]["Name"] + ": " +
                                           str(self.play_map_data["unit"][subunit.team][subunit.index]["Troop"][
                                                   troop][0]) + " + " +
                                           str(self.play_map_data["unit"][subunit.team][subunit.index]["Troop"][
                                                   troop][1])]
                        self.text_popup.popup(self.cursor.rect, popup_text)
                        self.add_main_ui_updater(self.text_popup)

                        if self.cursor.is_alt_select_just_up:
                            for subunit2 in self.unit_icon:
                                if subunit2.right_selected and subunit2 is not subunit:
                                    not_in_list = False
                                    self.play_map_data["unit"][subunit2.who.team][subunit2.who.index][
                                        "Temp Leader"] = subunit.index
                                    for subunit3_index, subunit3 in enumerate(self.unit_icon):
                                        if subunit3.selected:
                                            unit_change_team_unit(self, add_plus=False, old_selected=subunit3.who.index)
                                            self.org_chart.add_chart(self.play_map_data["unit"][subunit.team],
                                                                     self.preview_unit,
                                                                     selected=subunit3.who.index)
                                            break
                                    break
                        break

                if self.cursor.is_alt_select_just_up and not_in_list:  # remove unit's leader in org chart
                    self.play_map_data["unit"][subunit.team][rect]["Temp Leader"] = ""
                    for subunit3_index, subunit3 in enumerate(self.unit_icon):
                        if subunit3.selected:
                            unit_change_team_unit(self, add_plus=False, old_selected=subunit3.who.index)
                            self.org_chart.add_chart(self.play_map_data["unit"][subunit.team],
                                                     self.preview_unit,
                                                     selected=subunit3_index)
                            break
                    break

    elif self.team_coa_box.mouse_over:
        for this_team in self.team_coa:  # User select any team by clicking on coat of arm
            if this_team.mouse_over:
                shown_id = ("team", this_team.coa_images)
                if self.text_popup.last_shown_id != shown_id:
                    text = [self.faction_data.faction_name_list[faction] for faction in this_team.coa_images]
                    unit_data = [0, 0, 0]
                    for unit in self.play_source_data["unit"]:
                        if unit["Team"] == this_team.team:
                            unit_data[0] += 1
                            for troop_id, troop in unit["Troop"].items():
                                unit_data[1] += int(troop[0])
                                unit_data[2] += int(troop[1])
                    text.append("Leader: " + str(unit_data[0]) + " Active Troop: " + str(unit_data[1]) + " Reserve Troop: "+ str(unit_data[2]))
                    self.text_popup.popup(self.cursor.rect, text, shown_id=shown_id)
                else:
                    self.text_popup.popup(self.cursor.rect, None, shown_id=shown_id)
                self.add_ui_updater(self.text_popup)
            if this_team.event_press:
                self.team_selected = this_team.team
                this_team.change_select(True)

                for this_team2 in self.team_coa:
                    if self.team_selected != this_team2.team and this_team2.selected:
                        this_team2.change_select(False)

                leader_change_team_unit(self)
                self.org_chart.add_chart([], self.preview_unit)
                break

    elif self.map_back_button.event_press or esc_press:
        self.menu_state = "custom_unit_setup"
        self.current_map_row = 0
        self.remove_ui_updater(self.org_chart, self.start_button)

        leader_change_team_unit(self)
        self.org_chart.add_chart([], self.preview_unit)  # reset chart

        self.add_ui_updater(self.troop_list_box, self.select_button)
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

                setup_list(self.screen_scale, uimenu.NameList, self.current_map_row, unit_list,
                           self.map_namegroup, self.troop_list_box, self.main_ui_updater)
                break

        unit_change_team_unit(self)

    elif self.unit_model_room.mouse_over:
        if self.unit_selected is not None:
            self.text_popup.popup(self.cursor.rect,
                                  (self.leader_data.leader_lore[
                                              [item for item in self.play_map_data[self.map_source_selected]['unit'] if
                                               item["ID"] == self.unit_selected][0]["Leader ID"]]["Description"],),
                                  width_text_wrapper=500)
            self.add_ui_updater(self.text_popup)

    elif self.start_button.event_press:  # start battle
        self.team_pos = {team: [pos for pos in self.play_map_data["unit"]["pos"][team].values()] for
                         team in self.play_map_data["unit"]["pos"]}

        subunit_index = 1
        for index, subunit in enumerate(self.play_source_data["unit"]):
            subunit["ID"] = subunit_index
            subunit["Angle"] = 0
            subunit["Start Health"] = 100
            subunit["Start Stamina"] = 100
            subunit_index += 1

        for team in self.play_map_data["unit"]:
            if team != "pos":
                for subunit in self.play_map_data["unit"][team]:  # assign leader based on ID instead
                    temp_leader = subunit["Temp Leader"]
                    subunit["Leader"] = 0
                    if temp_leader != "":
                        subunit["Leader"] = self.play_map_data["unit"][team][temp_leader]["ID"]

        for icon in self.preview_unit:
            icon.kill()
        self.preview_unit.empty()

        self.play_map_data["battle"] = []
        for team, team_data in self.play_map_data["unit"].items():
            if team != "pos":
                for value in team_data:
                    new_value = {key: {key2: val2.copy() for key2, val2 in val.items()} if type(val) is dict else val
                                 for key, val in value.items()}
                    for troop in new_value["Troop"]:
                        troop_value = new_value["Troop"][troop]
                        new_value["Troop"][troop] = str(troop_value[0]) + "/" + str(troop_value[1])
                    self.play_map_data["battle"].append(new_value)

        self.start_battle(self.unit_selected)
