import gc
import pygame

from gamescript import menu, battleui
from gamescript.common import utility
from gamescript.common.ui import selector

setup_list = utility.setup_list
list_scroll = utility.list_scroll
edit_config = utility.edit_config
load_image = utility.load_image
clean_group_object = utility.clean_group_object
setup_unit_icon = selector.setup_unit_icon


def main_menu_process(self, mouse_left_up):

    if self.preset_map_button.event:  # preset map list menu
        self.menu_state = "preset_map"
        self.last_select = self.menu_state

        self.current_map_select = 0
        self.map_selected = self.preset_map_folder[self.current_map_select]

        self.preset_map_button.event = False
        self.main_ui_updater.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                                    *self.popup_namegroup)
        self.menu_button.remove(*self.menu_button)

        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.preset_map_list, self.map_namegroup,
                   self.map_listbox, self.main_ui_updater)
        self.make_preview_map(self.preset_map_folder, self.preset_map_list)

        self.menu_button.add(*self.map_select_button)
        self.main_ui_updater.add(*self.map_select_button, self.map_listbox, self.map_title, self.map_scroll)

    elif self.custom_map_button.event:  # custom map list menu
        self.menu_state = "custom"
        self.last_select = self.menu_state

        self.current_map_select = 0
        self.map_selected = self.custom_map_folder[self.current_map_select]

        self.custom_map_button.event = False
        self.main_ui_updater.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                                    *self.popup_namegroup)
        self.menu_button.remove(*self.menu_button)

        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup,
                   self.map_listbox,
                   self.main_ui_updater)
        self.make_preview_map(self.custom_map_folder, self.custom_map_list)

        self.menu_button.add(*self.map_select_button)
        self.main_ui_updater.add(*self.map_select_button, self.map_listbox, self.map_title, self.map_scroll)

    elif self.game_edit_button.event:  # custom subunit/sub-subunit editor menu
        self.menu_state = "game_creator"
        self.game_edit_button.event = False
        self.main_ui_updater.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                                    *self.popup_namegroup)
        self.menu_button.remove(*self.menu_button)

        self.menu_button.add(*self.editor_button)
        self.main_ui_updater.add(*self.editor_button)

    elif self.option_button.event:  # change start_set menu to option menu
        self.menu_state = "option"
        self.option_button.event = False
        self.main_ui_updater.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                                    *self.popup_namegroup)
        self.menu_button.remove(*self.menu_button)

        self.menu_button.add(*self.option_menu_button)
        self.main_ui_updater.add(*self.menu_button, self.option_menu_slider, self.value_box)
        self.main_ui_updater.add(*self.option_icon_list)

    elif self.lore_button.event:  # open encyclopedia
        self.before_lore_state = self.menu_state
        self.menu_state = "encyclopedia"
        self.main_ui_updater.add(self.encyclopedia, self.lore_name_list, *self.lore_button_ui,
                                 self.lore_scroll)  # add sprite related to encyclopedia
        self.encyclopedia.change_section(0, self.lore_name_list, self.subsection_name, self.lore_scroll, self.page_button,
                                         self.main_ui_updater)
        self.lore_button.event = False

    elif mouse_left_up and self.profile_box.rect.collidepoint(self.mouse_pos):
        self.text_input_popup = ("text_input", "profile_name")
        self.input_box.text_start(self.profile_name)
        self.input_ui.change_instruction("Profile Name:")
        self.main_ui_updater.add(self.input_ui_popup)

    elif mouse_left_up and self.genre_change_box.rect.collidepoint(self.mouse_pos):
        self.popup_list_open(self.genre_change_box.rect.bottomleft, self.genre_list, "genre")

    elif self.popup_listbox in self.main_ui_updater:
        if self.popup_listbox.rect.collidepoint(self.mouse_pos):
            self.ui_click = True
            for index, name in enumerate(self.popup_namegroup):
                if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # click on name in list
                    self.change_genre(index)

                    for thisname in self.popup_namegroup:  # remove troop name list
                        thisname.kill()
                        del thisname

                    self.main_ui_updater.remove(self.popup_listbox, self.popup_list_scroll)
                    break

        elif self.popup_list_scroll.rect.collidepoint(self.mouse_pos):  # scrolling on list
            self.ui_click = True
            self.current_popup_row = self.popup_list_scroll.user_input(
                self.mouse_pos)  # update the scroller and get new current subsection
            setup_list(self.screen_scale, menu.NameList, self.current_popup_row, self.genre_list,
                       self.popup_namegroup, self.popup_listbox, self.main_ui_updater)

        # else:
        #     self.main_ui.remove(self.popup_listbox, self.popup_list_scroll, *self.popup_namegroup)


