from engine.uimenu import uimenu
from engine import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image


def menu_preset_map_select(self, mouse_scroll_up, mouse_scroll_down, esc_press):
    self.main_ui_updater.remove(self.single_text_popup)
    for this_team in self.team_coa:  # User select any team by clicking on coat of arm
        if this_team.event_press:
            self.team_selected = this_team.team
            this_team.change_select(True)

            # Reset team selected on team user not currently selected
            for this_team2 in self.team_coa:
                if self.team_selected != this_team2.team and this_team2.selected:
                    this_team2.change_select(False)

            for icon in self.preview_unit:
                icon.kill()
            self.preview_unit.empty()

            self.setup_battle_unit(self.preview_unit, preview=self.team_selected)

            self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

            for index, icon in enumerate(self.unit_icon):  # select first unit
                self.unit_selected = icon.who.map_id
                icon.selection()
                who_todo = {key: value for key, value in self.leader_data.leader_list.items() if
                            key == icon.who.troop_id}
                preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True)
                self.map_preview.change_mode(1, team_pos_list=self.team_pos,
                                             camp_pos_list=self.camp_pos,
                                             selected=icon.who.base_pos)
                self.unit_model_room.add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"],
                                                       icon.who.coa)
                break
            return

    for index, name in enumerate(self.map_namegroup):  # user click on map name, change map
        if name.event_press:
            self.current_map_select = index
            self.map_source = 0
            self.team_selected = 1
            self.map_selected = self.preset_map_folder[self.current_map_select]
            self.change_battle_source()
            return

    for index, name in enumerate(self.source_namegroup):  # user select source
        if name.event_press:  # click on source name
            self.map_source = index
            self.team_selected = 1
            self.change_battle_source()
            return

    for box in (self.observe_mode_tick_box,):
        if box.event_press:
            if box.tick is False:
                box.change_tick(True)
            else:
                box.change_tick(False)
            if box.option == "observe":
                self.enactment = box.tick

    if self.map_list_box.event_press:  # click on subsection list scroll
        self.current_map_row = self.map_list_box.scroll.player_input(
            self.cursor.pos)  # update the scroll and get new current subsection
        setup_list(self.screen_scale, uimenu.NameList, self.current_map_row, self.preset_map_list,
                   self.map_namegroup, self.map_list_box,
                   self.main_ui_updater)

    elif self.source_list_box.event_press:  # click on subsection list scroll
        self.current_source_row = self.source_list_box.scroll.player_input(
            self.mouse_pos)  # update the scroll and get new current subsection
        setup_list(self.screen_scale, uimenu.NameList, self.current_source_row, self.source_name_list,
                   self.source_namegroup, self.source_list_box, self.main_ui_updater)

    elif self.map_back_button.event_press or esc_press:
        self.menu_state = self.last_select
        self.main_ui_updater.remove(*self.menu_button, self.map_list_box, self.map_list_box.scroll, self.map_option_box,
                                    self.observe_mode_tick_box, self.source_list_box, self.source_list_box.scroll,
                                    self.army_stat, self.map_preview, self.team_coa, self.map_title, self.unit_selector, self.unit_selector.scroll,
                                    tuple(self.unit_stat.values()), self.unit_model_room)
        self.menu_button.remove(*self.menu_button)

        # Reset selected team
        for team in self.team_coa:
            team.change_select(False)
        self.team_selected = 1

        self.map_source = 0
        self.map_preview.change_mode(0)  # revert map preview back to without unit dot

        for group in (self.map_namegroup, self.team_coa, self.source_namegroup, self.preview_unit,
                      self.unit_icon):  # remove map name, source name and coa item
            for stuff in group:
                stuff.kill()
                del stuff

        self.preview_unit.empty()

        self.back_mainmenu()

    elif self.start_button.event_press:  # Start Battle
        self.start_battle(self.unit_selected)

    elif self.map_list_box.mouse_over:
        self.current_map_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                           self.map_list_box.scroll, self.map_list_box, self.current_map_row,
                                           self.preset_map_list, self.map_namegroup, self.main_ui_updater)

    elif self.source_list_box.mouse_over:
        self.current_source_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                              self.source_list_box.scroll, self.source_list_box,
                                              self.current_source_row, self.source_name_list,
                                              self.source_namegroup, self.main_ui_updater)

    elif self.unit_selector.mouse_over:
        if mouse_scroll_up:
            if self.unit_selector.current_row > 0:
                self.unit_selector.current_row -= 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        elif mouse_scroll_down:
            if self.unit_selector.current_row < self.unit_selector.row_size:
                self.unit_selector.current_row += 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        elif self.unit_selector.scroll.event:
            new_row = self.unit_selector.scroll.player_input(self.mouse_pos)
            if self.unit_selector.current_row != new_row:
                self.unit_selector.current_row = new_row
                self.unit_selector.scroll.change_image(new_row=new_row, row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        else:
            for index, icon in enumerate(self.unit_icon):
                if icon.mouse_over:
                    popup_text = leader_popup_text(self, icon)
                    self.single_text_popup.pop(self.cursor.pos, popup_text)
                    self.main_ui_updater.add(self.single_text_popup)
                    if icon.event_press:
                        for other_icon in self.unit_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                        # self.unit_stat["unit"].add_leader_stat(icon.who, self.leader_data, self.troop_data)
                        who_todo = {key: value for key, value in self.leader_data.leader_list.items() if
                                    key == icon.who.troop_id}
                        preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True)
                        self.unit_model_room.add_preview_model(preview_sprite_pool[icon.who.troop_id]["sprite"],
                                                               icon.who.coa)
                        self.map_preview.change_mode(1, team_pos_list=self.team_pos,
                                                     camp_pos_list=self.camp_pos,
                                                     selected=icon.who.base_pos)

                        self.unit_selected = icon.who.map_id
                    break


