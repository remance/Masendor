from engine.game.menu_custom_unit_setup import unit_change_team_unit
from engine.uibattle.uibattle import TempUnitIcon


def menu_custom_map_select(self, esc_press):
    if self.weather_list_box in self.main_ui_updater:
        if not self.weather_list_box.mouse_over and self.cursor.is_select_just_up:  # click other stuffs
            self.remove_ui_updater(self.weather_list_box)

    if self.map_back_button.event or esc_press:

        for icon in self.unit_icon:
            icon.kill()
        self.unit_icon.empty()

        self.remove_ui_updater(*self.map_select_button, self.custom_battle_map_list_box,
                               self.custom_battle_faction_list_box, self.custom_map_option_box, self.unit_selector,
                               self.unit_selector.scroll, self.weather_custom_select, self.wind_custom_select,
                               self.custom_map_option_box, self.night_battle_tick_box, self.map_preview,
                               self.unit_model_room, self.weather_list_box, self.map_title, self.team_coa_box)

        for stuff in self.team_coa:
            stuff.kill()
            del stuff

        self.back_mainmenu()

    elif self.select_button.event:  # select this map and team list, go to unit setup screen
        if len([coa for coa in self.team_coa if coa.name is not None and coa.name != "None"]) > 1:  # enough team to play
            self.menu_state = "custom_unit_setup"

            self.add_ui_updater(self.custom_preset_army_list_box, self.unit_list_box)

            for icon in self.unit_icon:
                icon.kill()
            self.unit_icon.empty()

            self.remove_ui_updater(self.custom_battle_map_list_box, self.custom_map_option_box,
                                   self.night_battle_tick_box,
                                   self.weather_custom_select, self.wind_custom_select,
                                   self.custom_battle_faction_list_box)

            unit_change_team_unit(self, new_faction=True)

        else:
            self.input_popup = ("confirm_input", "warning")
            self.input_ui.change_instruction("Require at least 2 teams")
            self.add_ui_updater(self.inform_ui_popup)

    elif self.team_coa_box.mouse_over:
        for this_team in self.team_coa:  # User select any team by clicking on coat of arm
            if this_team.event_press:
                self.team_selected = this_team.team
                this_team.change_select(True)

                for icon in self.camp_icon:
                    icon.kill()
                self.camp_icon = []
                if this_team.team in self.play_map_data["camp_pos"]:
                    for camp in self.play_map_data["camp_pos"][this_team.team]:
                        self.camp_icon.append(TempUnitIcon(this_team.team, camp[1], 0))
                    self.camp_icon.append(TempUnitIcon(this_team.team, "+", 0))
                self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

                for this_team2 in self.team_coa:
                    if self.team_selected != this_team2.team and this_team2.selected:
                        this_team2.change_select(False)
                break

    elif self.custom_map_option_box.mouse_over:
        if self.night_battle_tick_box.event_press:
            if self.night_battle_tick_box.tick is False:
                self.night_battle_tick_box.change_tick(True)
            else:
                self.night_battle_tick_box.change_tick(False)
            battle_time = "09:00:00"
            if self.night_battle_tick_box.tick:  # check for night battle
                battle_time = "21:00:00"
            self.play_map_data["info"]["weather"][0][1] = battle_time

        elif self.weather_custom_select.event_press:
            self.weather_list_box.change_origin_with_pos(self.cursor.pos)
            self.add_ui_updater(self.weather_list_box)

        elif self.wind_custom_select.event_press:
            self.input_popup = ("text_input", "wind")
            self.input_ui.change_instruction("Wind Direction Degree:")
            self.add_ui_updater(self.input_ui_popup)

    if self.cursor.is_alt_select_just_up and self.map_preview.mouse_over:
        for index, icon in enumerate(self.unit_icon):  # place selected camp on map, require camp size input
            if icon.selected:
                map_pos = (
                    (int(self.cursor.pos[0] - self.map_preview.rect.x) * self.map_preview.map_scale_width),
                    int((self.cursor.pos[1] - self.map_preview.rect.y) * self.map_preview.map_scale_height))
                if icon.who.name == "+":
                    self.input_popup = ("text_input", "custom_camp_size/" + str(map_pos) + "/" +
                                        str(icon.who.team))
                    self.input_ui.change_instruction("Camp Size Value:")
                    self.add_ui_updater(self.input_ui_popup)
                else:
                    self.play_map_data["camp_pos"][icon.who.team][index][0] = map_pos
                self.map_preview.change_mode(1, camp_pos_list=self.play_map_data["camp_pos"])
                break

    elif self.unit_selector.mouse_over:
        if self.cursor.scroll_up:
            if self.unit_selector.current_row > 0:
                self.unit_selector.current_row -= 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

        elif self.cursor.scroll_down:
            if self.unit_selector.current_row < self.unit_selector.row_size:
                self.unit_selector.current_row += 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

        elif self.unit_selector.scroll.event:
            new_row = self.unit_selector.scroll.player_input(self.cursor.pos)
            if self.unit_selector.current_row != new_row:
                self.unit_selector.current_row = new_row
                self.unit_selector.scroll.change_image(new_row=new_row, row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

        else:
            for index, icon in enumerate(self.unit_icon):
                if icon.mouse_over:
                    if icon.event_press:
                        for other_icon in self.unit_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                    elif self.cursor.is_alt_select_just_up:  # right click remove icon
                        if icon.who.name != "+":
                            self.play_map_data["camp_pos"][icon.who.team].pop(index)
                            icon.kill()
                            self.camp_icon.pop(index)
                            self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)
                    self.map_preview.change_mode(1, camp_pos_list=self.play_map_data["camp_pos"])
                    break


