from gamescript import menu
from gamescript.common import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image


def menu_team_select(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if mouse_left_up or mouse_left_down:
        if mouse_left_up:
            change_team_coa(self)
            for index, name in enumerate(self.source_namegroup):  # user select source
                if name.rect.collidepoint(self.mouse_pos):  # click on source name
                    self.map_source = index
                    team_army, team_leader = self.read_battle_source(
                        [self.source_scale_text[self.map_source], self.source_text[self.map_source]])
                    self.change_battle_source(self.source_scale[self.map_source], team_army, team_leader)
                    break

            for box in self.tick_box:
                if box in self.main_ui_updater and box.rect.collidepoint(self.mouse_pos):
                    if box.tick is False:
                        box.change_tick(True)
                    else:
                        box.change_tick(False)
                    if box.option == "observe":
                        self.enactment = box.tick

        if self.source_list_box.scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
            self.current_source_row = self.source_list_box.scroll.player_input(
                self.mouse_pos)  # update the scroll and get new current subsection
            setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.source_name_list,
                       self.source_namegroup, self.source_list_box, self.main_ui_updater)
    if self.source_list_box.rect.collidepoint(self.mouse_pos):
        self.current_source_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                              self.source_list_box.scroll, self.source_list_box,
                                              self.current_source_row, self.source_list,
                                              self.source_namegroup, self.main_ui_updater)

    if self.map_back_button.event or esc_press:
        self.menu_state = self.last_select
        self.map_back_button.event = False
        self.main_ui_updater.remove(*self.menu_button, self.map_list_box, self.map_option_box,
                                    self.observe_mode_tick_box, self.source_list_box, self.source_list_box.scroll,
                                    self.source_description)
        self.menu_button.remove(*self.menu_button)

        # Reset selected team
        for team in self.team_coa:
            team.change_select(False)
        self.team_selected = 1

        self.map_source = 0
        self.map_show.change_mode(0)  # revert map preview back to without unit dot

        for group in (self.source_namegroup, self.army_stat):
            for stuff in group:  # remove map name item
                stuff.kill()
                del stuff

        if self.menu_state == "preset_map":  # regenerate map name list
            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.preset_map_list, self.map_namegroup,
                       self.map_list_box,
                       self.main_ui_updater)
        else:
            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup,
                       self.map_list_box,
                       self.main_ui_updater)

        self.menu_button.add(*self.map_select_button)
        self.main_ui_updater.add(*self.map_select_button, self.map_list_box, self.map_list_box.scroll,
                                 self.map_description)

    elif self.select_button.event:  # go to character select screen
        self.menu_state = "char_select"
        self.select_button.event = False
        self.char_select_row = 0

        self.main_ui_updater.remove(*self.map_select_button, self.map_option_box, self.source_list_box,
                                    self.observe_mode_tick_box, self.source_list_box.scroll,
                                    self.source_description, self.army_stat)
        self.menu_button.remove(*self.map_select_button)

        for group in (self.map_namegroup, self.team_coa):  # remove no longer related sprites in group
            for stuff in group:
                stuff.kill()
                del stuff

        self.char_stat["char"] = menu.ArmyStat(self.screen_scale,
                                               (self.screen_rect.center[0] / 2.5, self.screen_rect.height / 2.5),
                                               load_image(self.main_dir, self.screen_scale,
                                                          "char_stat.png", ("ui", "mapselect_ui")))  # char stat
        self.char_stat["model"] = menu.ArmyStat(self.screen_scale,
                                                (self.screen_rect.center[0] * 1.6, self.screen_rect.height / 2.5),
                                                load_image(self.main_dir, self.screen_scale,
                                                           "char_stat.png", ("ui", "mapselect_ui")))  # troop stat

        team_selected = self.team_selected

        self.setup_battle_troop(self.preview_char, specific_team=team_selected)

        self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

        for index, icon in enumerate(self.char_icon):  # select first char
            self.char_selected = icon.who.pos_id
            icon.selection()
            self.char_stat["char"].add_leader_stat(icon.who, self.leader_data, self.troop_data)
            who_todo = {key: value for key, value in self.leader_data.leader_list.items() if key == icon.who.troop_id}
            preview_sprite_pool = self.create_troop_sprite_pool(who_todo, preview=True, max_preview_size=400)
            self.char_stat["model"].add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"], icon.who.coa)
            self.map_show.change_mode(1, team_pos_list=self.team_pos, selected=icon.who.base_pos)
            break

        self.main_ui_updater.add(self.char_selector, self.char_selector.scroll,
                                 tuple(self.char_stat.values()), *self.char_select_button)
        self.menu_button.add(*self.char_select_button)


def change_team_coa(self):
    for this_team in self.team_coa:  # User select any team by clicking on coat of arm
        if this_team.rect.collidepoint(self.mouse_pos):
            self.team_selected = this_team.team
            this_team.change_select(True)

            # Reset team selected on team user not currently selected
            for this_team2 in self.team_coa:
                if self.team_selected != this_team2.team and this_team2.selected:
                    this_team2.change_select(False)
            break
