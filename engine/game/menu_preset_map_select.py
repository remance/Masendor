from engine.uibattle.uibattle import TempUnitIcon


def menu_preset_map_select(self, esc_press):
    if self.team_coa_box.mouse_over:
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

                # Reset team selected on team user not currently selected
                for this_team2 in self.team_coa:
                    if self.team_selected != this_team2.team and this_team2.selected:
                        this_team2.change_select(False)

                for icon in self.preview_unit:
                    icon.kill()
                self.preview_unit.empty()

                self.preview_unit.add(TempUnitIcon(this_team.team, "None", "None", None))
                self.setup_battle_unit(self.preview_unit, preview=self.team_selected)

                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

                return

    elif self.map_back_button.event_press or esc_press:
        self.menu_state = self.last_select
        self.remove_ui_updater(self.start_button, self.map_back_button, self.preset_map_list_box,
                               self.map_preview, self.team_coa,
                               self.unit_selector, self.unit_selector.scroll,
                               self.unit_model_room, self.map_title, self.team_coa_box)

        # Reset selected team
        for team in self.team_coa:
            team.change_select(False)
        self.team_selected = 1

        self.map_source_selected = 0
        self.map_preview.change_mode(0)  # revert map preview back to without unit dot

        for group in (self.team_coa, self.preview_unit, self.unit_icon):  # remove group item no longer used
            for stuff in group:
                stuff.kill()
                del stuff

        self.preview_unit.empty()

        self.back_mainmenu()

    elif self.start_button.event_press:  # Start Battle
        self.start_battle(self.unit_selected)

    elif self.unit_model_room.mouse_over:
        if self.unit_selected is not None:
            leader_id = [item for item in self.play_map_data[self.map_source_selected]['unit'] if
                                               item["ID"] == self.unit_selected][0]["Leader ID"]
            self.text_popup.popup(self.cursor.rect,
                                  (self.leader_data.leader_lore[leader_id]["Description"],),
                                  shown_id=("model", leader_id, self.unit_selected),
                                  width_text_wrapper=500)
            self.add_ui_updater(self.text_popup)

    elif self.unit_selector.mouse_over:
        if self.cursor.scroll_up:
            if self.unit_selector.current_row > 0:
                self.unit_selector.current_row -= 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        elif self.cursor.scroll_down:
            if self.unit_selector.current_row < self.unit_selector.row_size:
                self.unit_selector.current_row += 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        elif self.unit_selector.scroll.event:
            new_row = self.unit_selector.scroll.player_input(self.cursor.pos)
            if self.unit_selector.current_row != new_row:
                self.unit_selector.current_row = new_row
                self.unit_selector.scroll.change_image(new_row=new_row, row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        else:
            for index, icon in enumerate(self.unit_icon):
                if icon.mouse_over:
                    shown_id = ("icon", icon.who.name)
                    if self.text_popup.last_shown_id != shown_id:
                        popup_text = leader_popup_text(self, icon)
                        self.text_popup.popup(self.cursor.rect, popup_text, shown_id=shown_id)
                    else:
                        self.text_popup.popup(self.cursor.rect, None, shown_id=shown_id)
                    self.add_ui_updater(self.text_popup)
                    if icon.event_press:
                        for other_icon in self.unit_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                        # self.unit_stat["unit"].add_leader_stat(icon.who, self.leader_data, self.troop_data)
                        if icon.who.map_id is not None:
                            who_todo = {key: value for key, value in self.leader_data.leader_list.items() if
                                        key == icon.who.troop_id}
                            preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True)
                            self.unit_model_room.add_preview_model(
                                model=preview_sprite_pool[icon.who.troop_id]["sprite"],
                                coa=icon.who.coa)
                            self.map_preview.change_mode(1, team_pos_list=self.team_pos,
                                                         camp_pos_list=self.play_map_data["camp_pos"],
                                                         selected=icon.who.base_pos)

                            self.unit_selected = icon.who.map_id
                        else:
                            self.unit_selected = None
                            self.unit_model_room.add_preview_model()
                            self.map_preview.change_mode(1, team_pos_list=self.team_pos,
                                                         camp_pos_list=self.play_map_data["camp_pos"])
                    break


def leader_popup_text(self, icon):
    who = icon.who
    if not hasattr(who, "troop_id"):  # None unit for enactment mode
        if who.name == "None":
            return [who.name, "Selecting this unit lets you observe the battle between AI."]
        elif who.name == "+":
            return ["Add new unit"]
    else:
        stat = self.leader_data.leader_list[who.troop_id]

        leader_skill = ""
        for skill in stat["Skill"]:
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
                                     self.troop_data.weapon_list[primary_main_weapon[0]]["Name"]
        leader_primary_sub_weapon = self.troop_data.equipment_grade_list[primary_sub_weapon[1]]["Name"] + " " + \
                                    self.troop_data.weapon_list[primary_sub_weapon[0]]["Name"]
        leader_secondary_main_weapon = self.troop_data.equipment_grade_list[secondary_main_weapon[1]]["Name"] + " " + \
                                       self.troop_data.weapon_list[secondary_main_weapon[0]]["Name"]
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
                      self.localisation.grab_text(("ui", "Social Class")) + ": " +
                      self.leader_data.leader_class[stat["Social Class"]]["Leader Social Class"],
                      self.localisation.grab_text(("ui", "Authority")) + ": " + str(stat["Charisma"]),
                      self.localisation.grab_text(("ui", "Command")) + ": " +
                      self.localisation.grab_text(("ui", "Melee")) + ":" + self.skill_level_text[
                          stat["Melee Speciality"]] + " " +
                      self.localisation.grab_text(("ui", "Ranged")) + ":" + self.skill_level_text[
                          stat["Range Speciality"]] + " " +
                      self.localisation.grab_text(("ui", "cavalry_short")) + ":" + self.skill_level_text[
                          stat["Cavalry Speciality"]],
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
                    new_value = value
                    if type(new_value) is list:
                        new_value = str(new_value[0]) + "/" + str(new_value[1])
                    popup_text += [self.troop_data.troop_list[troop]["Name"] + ": " +
                                   new_value]
                break
        return popup_text
