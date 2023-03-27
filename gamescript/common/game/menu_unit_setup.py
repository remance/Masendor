from gamescript import menu, battleui
from gamescript.common import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image


def menu_unit_setup(self, mouse_left_up, mouse_left_down, mouse_right_up, mouse_scroll_up, mouse_scroll_down, esc_press):
    if mouse_left_up or mouse_left_down or mouse_right_up:
        if mouse_left_up or mouse_right_up:
            for this_team in self.team_coa:  # User select any team by clicking on coat of arm
                if this_team.rect.collidepoint(self.mouse_pos):
                    self.team_selected = this_team.team
                    this_team.change_select(True)

                    for this_team2 in self.team_coa:
                        if self.team_selected != this_team2.team and this_team2.selected:
                            this_team2.change_select(False)

                    unit_list = create_unit_list(self, this_team)
                    self.current_map_row = 0
                    setup_list(self.screen_scale, menu.NameList, self.current_map_row, unit_list,
                               self.map_namegroup, self.unit_list_box, self.main_ui_updater)
                    change_team_unit(self)
                    break

            for box in self.tick_box:
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
                        int(self.mouse_pos[0] - self.map_preview.rect.x) * self.map_preview.map_scale_width,
                        int((self.mouse_pos[1] - self.map_preview.rect.y) * self.map_preview.map_scale_height))
                        if icon.who.name != "+":  # choose pos of selected unit
                            self.custom_map_data["unit"]["pos"][icon.who.team][index] = map_pos
                        self.map_preview.change_mode(1, team_pos_list=self.custom_map_data["unit"]["pos"],
                                                     camp_pos_list=self.camp_pos[0])
                        break

        if mouse_left_up and self.unit_list_box.rect.collidepoint(self.mouse_pos):  # click on unit list
            if self.unit_list_box.scroll.rect.collidepoint(self.mouse_pos):
                self.current_map_row = self.unit_list_box.scroll.player_input(
                    self.mouse_pos)  # update the scroll and get new current subsection
                for coa in self.team_coa:
                    if coa.selected:  # get unit for selected team
                        unit_list = create_unit_list(self, coa)
                        setup_list(self.screen_scale, menu.NameList, self.current_map_row, unit_list,
                                   self.map_namegroup, self.unit_list_box, self.main_ui_updater)
            else:
                for index, name in enumerate(self.map_namegroup):  # player select unit in name list
                    if name.rect.collidepoint(self.mouse_pos):
                        for char in self.char_icon:
                            if char.selected:
                                if char.who.name == "+":  # add new unit
                                    for coa in self.team_coa:
                                        if coa.selected:  # get unit for selected team
                                            if coa.team not in self.custom_map_data["unit"]:
                                                self.custom_map_data["unit"][coa.team] = []
                                                self.custom_map_data["unit"]["pos"][coa.team] = {}
                                            unit_data = create_unit_list(self, coa, unit_selected=name.name)
                                            self.custom_map_data["unit"][coa.team].append(unit_data)
                                            change_team_unit(self)
                                            self.map_preview.change_mode(1, camp_pos_list=self.camp_pos[0])
                                else:  # change existed
                                    pass

                        break

    if self.unit_list_box.rect.collidepoint(self.mouse_pos):
        for coa in self.team_coa:
            if coa.selected:  # get unit for selected team
                unit_list = create_unit_list(self, coa)
                self.current_map_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                                   self.unit_list_box.scroll, self.unit_list_box,
                                                   self.current_map_row, unit_list, self.source_namegroup,
                                                   self.main_ui_updater)
                break

    elif self.char_selector.rect.collidepoint(self.mouse_pos):
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
            if mouse_left_up or mouse_right_up:
                for index, icon in enumerate(self.char_icon):  # select unit
                    if icon.rect.collidepoint(self.mouse_pos):
                        if mouse_left_up:
                            for other_icon in self.char_icon:
                                if other_icon.selected:  # unselected all others first
                                    other_icon.selection()
                            icon.selection()
                            if icon.who.team in self.custom_map_data["unit"]["pos"] and \
                                    index in self.custom_map_data["unit"]["pos"][icon.who.team]:
                                # highlight unit in preview map
                                self.map_preview.change_mode(1, team_pos_list=self.custom_map_data["unit"]["pos"],
                                                             camp_pos_list=self.camp_pos[0],
                                                             selected=
                                                             self.custom_map_data["unit"]["pos"][icon.who.team][index])
                        else:
                            if icon.who.name != "+":
                                self.custom_map_data["unit"][icon.who.team].pop(index)
                                self.custom_map_data["unit"]["pos"][icon.who.team].pop(index)
                                icon.kill()

                        self.map_preview.change_mode(1, team_pos_list=self.custom_map_data["unit"]["pos"],
                                                     camp_pos_list=self.camp_pos[0])
                        break

    if self.map_back_button.event or esc_press:
        self.menu_state = "custom_team_select"
        self.map_back_button.event = False
        self.current_map_row = 0
        self.main_ui_updater.remove(*self.menu_button, self.unit_list_box, self.unit_list_box.scroll,
                                    self.char_icon)
        self.menu_button.remove(*self.menu_button)

        # Reset selected team
        for team in self.team_coa:
            team.change_select(False)
        self.team_selected = 1

        self.custom_map_data["unit"] = {"pos": {}}

        self.map_preview.change_mode(1, camp_pos_list=self.camp_pos[0])  # revert map preview back to without unit dot

        for stuff in self.map_namegroup:  # remove map name item
            stuff.kill()
            del stuff

        setup_list(self.screen_scale, menu.NameList, self.current_source_row,
                   ["None"] + self.faction_data.faction_name_list,
                   self.source_namegroup, self.source_list_box, self.main_ui_updater)

        self.menu_button.add(*self.map_select_button)

        self.char_selector.setup_char_icon(self.char_icon, self.camp_icon)

        self.main_ui_updater.add(*self.menu_button, self.map_option_box, self.observe_mode_tick_box,
                                 self.source_list_box, self.source_list_box.scroll,
                                 self.char_selector, self.char_selector.scroll, self.team_coa)

    elif self.select_button.event:  # go to character select screen
        self.select_button.event = False
        # if len([coa for coa in self.team_coa if coa.name is not None and coa.name != "None"]) > 1:
        #     self.menu_state = "char_select"
        #     self.char_select_row = 0
        #     self.current_map_row = 0
        #
        #     self.main_ui_updater.remove(self.map_option_box, self.observe_mode_tick_box,
        #                                 self.source_list_box, self.source_list_box.scroll)
        #
        #     for stuff in self.source_namegroup:  # remove map name item
        #         stuff.kill()
        #         del stuff
        #
        #     # self.char_selector.setup_char_icon(self.char_icon, self.preview_char)
        # else:
        #     self.input_popup = ("confirm_input", "warning")
        #     self.input_ui.change_instruction("Each team require at least 1 unit")
        #     self.main_ui_updater.add(self.input_ui_popup)