def custom_map_list_on_select(self, item_index, item_text):
    self.last_index = item_index
    game = self.game
    game.current_map_select = item_index
    game.map_selected = game.battle_map_folder[game.current_map_select]
    game.create_preview_map()


def custom_faction_list_on_select(self, item_index, item_text):
    """
    Method for faction list where player can select faction into the current selected team
    :param self: Listui object
    :param item_index: Index of selected item in list
    :param item_text: Text of selected item
    """
    from engine.uibattle.uibattle import TempUnitIcon
    self.last_index = item_index
    game = self.game
    for coa in game.team_coa:  # check for selected team
        if coa.selected:
            if item_text != "None":  # Select faction
                faction_index = game.faction_data.faction_name_list.index(item_text)
                if game.cursor.is_select_just_up:
                    if "Team Faction " + str(coa.team) in game.play_map_data["info"]:
                        if faction_index not in game.play_map_data["info"]["Team Faction " + str(coa.team)]:
                            game.play_map_data["info"]["Team Faction " + str(coa.team)].append(
                                faction_index)
                    else:
                        game.play_map_data["info"]["Team Faction " + str(coa.team)] = [faction_index]
                    coa.change_coa(
                        {int(faction): game.faction_data.coa_list[int(faction)] for faction in
                         game.play_map_data["info"]["Team Faction " + str(coa.team)]},
                        game.faction_data.faction_list[game.play_map_data["info"][
                            "Team Faction " + str(coa.team)][0]]["Name"])
                elif game.cursor.is_alt_select_just_up:
                    if "Team Faction " + str(coa.team) in game.play_map_data["info"]:
                        if faction_index in game.play_map_data["info"]["Team Faction " + str(coa.team)]:
                            game.play_map_data["info"]["Team Faction " + str(coa.team)].remove(
                                faction_index)
                        if game.play_map_data["info"]["Team Faction " + str(coa.team)]:  # still not empty
                            coa.change_coa(
                                {int(faction): game.faction_data.coa_list[int(faction)] for faction in
                                 game.play_map_data["info"]["Team Faction " + str(coa.team)]},
                                game.faction_data.faction_list[game.play_map_data["info"][
                                    "Team Faction " + str(coa.team)][0]]["Name"])
                        else:  # list empty remove data
                            game.play_map_data["info"].pop("Team Faction " + str(coa.team))
                            coa.change_coa({0: None}, "None")
            else:  # select None faction, remove all in team
                if game.cursor.is_select_just_up and "Team Faction " + str(coa.team) in game.play_map_data["info"]:
                    game.play_map_data["info"].pop("Team Faction " + str(coa.team))
                coa.change_coa({0: None}, "None")

            if "Team Faction " + str(coa.team) in game.play_map_data["info"]:  # team now exist
                game.play_map_data["unit"][coa.team] = []
                game.play_map_data["unit"]["pos"][coa.team] = {}

                if coa.team not in game.play_map_data["camp_pos"]:  # new team, camp not exist
                    game.play_map_data["camp_pos"][coa.team] = []
                    for icon in game.camp_icon:
                        icon.kill()
                    game.camp_icon = []

                if not game.camp_icon or game.camp_icon[-1].name != "+":
                    game.camp_icon.append(TempUnitIcon(coa.team, "+", 0))

            else:  # team no longer exist
                if coa.team in game.play_map_data["unit"]:
                    game.play_map_data["unit"].pop(coa.team)
                    game.play_map_data["unit"]["pos"].pop(coa.team)

                    if coa.team in game.play_map_data["camp_pos"]:
                        game.play_map_data["camp_pos"].pop(coa.team)
                        for icon in game.camp_icon:
                            icon.kill()
                        game.camp_icon = []

            game.unit_selector.setup_unit_icon(game.unit_icon, game.camp_icon)
            break


def custom_weather_list_on_select(self, item_index, item_text):
    game = self.game
    self.last_index = item_index
    game.weather_custom_select.rename("Weather: " + item_text)
    battle_time = "09:00:00"
    if game.night_battle_tick_box.tick:  # check for night battle
        battle_time = "21:00:00"
    game.play_map_data["info"]["weather"] = \
        [[int(game.battle_map_data.weather_list.index(item_text) / 3), battle_time,
          game.play_map_data["info"]["weather"][0][2],
          ("Light", "Normal", "Strong").index(item_text.split(" ")[0])]]
    game.remove_ui_updater(game.weather_list_box)
