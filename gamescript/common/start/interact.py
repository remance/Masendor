import gc
import pygame

from gamescript import menu, battleui
from gamescript.common import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll

def main_menu_process(self, mouse_left_up):

    if self.preset_map_button.event:  # preset map list menu
        self.menu_state = "preset_map"
        self.last_select = self.menu_state
        self.preset_map_button.event = False
        self.main_ui.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                            *self.popup_namegroup)
        self.menu_button.remove(*self.menu_button)

        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.preset_map_list, self.map_namegroup,
                   self.map_listbox,
                   self.main_ui)
        self.make_preview_map(self.preset_map_folder, self.preset_map_list)

        self.menu_button.add(*self.map_select_button)
        self.main_ui.add(*self.map_select_button, self.map_listbox, self.map_title, self.map_scroll)

    elif self.custom_map_button.event:  # custom map list menu
        self.menu_state = "custom"
        self.last_select = self.menu_state
        self.custom_map_button.event = False
        self.main_ui.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                            *self.popup_namegroup)
        self.menu_button.remove(*self.menu_button)

        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup,
                   self.map_listbox,
                   self.main_ui)
        self.make_preview_map(self.custom_map_folder, self.custom_map_list)

        self.menu_button.add(*self.map_select_button)
        self.main_ui.add(*self.map_select_button, self.map_listbox, self.map_title, self.map_scroll)

    elif self.game_edit_button.event:  # custom subunit/sub-subunit editor menu
        self.menu_state = "game_creator"
        self.game_edit_button.event = False
        self.main_ui.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                            *self.popup_namegroup)
        self.menu_button.remove(*self.menu_button)

        self.menu_button.add(*self.editor_button)
        self.main_ui.add(*self.editor_button)

    elif self.option_button.event:  # change start_set menu to option menu
        self.menu_state = "option"
        self.option_button.event = False
        self.main_ui.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                            *self.popup_namegroup)
        self.menu_button.remove(*self.menu_button)

        self.menu_button.add(*self.option_menu_button)
        self.main_ui.add(*self.menu_button, self.option_menu_slider, self.value_box)
        self.main_ui.add(*self.option_icon_list)

    elif self.lore_button.event:  # open encyclopedia
        self.before_lore_state = self.menu_state
        self.menu_state = "encyclopedia"
        self.main_ui.add(self.encyclopedia, self.lore_name_list, *self.lore_button_ui,
                         self.lore_scroll)  # add sprite related to encyclopedia
        self.encyclopedia.change_section(0, self.lore_name_list, self.subsection_name, self.lore_scroll, self.page_button,
                                         self.main_ui)
        self.lore_button.event = False

    elif mouse_left_up and self.profile_box.rect.collidepoint(self.mouse_pos):
        self.text_input_popup = ("text_input", "profile_name")
        self.input_box.text_start(self.profile_name)
        self.input_ui.change_instruction("Profile Name:")
        self.main_ui.add(self.input_ui_popup)

    elif mouse_left_up and self.genre_change_box.rect.collidepoint(self.mouse_pos):
        self.popup_list_open(self.genre_change_box.rect.bottomleft, self.genre_list, "genre")

    elif self.popup_listbox in self.main_ui:
        if self.popup_listbox.rect.collidepoint(self.mouse_pos):
            self.ui_click = True
            for index, name in enumerate(self.popup_namegroup):
                if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # click on name in list
                    self.change_genre(index)

                    for thisname in self.popup_namegroup:  # remove troop name list
                        thisname.kill()
                        del thisname

                    self.main_ui.remove(self.popup_listbox, self.popup_list_scroll)
                    break

        elif self.popup_list_scroll.rect.collidepoint(self.mouse_pos):  # scrolling on list
            self.ui_click = True
            self.current_popup_row = self.popup_list_scroll.user_input(
                self.mouse_pos)  # update the scroller and get new current subsection
            setup_list(self.screen_scale, menu.NameList, self.current_popup_row, self.genre_list,
                       self.popup_namegroup, self.popup_listbox, self.main_ui)

        # else:
        #     self.main_ui.remove(self.popup_listbox, self.popup_list_scroll, *self.popup_namegroup)