def change_char(self):
    self.main_ui_updater.add(self.unit_selector, self.unit_selector.scroll,
                             tuple(self.unit_stat.values()), *self.unit_select_button)
    self.menu_button.add(*self.unit_select_button)


def leader_popup_text(self, icon):
    who = icon.who

    stat = self.leader_data.leader_list[who.troop_id]

    leader_skill = ""
    for skill in who.skill:
        leader_skill += self.leader_data.skill_list[skill]["Name"] + ", "
    leader_skill = leader_skill[:-2]
    primary_main_weapon = stat["Primary Main Weapon"]
    if not primary_main_weapon:  # replace empty with standard unarmed
        primary_main_weapon = (1, 3)
    primary_sub_weapon = stat["Primary Sub Weapon"]
    if not primary_sub_weapon:  # replace empty with standard unarmed
        primary_sub_weapon = (1, 3)
    secondary_main_weapon = stat["Secondary Main Weapon"]
    if not secondary_main_weapon:  # replace empty with standard unarmed
        secondary_main_weapon = (1, 3)
    secondary_sub_weapon = stat["Secondary Sub Weapon"]
    if not secondary_sub_weapon:  # replace empty with standard unarmed
        secondary_sub_weapon = (1, 3)

    leader_primary_main_weapon = self.troop_data.equipment_grade_list[primary_main_weapon[1]]["Name"] + " " + \
                                 self.troop_data.weapon_list[primary_main_weapon[0]]["Name"] + ", "
    leader_primary_sub_weapon = self.troop_data.equipment_grade_list[primary_sub_weapon[1]]["Name"] + " " + \
                                self.troop_data.weapon_list[primary_sub_weapon[0]]["Name"]
    leader_secondary_main_weapon = self.troop_data.equipment_grade_list[secondary_main_weapon[1]]["Name"] + " " + \
                                   self.troop_data.weapon_list[secondary_main_weapon[0]]["Name"] + ", "
    leader_secondary_sub_weapon = self.troop_data.equipment_grade_list[secondary_sub_weapon[1]]["Name"] + " " + \
                                  self.troop_data.weapon_list[secondary_sub_weapon[0]]["Name"]
    leader_armour = "No Armour"
    if stat["Armour"]:
        leader_armour = self.troop_data.equipment_grade_list[stat["Armour"][1]]["Name"] + " " + \
                        self.troop_data.armour_list[stat["Armour"][0]]["Name"]

    leader_mount = "None"
    if stat["Mount"]:
        leader_mount = self.troop_data.mount_grade_list[stat["Mount"][1]]["Name"] + ", " + \
                       self.troop_data.mount_list[stat["Mount"][0]]["Name"] + ", " + \
                       self.troop_data.mount_armour_list[stat["Mount"][2]]["Name"]

    popup_text = [who.name,
                  self.localisation.grab_text(("ui", "Social Class")) + ": " + who.social["Leader Social Class"],
                  self.localisation.grab_text(("ui", "Authority")) + ": " + str(who.leader_authority),
                  self.localisation.grab_text(("ui", "Command")) + ": " +
                  self.localisation.grab_text(("ui", "Melee")) + ":" + self.skill_level_text[who.melee_command] + " " +
                  self.localisation.grab_text(("ui", "Ranged")) + ":" + self.skill_level_text[who.range_command] + " " +
                  self.localisation.grab_text(("ui", "cavalry_short")) + ":" + self.skill_level_text[who.cav_command],
                  self.localisation.grab_text(("ui", "Skill")) + ": " + leader_skill,
                  self.localisation.grab_text(("ui", "1st_main_weapon")) + ": " + leader_primary_main_weapon,
                  self.localisation.grab_text(("ui", "1st_sub_weapon")) + ": " + leader_primary_sub_weapon,
                  self.localisation.grab_text(("ui", "2nd_main_weapon")) + ": " + leader_secondary_main_weapon,
                  self.localisation.grab_text(("ui", "2nd_sub_weapon")) + ": " + leader_secondary_sub_weapon,
                  self.localisation.grab_text(("ui", "Armour")) + ": " + leader_armour,
                  self.localisation.grab_text(("ui", "Mount")) + ": " + leader_mount]

    for item in self.play_source_data["unit"]:
        if item["ID"] == icon.who.map_id:
            for troop, value in item["Troop"].items():
                popup_text += [self.troop_data.troop_list[troop]["Name"] + ": " +
                               value]
            break

    return popup_text
