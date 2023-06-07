import pygame

from engine.uimenu.uimenu import ListAdapter
from engine.uibattle.uibattle import TempUnitIcon
from engine.game.menu_preset_map_select import leader_popup_text


def menu_custom_unit_setup(self, esc_press):

    if self.map_back_button.event_press or esc_press:
        self.menu_state = "custom_map"
        self.remove_ui_updater(self.troop_list_box, self.custom_unit_list_box, self.unit_icon, self.custom_unit_list_select)

        self.map_preview.change_mode(1, camp_pos_list=self.play_map_data["camp_pos"])  # revert map preview back to without unit dot

        for this_team in self.team_coa:  # Get and make camp icon for current selected team
            if this_team.team == self.team_selected:
                for icon in self.camp_icon:
                    icon.kill()
                self.camp_icon = []
                if this_team.team in self.play_map_data["camp_pos"]:
                    for camp in self.play_map_data["camp_pos"][this_team.team]:
                        self.camp_icon.append(TempUnitIcon(this_team.team, camp[1], 0))
                    self.camp_icon.append(TempUnitIcon(this_team.team, "+", 0))

        self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

        self.add_ui_updater(self.custom_battle_map_list_box, self.custom_map_option_box, self.night_battle_tick_box,
                            self.weather_custom_select, self.wind_custom_select, self.custom_battle_faction_list_box)

    elif self.select_button.event_press:  # go to unit leader setup screen
        can_continue = True
        if len(self.play_map_data["unit"]["pos"]) > 1:
            for team in self.play_map_data["unit"]["pos"]:
                for coa in self.team_coa:
                    if coa.team == team and 0 not in coa.coa_images and \
                            (not self.play_map_data["unit"]["pos"][team] or
                             len([this_unit for this_unit in self.play_source_data["unit"] if this_unit["Team"] == team]) != len(
                                self.play_map_data["unit"]["pos"][team])):
                        can_continue = False
        else:
            can_continue = False

        if can_continue is False:
            self.input_popup = ("confirm_input", "warning")
            self.input_ui.change_instruction("Need all units placed")
            self.add_ui_updater(self.inform_ui_popup)
        else:
            self.menu_state = "custom_leader_setup"

            self.remove_ui_updater(self.troop_list_box, self.unit_icon, self.select_button, self.custom_unit_list_select)

            for stuff in self.map_namegroup:  # remove name item
                stuff.kill()
                del stuff

            self.add_ui_updater(self.org_chart, self.start_button)

            leader_change_team_unit(self)

    elif self.team_coa_box.mouse_over:
        for this_team in self.team_coa:  # User select any team by clicking on coat of arm
            if this_team.mouse_over:
                shown_id = ("team", this_team.coa_images)
                if self.text_popup.last_shown_id != shown_id:
                    if 0 in this_team.coa_images:
                        if not this_team.coa_images[0]:
                            text = ["None"]
                        else:
                            text = ["All Factions"]
                    else:
                        text = [self.faction_data.faction_name_list[faction] for faction in this_team.coa_images]
                    unit_data = [0, 0, 0]
                    for unit in self.play_source_data["unit"]:
                        if unit["Team"] == this_team.team:
                            unit_data[0] += 1
                            for troop_id, troop in unit["Troop"].items():
                                unit_data[1] += int(troop[0])
                                unit_data[2] += int(troop[1])
                    text.append("Leader: " + str(unit_data[0]) + " Active Troop: " + str(
                        unit_data[1]) + " Reserve Troop: " + str(unit_data[2]))

                    self.text_popup.popup(self.cursor.rect, text, shown_id=shown_id)
                else:
                    self.text_popup.popup(self.cursor.rect, None, shown_id=shown_id)
                self.add_ui_updater(self.text_popup)
            if this_team.event_press:
                self.team_selected = this_team.team
                this_team.change_select(True)

                for this_team2 in self.team_coa:
                    if self.team_selected != this_team2.team and this_team2.selected:
                        this_team2.change_select(False)

                unit_change_team_unit(self, new_faction=True)
                break

    elif self.map_preview.mouse_over:
        if self.cursor.is_alt_select_just_up:
            for icon in self.unit_icon:
                if icon.selected:
                    map_pos = (
                        int(self.cursor.pos[0] - self.map_preview.rect.x) * self.map_preview.map_scale_width,
                        int((self.cursor.pos[1] - self.map_preview.rect.y) * self.map_preview.map_scale_height))
                    if icon.who.name != "+":  # choose pos of selected unit
                        self.play_map_data["unit"]["pos"][icon.who.team][icon.who.index] = map_pos
                        self.play_source_data["unit"][icon.who.map_id]["POS"] = map_pos
                        self.map_preview.change_mode(1, team_pos_list=self.play_map_data["unit"]["pos"],
                                                     camp_pos_list=self.play_map_data["camp_pos"],
                                                     selected=self.play_map_data["unit"]["pos"][icon.who.team][
                                                         icon.who.index])
                        unit_change_team_unit(self, old_selected=icon.who.index)
                    break

    elif self.unit_model_room.mouse_over:
        if self.unit_selected is not None:
            leader_id = [item for item in self.play_source_data['unit'] if
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
                    popup_text = leader_popup_text(self, icon)
                    self.text_popup.popup(self.cursor.rect, popup_text)
                    self.add_ui_updater(self.text_popup)
                    if icon.event_press:
                        for other_icon in self.unit_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                        self.unit_selected = icon.who.map_id
                        if icon.who.team in self.play_map_data["unit"]["pos"] and \
                                icon.who.index in self.play_map_data["unit"]["pos"][icon.who.team]:
                            # highlight selected unit in preview map
                            self.map_preview.change_mode(1, team_pos_list=self.play_map_data["unit"]["pos"],
                                                         camp_pos_list=self.play_map_data["camp_pos"],
                                                         selected=self.play_map_data["unit"]["pos"][icon.who.team][
                                                             icon.who.index])
                        if icon.who.map_id is not None:
                            who_todo = {key: value for key, value in self.leader_data.leader_list.items() if
                                        key == icon.who.troop_id}
                            preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True)
                            self.unit_model_room.add_preview_model(
                                model=preview_sprite_pool[icon.who.troop_id]["sprite"],
                                coa=icon.who.coa)
                        else:
                            self.unit_model_room.add_preview_model()
                            self.map_preview.change_mode(1, team_pos_list=self.team_pos,
                                                         camp_pos_list=self.play_map_data["camp_pos"])

                    elif self.cursor.is_alt_select_just_up:  # remove unit
                        if icon.who.name != "+":
                            if icon.who.index in self.play_map_data["unit"]["pos"][icon.who.team]:
                                self.play_map_data["unit"]["pos"][icon.who.team].pop(icon.who.index)
                            self.play_source_data["unit"].pop(icon.who.map_id)

                            for icon2 in self.unit_icon:
                                if icon2.who.index and icon2.who.index > icon.who.index:
                                    if icon2.who.index in self.play_map_data["unit"]["pos"][icon.who.team]:
                                        self.play_map_data["unit"]["pos"][icon.who.team][icon2.who.index - 1] = \
                                            self.play_map_data["unit"]["pos"][icon.who.team].pop(icon2.who.index)
                                        if icon2.who.team == icon.who.team:
                                            self.play_source_data["unit"][icon2.who.map_id]["Temp Leader"] = ""
                                    icon2.who.index -= 1

                            self.map_preview.change_mode(1, team_pos_list=self.play_map_data["unit"]["pos"],
                                                         camp_pos_list=self.play_map_data["camp_pos"])

                            for map_id, subunit in enumerate(self.play_source_data["unit"]):
                                if subunit["Team"] == self.team_selected:
                                    subunit["Temp Leader"] = ""  # reset leader structure when unit got removed
                                    subunit["ID"] = map_id  # reset map id

                            if not icon.selected:  # find new selected
                                for icon2 in self.unit_icon:
                                    if icon2.selected:
                                        self.map_preview.change_mode(1,
                                                                     team_pos_list=self.play_map_data["unit"]["pos"],
                                                                     camp_pos_list=self.play_map_data["camp_pos"],
                                                                     selected=self.play_map_data["unit"]["pos"][
                                                                         icon2.who.team][icon2.who.index])
                                        self.unit_selected = icon2.who.map_id
                                        break
                            unit_change_team_unit(self)
                    break