def game_creator_process(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.editor_back_button.event or esc_press:
        self.editor_back_button.event = False
        self.back_mainmenu()

    elif self.unit_edit_button.event:
        self.unit_edit_button.event = False
        self.battle_game.prepare_new_game(self.ruleset, self.ruleset_folder, 1, True, None, 1, (1, 1, 1, 1),
                                          "unit_editor")
        self.battle_game.run_game()
        pygame.mixer.music.unload()
        pygame.mixer.music.set_endevent(self.SONG_END)
        pygame.mixer.music.load(self.music_list[0])
        pygame.mixer.music.play(-1)


def option_menu_process(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.back_button.event or esc_press:  # back to start_set menu
        self.back_button.event = False

        self.main_ui_updater.remove(*self.option_icon_list, self.option_menu_slider, self.value_box)

        self.back_mainmenu()

    if mouse_left_up or mouse_left_down:
        if self.volume_slider.rect.collidepoint(self.mouse_pos) and (
                mouse_left_down or mouse_left_up):  # mouse click on slider bar
            self.volume_slider.user_input(self.mouse_pos,
                                          self.value_box[0])  # update slider button based on mouse value
            self.master_volume = float(
                self.volume_slider.value / 100)  # for now only music volume slider exist
            edit_config("DEFAULT", "master_volume", str(self.volume_slider.value), "configuration.ini",
                        self.config)
            pygame.mixer.music.set_volume(self.master_volume)

        if mouse_left_up:
            if self.resolution_drop.rect.collidepoint(self.mouse_pos):  # click on resolution bar
                if self.resolution_bar in self.main_ui_updater:  # remove the bar list if click again
                    self.main_ui_updater.remove(self.resolution_bar)
                    self.menu_button.remove(self.resolution_bar)
                else:  # add bar list
                    self.main_ui_updater.add(self.resolution_bar)
                    self.menu_button.add(self.resolution_bar)

            else:
                for bar in self.resolution_bar:  # loop to find which resolution bar is selected, this happens outside of clicking check below
                    if bar.event:
                        bar.event = False
                        self.resolution_drop.change_state(bar.text)  # change button value based on new selected value
                        resolution_change = bar.text.split()
                        self.new_screen_width = resolution_change[0]
                        self.new_screen_height = resolution_change[2]

                        edit_config("DEFAULT", "screen_width", self.new_screen_width, "configuration.ini",
                                    self.config)
                        edit_config("DEFAULT", "screen_height", self.new_screen_height, "configuration.ini",
                                    self.config)
                        self.screen = pygame.display.set_mode(self.screen_rect.size,
                                                              self.window_style | pygame.RESIZABLE, self.best_depth)
                        break
                self.main_ui_updater.remove(self.resolution_bar)


def map_select_process(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if mouse_left_up or mouse_left_down:
        if mouse_left_up:
            for index, name in enumerate(self.map_namegroup):  # user click on map name, change map
                if name.rect.collidepoint(self.mouse_pos):
                    self.current_map_select = index
                    if self.menu_state == "preset_map":  # make new map image
                        self.map_selected = self.preset_map_folder[self.current_map_select]
                        self.make_preview_map(self.preset_map_folder, self.preset_map_list)
                    else:
                        self.map_selected = self.custom_map_folder[self.current_map_select]
                        self.make_preview_map(self.custom_map_folder, self.custom_map_list)
                    break

        if self.map_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
            self.current_map_row = self.map_scroll.user_input(
                self.mouse_pos)  # update the scroll and get new current subsection
            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.preset_map_list,
                       self.map_namegroup, self.map_listbox,
                       self.main_ui_updater)

    if self.map_listbox.rect.collidepoint(self.mouse_pos):
        self.current_map_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.map_scroll,
                                           self.map_listbox,
                                           self.current_map_row, self.preset_map_list, self.map_namegroup, self.main_ui_updater)

    if self.map_back_button.event or esc_press:
        self.map_back_button.event = False
        self.current_map_row = 0

        self.main_ui_updater.remove(self.map_listbox, self.map_show, self.map_scroll, self.map_description,
                                    self.team_coa, self.map_title)

        for group in (self.map_namegroup, self.team_coa):
            for stuff in group:
                stuff.kill()
                del stuff

        self.back_mainmenu()

    elif self.select_button.event:  # select this map, go to team/source selection screen
        self.current_source_row = 0
        self.menu_state = "team_select"
        self.select_button.event = False

        self.main_ui_updater.remove(*self.map_select_button, self.map_listbox, self.map_scroll, self.map_description)
        self.menu_button.remove(*self.map_select_button)

        for stuff in self.map_namegroup:  # remove map name item
            stuff.kill()
            del stuff

        change_to_source_selection(self)


def team_select_process(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if mouse_left_up or mouse_left_down:
        if mouse_left_up:
            change_team_coa(self)
            for index, name in enumerate(self.source_namegroup):  # user select source
                if name.rect.collidepoint(self.mouse_pos):  # click on source name
                    self.map_source = index
                    team_army, team_leader = self.read_source(
                        [self.source_scale_text[self.map_source], self.source_text[self.map_source]])
                    self.change_source(self.source_scale[self.map_source], team_army, team_leader)
                    break

            for box in self.tick_box:
                if box in self.main_ui_updater and box.rect.collidepoint(self.mouse_pos):
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
                       self.source_list_box, self.main_ui_updater)
    if self.source_list_box.rect.collidepoint(self.mouse_pos):
        self.current_source_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                              self.source_scroll, self.source_list_box,
                                              self.current_source_row, self.source_list,
                                              self.source_namegroup, self.main_ui_updater)

    if self.map_back_button.event or esc_press:
        self.menu_state = self.last_select
        self.map_back_button.event = False
        self.main_ui_updater.remove(*self.menu_button, self.map_listbox, self.map_option_box,
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
                       self.main_ui_updater)
        else:
            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup,
                       self.map_listbox,
                       self.main_ui_updater)

        self.menu_button.add(*self.map_select_button)
        self.main_ui_updater.add(*self.map_select_button, self.map_listbox, self.map_scroll, self.map_description)

    elif self.start_button.event:  # start battle button
        self.start_button.event = False
        start_battle(self)

    elif self.select_button.event:  # go to character select screen
        self.menu_state = "char_select"
        self.select_button.event = False
        self.char_select_row = 0
        self.char_selected = 0

        self.main_ui_updater.remove(*self.map_select_button, self.map_option_box, self.enactment_tick_box,
                                    self.source_list_box, self.source_scroll, self.source_description, self.army_stat)
        self.menu_button.remove(*self.map_select_button)

        for group in (self.map_namegroup, self.team_coa):  # remove no longer related sprites in group
            for stuff in group:
                stuff.kill()
                del stuff

        self.char_stat["char"] = menu.ArmyStat(self.screen_scale,
                                               (self.screen_rect.center[0] / 2.5, self.screen_rect.height / 2.5),
                                               load_image(self.main_dir, self.screen_scale,
                                                          "char_stat.png", "ui\\mapselect_ui"))  # char stat
        self.char_stat["troop"] = menu.ArmyStat(self.screen_scale,
                                                (self.screen_rect.center[0] * 1.6, self.screen_rect.height / 2.5),
                                                load_image(self.main_dir, self.screen_scale,
                                                           "char_stat.png", "ui\\mapselect_ui"))  # troop stat

        team_selected = self.team_selected
        if self.enactment:
            team_selected = None

        self.unit_setup(self.preview_char, self.troop_data.troop_list, specific_team=team_selected)

        setup_unit_icon(self.char_selector, self.unit_icon, self.preview_char, self.char_selector_scroll, icon_scale=1)

        for index, icon in enumerate(self.unit_icon):  # select first char
            icon.selection()
            self.char_stat["char"].add_leader_stat(icon.unit.leader[0])
            self.map_show.change_mode(1, team_pos_list=self.team_pos, selected=icon.unit.base_pos)
            break

        for index, unit in enumerate(self.preview_char):
            if index == 0:  # get for adding subunit to preview
                get_unit = unit
            for subunit in unit.subunits:  # change subunit pos to preview box
                subunit.pos = (self.char_stat["troop"].rect.topleft[0] + (subunit.unit_position[0] * subunit.image.get_width() / 5),
                               self.char_stat["troop"].rect.topleft[1] + ((subunit.unit_position[1] + 4) * subunit.image.get_height() / 5))
                subunit.rect = subunit.image.get_rect(center=subunit.pos)

        self.main_ui_updater.add(self.char_selector, self.char_selector_scroll,
                                 list(self.char_stat.values()), *self.char_select_button, get_unit.subunits)
        self.menu_button.add(*self.char_select_button)


