from gamescript import menu
from gamescript.common import utility
from gamescript.common.game import menu_preset_team_select

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image

change_team_coa = menu_preset_team_select.change_team_coa


def menu_custom_team_select(self, mouse_left_up, mouse_left_down, mouse_right_up, mouse_scroll_up, mouse_scroll_down,
                            esc_press):
    if mouse_left_up or mouse_left_down:
        if mouse_left_up:
            change_team_coa(self)
            for index, name in enumerate(self.source_namegroup):  # user select source
                if name.rect.collidepoint(self.mouse_pos):  # click on source name
                    team_army, team_leader = self.read_battle_source(
                        [self.source_scale_text[self.map_source], self.source_text[self.map_source]])
                    self.change_battle_source(team_army, team_leader)
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
            setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.faction_data.faction_name_list,
                       self.source_namegroup, self.source_list_box, self.main_ui_updater)
    elif mouse_right_up:
        pass

    if self.source_list_box.rect.collidepoint(self.mouse_pos):
        self.current_source_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                              self.source_list_box.scroll, self.source_list_box,
                                              self.current_source_row, self.faction_data.faction_name_list,
                                              self.source_namegroup, self.main_ui_updater)

    if self.map_back_button.event or esc_press:
        self.menu_state = self.last_select
        self.map_back_button.event = False
        self.main_ui_updater.remove(*self.menu_button, self.map_list_box, self.map_option_box,
                                    self.observe_mode_tick_box, self.source_list_box, self.source_list_box.scroll,
                                    self.source_description,  self.char_selector, self.char_selector.scroll)
        self.menu_button.remove(*self.menu_button)

        # Reset selected team
        for team in self.team_coa:
            team.change_select(False)
        self.team_selected = 1

        self.map_source = 0
        self.map_show.change_mode(0)  # revert map preview back to without unit dot

        for stuff in self.source_namegroup:  # remove map name item
            stuff.kill()
            del stuff

        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup,
                   self.map_list_box, self.main_ui_updater)

        self.menu_button.add(*self.map_select_button)
        self.main_ui_updater.add(*self.map_select_button, self.map_list_box, self.map_list_box.scroll,
                                 self.map_description)

    elif self.select_button.event:  # go to character select screen
        self.menu_state = "char_select"
        self.select_button.event = False
        self.char_select_row = 0

        self.main_ui_updater.remove(*self.team_select_button, self.char_selector, self.char_selector.scroll,
                                    self.map_option_box, self.observe_mode_tick_box,
                                    self.source_list_box, self.source_list_box.scroll)
        self.menu_button.remove(*self.map_select_button)

        for group in (self.map_namegroup, self.team_coa):  # remove no longer related sprites in group
            for stuff in group:
                stuff.kill()
                del stuff

        team_selected = self.team_selected

        self.setup_battle_troop(self.preview_char, specific_team=team_selected)

        self.char_selector.setup_char_icon(self.char_icon, self.preview_char)

        for index, icon in enumerate(self.char_icon):  # select first char
            self.char_selected = icon.who.map_id
            icon.selection()
            self.char_stat["char"].add_leader_stat(icon.who, self.leader_data, self.troop_data)
            who_todo = {key: value for key, value in self.leader_data.leader_list.items() if key == icon.who.troop_id}
            preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True, max_preview_size=400)
            self.char_stat["model"].add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"], icon.who.coa)
            self.map_show.change_mode(1, team_pos_list=self.team_pos, camp_pos_list=self.camp_pos[self.map_source],
                                      selected=icon.who.base_pos)
            break

        self.main_ui_updater.add(self.char_selector, self.char_selector.scroll,
                                 tuple(self.char_stat.values()), *self.char_select_button)
        self.menu_button.add(*self.char_select_button)