def change_team_unit(self):
    for this_team in self.team_coa:
        if this_team.selected:
            for icon in self.preview_char:
                icon.kill()
            self.preview_char.empty()

            if this_team.team in self.custom_map_data["unit"]:
                for unit in self.custom_map_data["unit"][this_team.team]:
                    if unit["Leader ID"] in self.leader_data.images:
                        image = self.leader_data.images[unit["Leader ID"]]
                    else:
                        image = unit["Leader ID"]
                    self.preview_char.add(battleui.TempCharIcon(self.screen_scale, this_team.team, image))

            self.preview_char.add(battleui.TempCharIcon(self.screen_scale, this_team.team, "+"))

            unit_list = create_unit_list(self, this_team)

            self.current_map_row = 0

            setup_list(self.screen_scale, menu.NameList, self.current_map_row, unit_list,
                       self.map_namegroup, self.unit_list_box, self.main_ui_updater)

            self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

            break


def create_unit_list(self, coa, unit_selected=None):
    unit_list = []
    unit_data = None
    for faction in coa.coa_images:
        if faction == 0:  # all faction
            for this_faction in self.faction_data.faction_unit_list:
                unit_list += list(self.faction_data.faction_unit_list[this_faction].keys())
                if unit_selected and unit_selected in self.faction_data.faction_unit_list[this_faction]:
                    unit_data = self.faction_data.faction_unit_list[this_faction][unit_selected]
        else:
            unit_list += list(self.faction_data.faction_unit_list[faction].keys())
            if unit_selected and unit_selected in self.faction_data.faction_unit_list[faction]:
                unit_data = self.faction_data.faction_unit_list[faction][unit_selected]

        unit_list = sorted((set(unit_list)), key=unit_list.index)
    if not unit_selected:
        return unit_list
    else:
        return unit_data