def leader_change_team_unit(self):
    for this_team in self.team_coa:
        if this_team.selected:
            for icon in self.preview_unit:
                icon.kill()
            self.preview_unit.empty()

            for unit_index, unit in enumerate(self.play_source_data["unit"]):
                if this_team.team == unit["Team"]:
                    if unit["Leader ID"] in self.leader_data.images:
                        image = self.leader_data.images[unit["Leader ID"]]
                    else:
                        image = self.leader_data.leader_list[unit["Leader ID"]]["Name"].split(" ")[0]
                    add_unit = TempUnitIcon(this_team.team, image, unit_index, map_id=unit["ID"],
                                            coa=self.faction_data.coa_list[self.leader_data.leader_list[
                                                unit["Leader ID"]]["Faction"]])
                    add_unit.troop_id = unit["Leader ID"]
                    self.preview_unit.add(add_unit)
            self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

            break


def unit_change_team_unit(self, new_faction=False, old_selected=None, add_plus=True):
    """Player select another team"""
    for this_team in self.team_coa:
        if this_team.selected:
            for icon in self.preview_unit:
                icon.kill()
            self.preview_unit.empty()

            unit_list = []
            if "Team Faction " + str(this_team.team) in self.play_map_data["info"]:
                for unit_index, unit in enumerate(self.play_source_data["unit"]):
                    if unit["Team"] == this_team.team:
                        if unit["Leader ID"] in self.leader_data.images:
                            image = self.leader_data.images[unit["Leader ID"]]
                        else:
                            image = self.leader_data.leader_list[unit["Leader ID"]]["Name"].split(" ")[0]

                        if unit_index in self.play_map_data["unit"]["pos"][this_team.team] and add_plus:
                            # unit placed on map, put in black-green colour in portrait
                            if type(image) is str:
                                add_subunit = TempUnitIcon(this_team.team, image, unit_index, map_id=unit["ID"],
                                                           coa=self.faction_data.coa_list[self.leader_data.leader_list[
                                                               unit["Leader ID"]]["Faction"]])
                                self.preview_unit.add(add_subunit)
                                new_image = pygame.Surface(self.leader_data.images["0"].get_size(), pygame.SRCALPHA)
                                pygame.draw.circle(new_image, (20, 150, 60),
                                                   (new_image.get_width() / 2, new_image.get_height() / 2),
                                                   new_image.get_width() / 2, width=int(10 * self.screen_scale[1]))
                                add_subunit.portrait.blit(new_image, new_image.get_rect(topleft=(0, 0)))
                            else:
                                new_image = pygame.Surface(image.get_size())
                                new_image.blit(image, image.get_rect(topleft=(0, 0)))
                                pygame.draw.circle(new_image, (20, 150, 60),
                                                   (new_image.get_width() / 2, new_image.get_height() / 2),
                                                   new_image.get_width() / 2, width=int(10 * self.screen_scale[1]))
                                add_subunit = TempUnitIcon(this_team.team, image, unit_index, map_id=unit["ID"],
                                                           coa=self.faction_data.coa_list[self.leader_data.leader_list[
                                                               unit["Leader ID"]]["Faction"]])
                                self.preview_unit.add(add_subunit)
                            add_subunit.troop_id = unit["Leader ID"]
                        else:
                            add_subunit = TempUnitIcon(this_team.team, image, unit_index, map_id=unit["ID"],
                                                       coa=self.faction_data.coa_list[self.leader_data.leader_list[
                                                           unit["Leader ID"]]["Faction"]])
                            self.preview_unit.add(add_subunit)
                            add_subunit.troop_id = unit["Leader ID"]

                if add_plus:
                    self.preview_unit.add(TempUnitIcon(this_team.team, "+", None))

                unit_list = create_unit_list(self, this_team)

            if new_faction:
                self.remove_ui_updater(self.troop_list_box)
                self.troop_list_box.__init__(self.troop_list_box.origin, self.troop_list_box.pivot,
                                             self.troop_list_box.relative_size_inside_container,
                                             ListAdapter(unit_list,
                                                        replace_on_select=custom_unit_list_on_select,
                                                        replace_on_mouse_over=custom_unit_list_on_mouse_over),
                                             self.troop_list_box.parent,
                                             self.troop_list_box.item_size,
                                             layer=self.troop_list_box._layer)
                self.add_ui_updater(self.troop_list_box)

            self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

            if old_selected is not None:
                for icon in self.unit_icon:
                    if icon.who.index == old_selected:
                        icon.selection()

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