def map_select_process(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if mouse_left_up or mouse_left_down:
        if mouse_left_up:
            for index, name in enumerate(self.map_namegroup):  # user click on map name, change map
                if name.rect.collidepoint(self.mouse_pos):
                    self.current_map_select = index
                    if self.menu_state == "preset_map":  # make new map image
                        self.make_preview_map(self.preset_map_folder, self.preset_map_list)
                    else:
                        self.make_preview_map(self.custom_map_folder, self.custom_map_list)
                    break

        if self.map_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
            self.current_map_row = self.map_scroll.user_input(
                self.mouse_pos)  # update the scroll and get new current subsection
            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.preset_map_list,
                       self.map_namegroup, self.map_listbox,
                       self.main_ui)

    if self.map_listbox.rect.collidepoint(self.mouse_pos):
        self.current_map_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.map_scroll,
                                           self.map_listbox,
                                           self.current_map_row, self.preset_map_list, self.map_namegroup, self.main_ui)

    if self.map_back_button.event or esc_press:
        self.map_back_button.event = False
        self.current_map_row = 0
        self.current_map_select = 0

        self.main_ui.remove(self.map_listbox, self.map_show, self.map_scroll, self.map_description,
                            self.team_coa, self.map_title)

        for group in (self.map_namegroup, self.team_coa):  # remove no longer related sprites in group
            for stuff in group:
                stuff.kill()
                del stuff

        self.back_mainmenu()

    elif self.select_button.event:  # select this map, go to prepare setup
        self.current_source_row = 0
        self.menu_state = "team_select"
        self.select_button.event = False

        self.main_ui.remove(*self.map_select_button, self.map_listbox, self.map_scroll, self.map_description)
        self.menu_button.remove(*self.map_select_button)

        for stuff in self.map_namegroup:  # remove map name item
            stuff.kill()
            del stuff

        for team in self.team_coa:
            if self.team_selected == team.team:
                team.change_select(True)

        openfolder = self.preset_map_folder
        if self.last_select == "custom":
            openfolder = self.custom_map_folder
        try:
            self.source_list = self.read_selected_map_data(openfolder, "source.csv")
            self.source_name_list = [value[0] for value in list(self.source_list.values())[1:]]
            self.source_scale_text = [value[1] for value in list(self.source_list.values())[1:]]
            self.source_scale = [(float(value[2]), float(value[3]), float(value[4]), float(value[5]))
                                 for value in
                                 list(self.source_list.values())[1:]]
            self.source_text = [value[-1] for value in list(self.source_list.values())[1:]]
        except Exception:  # no source.csv make empty list
            self.source_name_list = [""]
            self.source_scale_text = [""]
            self.source_scale = [""]
            self.source_text = [""]

        setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.source_name_list,
                   self.source_namegroup, self.source_list_box, self.main_ui)

        self.source_scroll = battleui.UIScroller(self.source_list_box.rect.topright,
                                                 self.source_list_box.image.get_height(),
                                                 self.source_list_box.max_show,
                                                 layer=16)  # scroll bar for source list

        for index, team in enumerate(self.team_coa):
            if index == 0:
                self.army_stat.add(
                    menu.ArmyStat(self.screen_scale,
                                  (team.rect.bottomleft[0], self.screen_rect.height / 1.5)))  # left army stat
            else:
                self.army_stat.add(
                    menu.ArmyStat(self.screen_scale,
                                  (team.rect.bottomright[0], self.screen_rect.height / 1.5)))  # right army stat

        self.change_source([self.source_scale_text[self.map_source], self.source_text[self.map_source]],
                           self.source_scale[self.map_source])

        self.menu_button.add(*self.team_select_button)
        self.main_ui.add(*self.team_select_button, self.map_option_box, self.enactment_tick_box,
                         self.source_list_box,
                         self.source_scroll, self.army_stat)


def team_select_process(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if mouse_left_up or mouse_left_down:
        if mouse_left_up:
            for this_team in self.team_coa:  # User select any team by clicking on coat of arm
                if this_team.rect.collidepoint(self.mouse_pos):
                    self.team_selected = this_team.team
                    this_team.change_select(True)

                    # Reset team selected on team user not currently selected
                    for this_team2 in self.team_coa:
                        if self.team_selected != this_team2.team and this_team2.selected:
                            this_team2.change_select(False)
                    break

            for index, name in enumerate(self.source_namegroup):  # user select source
                if name.rect.collidepoint(self.mouse_pos):  # click on source name
                    self.map_source = index
                    self.change_source(
                        [self.source_scale_text[self.map_source], self.source_text[self.map_source]],
                        self.source_scale[self.map_source])
                    break

            for box in self.tick_box:
                if box in self.main_ui and box.rect.collidepoint(self.mouse_pos):
                    if box.tick is False:
                        box.change_tick(True)
                    else:
                        box.change_tick(False)
                    if box.option == "enactment":
                        self.enactment = box.tick

        if self.source_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
            self.current_source_row = self.source_scroll.user_input(
                self.mouse_pos)  # update the scroll and get new current subsection
            setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.source_list,
                       self.source_namegroup,
                       self.source_list_box, self.main_ui)
    if self.source_list_box.rect.collidepoint(self.mouse_pos):
        self.current_source_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                              self.source_scroll, self.source_list_box,
                                              self.current_source_row, self.source_list,
                                              self.source_namegroup, self.main_ui)

    if self.map_back_button.event or esc_press:
        self.menu_state = self.last_select
        self.map_back_button.event = False
        self.main_ui.remove(*self.menu_button, self.map_listbox, self.map_option_box,
                            self.enactment_tick_box,
                            self.source_list_box, self.source_scroll, self.source_description)
        self.menu_button.remove(*self.menu_button)

        # v Reset selected team
        for team in self.team_coa:
            team.change_select(False)
        self.team_selected = 1
        # ^ End reset selected team

        self.map_source = 0
        self.map_show.change_mode(0)  # revert map preview back to without unit dot

        for group in (self.source_namegroup, self.army_stat):
            for stuff in group:  # remove map name item
                stuff.kill()
                del stuff

        if self.menu_state == "preset_map":  # regenerate map name list
            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.preset_map_list, self.map_namegroup,
                       self.map_listbox,
                       self.main_ui)
        else:
            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup,
                       self.map_listbox,
                       self.main_ui)

        self.menu_button.add(*self.map_select_button)
        self.main_ui.add(*self.map_select_button, self.map_listbox, self.map_scroll, self.map_description)

    elif self.start_button.event:  # start self button
        self.start_button.event = False
        start_battle(self)


def start_battle(self):
    self.battle_game.prepare_new_game(self.ruleset, self.ruleset_folder, self.team_selected,
                                      self.enactment,
                                      self.preset_map_folder[self.current_map_select],
                                      self.map_source,
                                      self.source_scale[self.map_source], "battle")
    self.battle_game.run_game()
    pygame.mixer.music.unload()
    pygame.mixer.music.set_endevent(self.SONG_END)
    pygame.mixer.music.load(self.music_list[0])
    pygame.mixer.music.play(-1)
    gc.collect()  # collect no longer used object in previous battle from memory