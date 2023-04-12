from gamescript import menu, battleui
from gamescript.common import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image


def menu_custom_team_select(self, mouse_left_up, mouse_left_down, mouse_right_up, mouse_scroll_up, mouse_scroll_down,
                            esc_press):
    if self.popup_list_box in self.main_ui_updater:
        if self.popup_list_box.scroll.rect.collidepoint(self.mouse_pos):
            new_row = self.popup_list_box.scroll.player_input(self.mouse_pos)
            if new_row is not None:
                self.current_popup_row = new_row
                setup_list(self.screen_scale, menu.NameList, self.current_popup_row,
                           self.popup_list_box.namelist,
                           self.popup_namegroup, self.popup_list_box, self.main_ui_updater)
        elif mouse_left_up:
            if self.popup_list_box.rect.collidepoint(self.mouse_pos):
                for index, name in enumerate(self.popup_namegroup):  # click on popup list
                    if name.rect.collidepoint(self.mouse_pos):
                        self.weather_custom_select.rename("Weather: " + name.name)
                        battle_time = "09:00:00"
                        if self.night_battle_tick_box.tick:  # check for night battle
                            battle_time = "21:00:00"
                        self.custom_map_data["info"]["weather"] = \
                            [[int(self.battle_map_data.weather_list.index(name.name) / 3), battle_time,
                              self.custom_map_data["info"]["weather"][0][2],
                             ("Light", "Normal", "Strong").index(name.name.split(" ")[0])]]
                        for this_name in self.popup_namegroup:  # remove name list
                            this_name.kill()
                            del this_name
                        self.main_ui_updater.remove(self.popup_list_box, self.popup_list_box.scroll)
                        break
            else:  # click other stuffs
                for this_name in self.popup_namegroup:  # remove name list
                    this_name.kill()
                    del this_name
                self.main_ui_updater.remove(self.popup_list_box, self.popup_list_box.scroll)

    if mouse_left_up or mouse_left_down or mouse_right_up:
        if mouse_left_up or mouse_right_up:
            change_team_coa(self)
            for index, name in enumerate(self.source_namegroup):  # player select faction name list
                if name.rect.collidepoint(self.mouse_pos):
                    for coa in self.team_coa:
                        if coa.selected:
                            if name.name != "None":
                                faction_index = self.faction_data.faction_name_list.index(name.name)
                                if mouse_left_up:
                                    if "Team " + str(coa.team) in self.custom_map_data["info"]:
                                        if faction_index not in self.custom_map_data["info"]["Team " + str(coa.team)]:
                                            self.custom_map_data["info"]["Team " + str(coa.team)].append(faction_index)
                                    else:
                                        self.custom_map_data["info"]["Team " + str(coa.team)] = [faction_index]
                                    coa.change_coa(
                                        {int(faction): self.faction_data.coa_list[int(faction)] for faction in
                                         self.custom_map_data["info"]["Team " + str(coa.team)]},
                                        self.faction_data.faction_list[self.custom_map_data["info"][
                                            "Team " + str(coa.team)][0]]["Name"])
                                elif mouse_right_up:
                                    if faction_index in self.custom_map_data["info"]["Team " + str(coa.team)]:
                                        self.custom_map_data["info"]["Team " + str(coa.team)].remove(faction_index)
                                    if self.custom_map_data["info"]["Team " + str(coa.team)]:  # still not empty
                                        coa.change_coa(
                                            {int(faction): self.faction_data.coa_list[int(faction)] for faction in
                                             self.custom_map_data["info"]["Team " + str(coa.team)]},
                                            self.faction_data.faction_list[self.custom_map_data["info"][
                                                "Team " + str(coa.team)][0]]["Name"])
                                    else:  # list empty remove data
                                        self.custom_map_data["info"].pop("Team " + str(coa.team))
                                        coa.change_coa({0: None}, "None")
                            else:
                                if mouse_left_up and "Team " + str(coa.team) in self.custom_map_data["info"]:
                                    self.custom_map_data["info"].pop("Team " + str(coa.team))
                                coa.change_coa({0: None}, "None")

                            if "Team " + str(coa.team) in self.custom_map_data["info"]:  # camp, team exist
                                if coa.team not in self.camp_pos[0]:  # new team, camp not exist
                                    self.camp_pos[0][coa.team] = []
                                    for icon in self.camp_icon:
                                        icon.kill()
                                    self.camp_icon = []
                                else:
                                    for camp in self.camp_pos[0][coa.team]:
                                        self.camp_icon.append(battleui.TempCharIcon(self.screen_scale, coa.team,
                                                                                    camp[1], 0))
                                if not self.camp_icon or self.camp_icon[-1].name != "+":
                                    self.camp_icon.append(battleui.TempCharIcon(self.screen_scale, coa.team, "+", 0))

                            else:  # team no longer exist
                                if coa.team in self.camp_pos[0]:
                                    self.camp_pos[0].pop(coa.team)
                                    for icon in self.camp_icon:
                                        icon.kill()
                                    self.camp_icon = []
                            self.char_selector.setup_char_icon(self.char_icon, self.camp_icon)
                            break

            for box in (self.observe_mode_tick_box, self.night_battle_tick_box):
                if box in self.main_ui_updater and box.rect.collidepoint(self.mouse_pos):
                    if box.tick is False:
                        box.change_tick(True)
                    else:
                        box.change_tick(False)
                    if box.option == "observe":
                        self.enactment = box.tick

            if mouse_right_up and self.map_preview.rect.collidepoint(self.mouse_pos):
                for index, icon in enumerate(self.char_icon):
                    if icon.selected:
                        map_pos = (
                            (int(self.mouse_pos[0] - self.map_preview.rect.x) * self.map_preview.map_scale_width),
                            int((self.mouse_pos[1] - self.map_preview.rect.y) * self.map_preview.map_scale_height))
                        if icon.who.name == "+":
                            self.input_popup = ("text_input", "custom_camp_size/" + str(map_pos) + "/" +
                                                str(icon.who.team))
                            self.input_ui.change_instruction("Camp Size Value:")
                            self.main_ui_updater.add(self.input_ui_popup)
                        else:
                            self.camp_pos[0][icon.who.team][index][0] = map_pos
                        self.map_preview.change_mode(1, camp_pos_list=self.camp_pos[0])
                        break

        if mouse_left_up and self.source_list_box.scroll.rect.collidepoint(self.mouse_pos):  # click on list scroll
            self.current_source_row = self.source_list_box.scroll.player_input(
                self.mouse_pos)  # update the scroll and get new current subsection
            setup_list(self.screen_scale, menu.NameList, self.current_source_row,
                       ["None"] + self.faction_data.faction_name_list,
                       self.source_namegroup, self.source_list_box, self.main_ui_updater)

    if self.source_list_box.rect.collidepoint(self.mouse_pos):
        self.current_source_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                              self.source_list_box.scroll, self.source_list_box,
                                              self.current_source_row, ["None"] + self.faction_data.faction_name_list,
                                              self.source_namegroup, self.main_ui_updater)

    elif self.weather_custom_select.rect.collidepoint(self.mouse_pos):
        if mouse_left_up:
            self.current_popup_row = 0
            self.popup_list_open(self.weather_custom_select.rect.bottomleft,
                                 self.battle_map_data.weather_list, "weather",
                                 "top", self.main_ui_updater)

    elif self.wind_custom_select.rect.collidepoint(self.mouse_pos):
        if mouse_left_up:
            self.input_popup = ("text_input", "wind")
            self.input_ui.change_instruction("Wind Direction Degree:")
            self.main_ui_updater.add(self.input_ui_popup)

    elif self.char_selector.rect.collidepoint(self.mouse_pos):
        if mouse_scroll_up:
            if self.char_selector.current_row > 0:
                self.char_selector.current_row -= 1
                self.char_selector.scroll.change_image(new_row=self.char_selector.current_row,
                                                       row_size=self.char_selector.row_size)
                self.char_selector.setup_char_icon(self.char_icon, self.camp_icon)

        elif mouse_scroll_down:
            if self.char_selector.current_row < self.char_selector.row_size:
                self.char_selector.current_row += 1
                self.char_selector.scroll.change_image(new_row=self.char_selector.current_row,
                                                       row_size=self.char_selector.row_size)
                self.char_selector.setup_char_icon(self.char_icon, self.camp_icon)

        elif self.char_selector.scroll.rect.collidepoint(self.mouse_pos):
            if mouse_left_down or mouse_left_up:
                new_row = self.char_selector.scroll.player_input(self.mouse_pos)
                if self.char_selector.current_row != new_row:
                    self.char_selector.current_row = new_row
                    self.char_selector.scroll.change_image(new_row=new_row, row_size=self.char_selector.row_size)
                    self.char_selector.setup_char_icon(self.char_icon, self.camp_icon)

        else:
            if mouse_left_up or mouse_right_up:
                for index, icon in enumerate(self.char_icon):
                    if icon.rect.collidepoint(self.mouse_pos):
                        if mouse_left_up:
                            for other_icon in self.char_icon:
                                if other_icon.selected:  # unselected all others first
                                    other_icon.selection()
                            icon.selection()
                        else:  # right click remove icon
                            if icon.who.name != "+":
                                self.camp_pos[0][icon.who.team].pop(index)
                                icon.kill()
                                self.camp_icon.pop(index)
                                self.char_selector.setup_char_icon(self.char_icon, self.camp_icon)
                        self.map_preview.change_mode(1, camp_pos_list=self.camp_pos[0])
                        break

    if self.map_back_button.event or esc_press:
        self.custom_map_data["info"] = {"weather": self.custom_map_data["info"]["weather"]}  # keep weather setting only
        self.custom_map_data["unit"] = {"pos": {}}
        self.camp_pos = [{}]
        self.menu_state = self.last_select
        self.map_back_button.event = False
        self.main_ui_updater.remove(*self.menu_button, self.map_list_box, self.custom_map_option_box,
                                    self.observe_mode_tick_box, self.night_battle_tick_box,
                                    self.source_list_box, self.source_list_box.scroll,
                                    self.char_selector, self.char_selector.scroll,
                                    self.char_icon, self.team_coa, self.weather_custom_select, self.wind_custom_select)
        self.menu_button.remove(*self.menu_button)

        for this_name in self.popup_namegroup:  # remove name list
            this_name.kill()
            del this_name
        self.main_ui_updater.remove(self.popup_list_box, self.popup_list_box.scroll)

        # Reset selected team
        for team in self.team_coa:
            team.change_select(False)
        self.team_selected = 1

        self.map_preview.change_mode(0)  # revert map preview back to without unit dot

        for stuff in self.source_namegroup:  # remove map name item
            stuff.kill()
            del stuff
        for icon in self.camp_icon:
            icon.kill()

        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup,
                   self.map_list_box, self.main_ui_updater)

        self.menu_button.add(*self.map_select_button)
        self.main_ui_updater.add(*self.map_select_button, self.map_list_box, self.map_list_box.scroll,
                                 self.map_description)

    elif self.select_button.event:  # go to unit setup screen
        self.select_button.event = False
        if len([coa for coa in self.team_coa if coa.name is not None and coa.name != "None"]) > 1:
            self.menu_state = "unit_setup"
            self.char_select_row = 0

            self.main_ui_updater.remove(self.custom_map_option_box, self.observe_mode_tick_box, self.night_battle_tick_box,
                                        self.source_list_box, self.source_list_box.scroll, self.weather_custom_select,
                                        self.wind_custom_select)

            for this_name in self.popup_namegroup:  # remove name list
                this_name.kill()
                del this_name
            self.main_ui_updater.remove(self.popup_list_box, self.popup_list_box.scroll)

            for stuff in self.source_namegroup:  # remove map name item
                stuff.kill()
                del stuff

            for coa in self.team_coa:
                if coa.coa_images and coa.team not in self.custom_map_data["unit"]:
                    self.custom_map_data["unit"][coa.team] = []
                    self.custom_map_data["unit"]["pos"][coa.team] = {}
                elif coa.team in self.custom_map_data["unit"]:  # non existence team
                    self.custom_map_data["unit"].pop(coa.team)
                    self.custom_map_data["unit"]["pos"].pop(coa.team)

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

            # self.char_selector.setup_char_icon(self.char_icon, self.preview_char)
        else:
            self.input_popup = ("confirm_input", "warning")
            self.input_ui.change_instruction("Require at least 2 teams")
            self.main_ui_updater.add(self.input_ui_popup)


def change_team_coa(self):
    for this_team in self.team_coa:  # User select any team by clicking on coat of arm
        if this_team.rect.collidepoint(self.mouse_pos):
            self.team_selected = this_team.team
            this_team.change_select(True)

            for icon in self.camp_icon:
                icon.kill()
            self.camp_icon = []
            if this_team.team in self.camp_pos[0]:
                for camp in self.camp_pos[0][this_team.team]:
                    self.camp_icon.append(battleui.TempCharIcon(self.screen_scale, this_team.team, camp[1], 0))
                self.camp_icon.append(battleui.TempCharIcon(self.screen_scale, this_team.team, "+", 0))
            self.char_selector.setup_char_icon(self.char_icon, self.camp_icon)

            for this_team2 in self.team_coa:
                if self.team_selected != this_team2.team and this_team2.selected:
                    this_team2.change_select(False)
            break
