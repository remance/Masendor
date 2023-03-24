from gamescript import menu, battleui
from gamescript.common import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image


def menu_custom_team_select(self, mouse_left_up, mouse_left_down, mouse_right_up, mouse_scroll_up, mouse_scroll_down,
                            esc_press):
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
                                    coa.change_coa([self.faction_data.coa_list[int(faction)] for faction in
                                                    self.custom_map_data["info"]["Team " + str(coa.team)]],
                                                   self.faction_data.faction_list[self.custom_map_data["info"][
                                                       "Team " + str(coa.team)][0]]["Name"])
                                elif mouse_right_up:
                                    if faction_index in self.custom_map_data["info"]["Team " + str(coa.team)]:
                                        self.custom_map_data["info"]["Team " + str(coa.team)].remove(faction_index)
                                    if self.custom_map_data["info"]["Team " + str(coa.team)]:  # still not empty
                                        coa.change_coa([self.faction_data.coa_list[int(faction)] for faction in
                                                        self.custom_map_data["info"]["Team " + str(coa.team)]],
                                                       self.faction_data.faction_list[self.custom_map_data["info"][
                                                           "Team " + str(coa.team)][0]]["Name"])
                                    else:  # list empty remove data
                                        self.custom_map_data["info"].pop("Team " + str(coa.team))
                                        coa.change_coa([None], "None")
                            else:
                                if mouse_left_up and "Team " + str(coa.team) in self.custom_map_data["info"]:
                                    self.custom_map_data["info"].pop("Team " + str(coa.team))
                                coa.change_coa([None], "None")

                            if "Team " + str(coa.team) in self.custom_map_data["info"]:  # camp, team exist
                                if coa.team not in self.camp_pos[0]:  # new team, camp not exist
                                    self.camp_pos[0][coa.team] = []
                                    for icon in self.camp_icon:
                                        icon.kill()
                                    self.camp_icon = []
                                else:
                                    for camp in self.camp_pos[0][coa.team]:
                                        self.camp_icon.append(battleui.CampIcon(self.screen_scale, coa.team, camp[1]))
                                if not self.camp_icon or self.camp_icon[-1].camp_size != "+":
                                    self.camp_icon.append(battleui.CampIcon(self.screen_scale, coa.team, "+"))

                            else:  # team no longer exist
                                if coa.team in self.camp_pos[0]:
                                    self.camp_pos[0].pop(coa.team)
                                    for icon in self.camp_icon:
                                        icon.kill()
                                    self.camp_icon = []
                            self.char_selector.setup_char_icon(self.char_icon, self.camp_icon)
                            break
                    # team_army, team_leader = self.read_battle_source(
                    #     [self.source_scale_text[self.map_source], self.source_text[self.map_source]])
                    # self.change_battle_source(team_army, team_leader)

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
                        (int(self.mouse_pos[0] - self.map_preview.rect.x) * self.map_preview.map_scale_width),
                        int((self.mouse_pos[1] - self.map_preview.rect.y) * self.map_preview.map_scale_height))
                        if icon.who.camp_size == "+":
                            self.input_popup = ("text_input", "custom_camp_size/" + str(map_pos) + "/" +
                                                    str(icon.who.team))
                            self.input_ui.change_instruction("Camp Size Value:")
                            self.main_ui_updater.add(self.input_ui_popup)
                        else:
                            print(self.camp_pos[0][icon.who.team], index)
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
                        else:
                            if icon.who.camp_size != "+":
                                icon.kill()

                        self.map_preview.change_mode(1, camp_pos_list=self.camp_pos[0])
                        break

    if self.map_back_button.event or esc_press:
        self.custom_map_data = {"info": {}, "unit": {}}
        self.camp_pos = [{}]
        self.menu_state = self.last_select
        self.map_back_button.event = False
        self.main_ui_updater.remove(*self.menu_button, self.map_list_box, self.map_option_box,
                                    self.observe_mode_tick_box, self.source_list_box, self.source_list_box.scroll,
                                    self.source_description,  self.char_selector, self.char_selector.scroll,
                                    self.char_icon, self.team_coa)
        self.menu_button.remove(*self.menu_button)

        # Reset selected team
        for team in self.team_coa:
            team.change_select(False)
        self.team_selected = 1

        self.map_source = 0
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

    elif self.select_button.event:  # go to character select screen
        # self.menu_state = "unit_setup"
        self.select_button.event = False
        # self.char_select_row = 0
        #
        # self.main_ui_updater.remove(*self.team_select_button, self.map_option_box, self.observe_mode_tick_box,
        #                             self.source_list_box, self.source_list_box.scroll)
        # self.menu_button.remove(*self.map_select_button)
        #
        # for stuff in self.source_namegroup:  # remove map name item
        #     stuff.kill()
        #     del stuff
        #
        # self.char_selector.setup_char_icon(self.char_icon, self.preview_char)
        #
        # self.menu_button.add(*self.char_select_button)


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
                    self.camp_icon.append(battleui.CampIcon(self.screen_scale, this_team.team, camp[1]))
                self.camp_icon.append(battleui.CampIcon(self.screen_scale, this_team.team, "+"))
            self.char_selector.setup_char_icon(self.char_icon, self.camp_icon)

            for this_team2 in self.team_coa:
                if self.team_selected != this_team2.team and this_team2.selected:
                    this_team2.change_select(False)
            break