def custom_unit_list_on_mouse_over(self, item_index, item_text):
    game = self.game
    for coa in game.team_coa:
        if coa.selected:  # get unit for selected team
            unit_data = create_unit_list(game, coa, unit_selected=item_text)
            popup_text = [game.leader_data.leader_list[unit_data["Leader ID"]]["Name"]]  # make popup of unit data
            for troop in unit_data["Troop"]:
                popup_text += [game.troop_data.troop_list[troop]["Name"] + ": " +
                               str(unit_data["Troop"][troop][0]) + " + " +
                               str(unit_data["Troop"][troop][1])]
            game.text_popup.popup(game.cursor.rect, popup_text)
            game.add_ui_updater(game.text_popup)
            break


def custom_unit_list_on_select(self, item_index, item_text):
    """
    Method for unit list where player can add unit into the current selected team
    :param self: ListUI object
    :param item_index: Index of selected item in list
    :param item_text: Text of selected item
    """
    game = self.game
    self.last_index = item_index
    for coa in game.team_coa:
        if coa.selected:  # get unit for selected team
            if game.cursor.is_select_just_up:
                has_unit_selected = False
                for this_unit in game.unit_icon:
                    if this_unit.selected:
                        if this_unit.who.name == "+":  # add new unit
                            add_unit_data(game, coa, item_text)
                            old_selected = None
                        else:  # change existed
                            unit_data = make_unit_data(game, coa, item_text)
                            unit_data["ID"] = this_unit.who.map_id
                            game.play_source_data["unit"][this_unit.who.map_id] = unit_data
                            old_selected = this_unit.who.index

                            if this_unit.who.map_id is not None:
                                who_todo = {key: value for key, value in self.game.leader_data.leader_list.items() if
                                            key == this_unit.who.troop_id}
                                preview_sprite_pool, _ = self.game.create_troop_sprite_pool(who_todo, preview=True)
                                self.game.unit_model_room.add_preview_model(
                                    model=preview_sprite_pool[this_unit.who.troop_id]["sprite"],
                                    coa=this_unit.who.coa)

                        has_unit_selected = True
                        unit_change_team_unit(game, old_selected=old_selected)
                        game.map_preview.change_mode(1,
                                                     team_pos_list=game.play_map_data["unit"]["pos"],
                                                     camp_pos_list=game.play_map_data["camp_pos"], selected=old_selected)
                        break

                if not has_unit_selected:  # no unit selected, consider as adding new unit
                    for coa in game.team_coa:
                        if coa.selected:  # add unit for selected team
                            add_unit_data(game, coa, item_text)
                            unit_change_team_unit(game)
                            game.map_preview.change_mode(1, team_pos_list=game.play_map_data["unit"]["pos"],
                                                         camp_pos_list=game.play_map_data["camp_pos"])
            break


def make_unit_data(game, coa, item_text):
    unit_data = create_unit_list(game, coa, unit_selected=item_text).copy()
    unit_data["Team"] = coa.team
    unit_data["Temp Leader"] = ""
    return unit_data


def add_unit_data(game, coa, item_text):
    if coa.team not in game.play_map_data["unit"]:
        game.play_map_data["unit"][coa.team] = []
    unit_data = make_unit_data(game, coa, item_text)
    game.play_map_data["unit"][coa.team].append(unit_data)
    game.play_source_data["unit"].append(unit_data)
    unit_data["ID"] = len(game.play_source_data["unit"]) - 1