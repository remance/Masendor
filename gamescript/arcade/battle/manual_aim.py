import pygame


def manual_aim(self, key_press, mouse_left_up, mouse_right_up, mouse_scroll_up, mouse_scroll_down):
    """
    Range attack aim with player manual control.
    """
    shoot_text = ""
    shoot_ready = [0, 0]
    has_ammo = [0, 0]
    shoot_ready_list = [[], []]
    self.battle_ui_updater.add(self.single_text_popup)
    if self.player_input_state == "leader aim":
        if self.player_char.equipped_weapon in self.player_char.ammo_now:
            for weapon in self.player_char.ammo_now[self.player_char.equipped_weapon]:
                shoot_distance = self.player_char.base_pos.distance_to(self.command_mouse_pos)
                shoot_range = self.player_char.shoot_range[weapon]
                if (self.player_char.ammo_now[self.player_char.equipped_weapon][
                    weapon]) > 0 and shoot_range >= shoot_distance:
                    shoot_ready_list[weapon].append(self.player_char)
                    shoot_ready[weapon] += 1
                shoot_text += str(self.player_char.ammo_now[self.player_char.equipped_weapon][weapon]) + "/" + \
                              str(self.player_char.magazine_count[self.player_char.equipped_weapon][
                                      weapon]) + " Range " + \
                              str(int(shoot_distance)) + "/" + str(int(shoot_range)) + ", "
            shoot_text = shoot_text[:-2]

    elif self.player_input_state == "volley aim" or self.player_input_state == "troop aim":
        for weapon in (0, 1):
            for this_subunit in self.player_char.unit.alive_subunit_list:
                if self.player_input_state == "volley aim" or (
                        self.player_input_state == "troop aim" and this_subunit.leader is None):
                    if this_subunit.equipped_weapon in this_subunit.ammo_now:
                        if weapon in this_subunit.ammo_now[this_subunit.equipped_weapon]:
                            has_ammo[weapon] += 1
                            shoot_distance = this_subunit.base_pos.distance_to(self.command_mouse_pos)
                            if this_subunit.ammo_now[this_subunit.equipped_weapon][weapon] > 0:
                                if this_subunit.shoot_range[weapon] >= shoot_distance:
                                    shoot_ready_list[weapon].append(this_subunit)
                                    shoot_ready[weapon] += 1
            shoot_text += str(shoot_ready[weapon]) + "/" + str(has_ammo[weapon]) + ", "
        shoot_text = shoot_text[:-2]

    self.single_text_popup.pop(self.cursor.rect.bottomright, shoot_text)

    if key_press == pygame.K_q:  # Cancel manual aim
        self.camera_zoom = self.max_camera_zoom
        self.camera_zoom_change()
        self.cursor.change_image("normal")
        self.battle_ui_updater.remove(self.single_text_popup)
        self.player_input_state = None
        for this_subunit in self.player_char.unit.alive_subunit_list:
            if this_subunit.equipped_weapon != this_subunit.player_equipped_weapon:
                this_subunit.player_weapon_selection()
    elif mouse_left_up and shoot_ready[0] > 0:
        for this_subunit in shoot_ready_list[0]:
            this_subunit.command_action = {"name": "Action 0", "range attack": True, "pos": self.command_mouse_pos, "arc shot": False}  # TODO rework this to add direct shot check
    elif mouse_right_up and shoot_ready[1] > 0:
        for this_subunit in shoot_ready_list[1]:
            this_subunit.command_action = {"name": "Action 1", "range attack": True, "pos": self.command_mouse_pos, "arc shot": False}
    elif self.map_scale_delay == 0:
        if mouse_scroll_up:
            self.camera_zoom += 1
            if self.camera_zoom > self.max_camera_zoom:
                self.camera_zoom = self.max_camera_zoom
            else:
                self.camera_zoom_change()
        elif mouse_scroll_down:
            self.camera_zoom -= 1
            if self.camera_zoom < 1:
                self.camera_zoom = 1
            else:
                self.camera_zoom_change()