def char_select_process(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.char_back_button.event or esc_press:  # go back to team/source selection screen
        self.current_source_row = 0
        self.menu_state = "team_select"
        self.char_back_button.event = False

        self.main_ui_updater.remove(self.char_selector, self.char_selector_scroll,
                                    list(self.char_stat.values()), *self.char_select_button)
        self.menu_button.remove(*self.char_select_button)

        clean_group_object((self.subunit, self.leader, self.preview_char,
                            self.unit_icon, self.troop_number_sprite,
                            self.inspect_subunit))

        change_to_source_selection(self)

        self.make_team_coa([self.map_data[self.map_title.name]["Team 1"],
                            self.map_data[self.map_title.name]["Team 2"]], self.main_ui_updater)

    elif self.start_button.event:  # start battle button
        self.start_button.event = False
        start_battle(self, self.char_selected)

    elif self.char_selector_scroll.rect.collidepoint(self.mouse_pos):
        if mouse_left_down or mouse_left_up:
            new_row = self.char_selector_scroll.user_input(self.mouse_pos)
            if self.char_selector.current_row != new_row:
                self.char_selector.current_row = new_row
                setup_unit_icon(self.char_selector, self.unit_icon, self.preview_char,
                                self.char_selector_scroll, icon_scale=1)

    elif self.char_selector.rect.collidepoint(self.mouse_pos) and mouse_left_up:
        for index, icon in enumerate(self.unit_icon):
            if icon.rect.collidepoint(self.mouse_pos):
                for other_icon in self.unit_icon:
                    if other_icon.selected:  # unselected all others first
                        other_icon.selection()
                        self.main_ui_updater.remove(other_icon.unit.subunits)
                icon.selection()
                self.char_stat["char"].add_leader_stat(icon.unit.leader[0])
                self.map_show.change_mode(1, team_pos_list=self.team_pos, selected=icon.unit.base_pos)

                self.main_ui_updater.add(icon.unit.subunits)

                self.char_selected = index
                break

    elif self.char_stat["troop"].rect.collidepoint(self.mouse_pos):
        for icon in self.unit_icon:
            if icon.selected:
                for subunit in icon.unit.subunits:
                    if subunit.rect.collidepoint(self.mouse_pos):
                        self.main_ui_updater.add(self.char_popup)
                        self.char_popup.pop(self.mouse_pos, subunit.name)

    else:
        self.main_ui_updater.remove(self.char_popup)


def read_source(self, description_text):
    """Change source description and add new subunit dot when select new source"""
    self.source_description.change_text(description_text)
    self.main_ui_updater.add(self.source_description)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    unit_info = self.read_selected_map_data(openfolder, "unit_pos.csv", source=True)

    self.team_pos = {row["Team"]: [] for row in list(unit_info.values())}
    for row in list(unit_info.values()):
        self.team_pos[row["Team"]].append([int(item) for item in row["POS"].split(",")])

    self.map_show.change_mode(1, team_pos_list=self.team_pos)

    team_army = {row["Team"]: [] for row in list(unit_info.values())[1:]}
    team_leader = {row["Team"]: [] for row in list(unit_info.values())[1:]}
    for row in list(unit_info.values())[1:]:
        for small_row in [value for key, value in row.items() if "Row" in key]:
            for item in small_row.split(","):
                if item.isdigit():
                    team_army[row["Team"]].append(int(item))
                else:
                    team_army[row["Team"]].append(item)
            if type(row["Leader"]) == str and "," in row["Leader"]:
                for item in row["Leader"].split(","):
                    team_leader[row["Team"]].append(int(item))
            else:
                team_leader[row["Team"]].append(int(row["Leader"]))

    return team_army, team_leader


def change_source(self, scale_value, team_army, team_commander):
    """change army stat when select new source"""

    self.unit_scale = scale_value

    team_total_troop = {key: 0 for key in team_army.keys()}  # total troop number in army
    troop_type_list = {key: [0, 0, 0, 0] for key in team_army.keys()}  # total number of each troop type
    leader_name_list = {key: leader[0] for key, leader in team_commander.items()}

    for index, team in team_army.items():
        for this_unit in team:
            if this_unit != 0 and type(this_unit) != str:
                team_total_troop[index] += self.troop_data.troop_list[this_unit]["Troop"] * scale_value[index]
                troop_type = 0
                if self.troop_data.troop_list[this_unit]["Troop Class"] in (2, 4):  # range subunit
                    troop_type += 1  # range weapon and accuracy higher than melee melee_attack
                if self.troop_data.troop_list[this_unit]["Troop Class"] in (3, 4, 5, 6, 7):  # cavalry
                    troop_type += 2
                troop_type_list[index][troop_type] += int(
                    self.troop_data.troop_list[this_unit]["Troop"] * scale_value[index])
        troop_type_list[index].append(len(team))

    army_loop_list = {key: "{:,}".format(troop) + " Troops" for key, troop in team_total_troop.items()}
    army_loop_list = {key: self.leader_data.leader_list[leader_name_list[index]]["Name"] + ": " + troop for key, troop in
                       army_loop_list.items()}

    for index, army in enumerate(self.army_stat):  # + 1 index to skip neutral unit in stat
        army.add_army_stat(troop_type_list[index + 1], army_loop_list[index+ 1])


def change_to_source_selection(self):
    for team in self.team_coa:
        if self.team_selected == team.team:
            team.change_select(True)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    try:
        self.source_list = self.read_selected_map_data(openfolder, "source.csv")
        self.source_name_list = [value["Source"] for value in list(self.source_list.values())]
        self.source_scale_text = [value["Number Text"] for value in list(self.source_list.values())]
        self.source_scale = [{0: float(value["Team 0 Scale"]), 1: float(value["Team 1 Scale"]),
                              2: float(value["Team 2 Scale"]), 3: float(value["Team 3 Scale"])}
                             for value in list(self.source_list.values())]
        self.source_text = [value["Description"] for value in list(self.source_list.values())]
    except Exception:  # no source.csv make empty list
        self.source_name_list = [""]
        self.source_scale_text = [""]
        self.source_scale = [""]
        self.source_text = [""]

    setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.source_name_list,
               self.source_namegroup, self.source_list_box, self.main_ui_updater)

    self.source_scroll = battleui.UIScroller(self.source_list_box.rect.topright,
                                             self.source_list_box.image.get_height(),
                                             self.source_list_box.max_row_show,
                                             layer=16)  # scroll bar for source list

    for index, team in enumerate(self.team_coa):
        if index == 0:
            self.army_stat.add(
                menu.ArmyStat(self.screen_scale,
                              (team.rect.bottomleft[0], self.screen_rect.height / 1.5),
                              load_image(self.main_dir, self.screen_scale, "stat.png",
                                         "ui\\mapselect_ui")))  # left army stat
        else:
            self.army_stat.add(
                menu.ArmyStat(self.screen_scale,
                              (team.rect.bottomright[0], self.screen_rect.height / 1.5),
                              load_image(self.main_dir, self.screen_scale, "stat.png",
                                         "ui\\mapselect_ui")))  # right army stat

    team_army, team_leader = self.read_source([self.source_scale_text[self.map_source], self.source_text[self.map_source]])
    self.change_source(self.source_scale[self.map_source], team_army, team_leader)

    self.menu_button.add(*self.team_select_button)
    self.main_ui_updater.add(*self.team_select_button, self.map_option_box, self.enactment_tick_box,
                             self.source_list_box, self.source_scroll, self.army_stat)


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


def start_battle(self, char_selected=None):
    self.battle_game.prepare_new_game(self.ruleset, self.ruleset_folder, self.team_selected,
                                      self.enactment, self.map_selected,
                                      self.map_source, self.source_scale[self.map_source], "battle",
                                      char_selected=char_selected)
    self.battle_game.run_game()
    pygame.mixer.music.unload()
    pygame.mixer.music.set_endevent(self.SONG_END)
    pygame.mixer.music.load(self.music_list[0])
    pygame.mixer.music.play(-1)
    gc.collect()  # collect no longer used object in previous battle from memory

