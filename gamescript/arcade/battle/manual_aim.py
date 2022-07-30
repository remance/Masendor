import pygame


def manual_aim(self, key_press, mouse_pos, mouse_left_up, mouse_right_up):
    ammo_text = ""
    shoot_ready = [0, 0]
    can_shoot = [0, 0]
    shoot_ready_list = [[], []]
    if self.player_input_state == "leader aim":
        if self.player_char.equipped_weapon in self.player_char.ammo_now:
            for weapon in self.player_char.ammo_now[self.player_char.equipped_weapon]:
                if (self.player_char.ammo_now[self.player_char.equipped_weapon][weapon]) > 0:  # TODO add range condition
                    shoot_ready_list[weapon].append(self.player_char)
                ammo_text += str(self.player_char.ammo_now[self.player_char.equipped_weapon][weapon]) + " " + \
                             str(int(self.player_char.weapon_cooldown[weapon])) + "/" + \
                             str(int(self.player_char.weapon_speed[weapon])) + ", "
            ammo_text = ammo_text[:-2]

    elif self.player_input_state == "volley aim" or self.player_input_state == "troop aim":
        for weapon in (0, 1):
            for this_subunit in self.player_char.unit.alive_subunit_list:
                if self.player_input_state == "volley aim" or (self.player_input_state == "troop aim" and this_subunit.leader is None):
                    if this_subunit.equipped_weapon in this_subunit.ammo_now:
                        if weapon in this_subunit.ammo_now[this_subunit.equipped_weapon]:
                            can_shoot[weapon] += 1
                            if this_subunit.ammo_now[this_subunit.equipped_weapon][weapon] > 0:
                                shoot_ready_list[weapon].append(this_subunit)
                                shoot_ready[weapon] += 1
            ammo_text += str(shoot_ready[weapon]) + "/" + str(can_shoot[weapon]) + ", "
        ammo_text = ammo_text[:-2]

    self.single_text_popup.pop(self.cursor.rect.bottomright, ammo_text)
    if key_press == pygame.K_q:  # Cancel manual aim
        self.camera_zoom = 10
        self.camera_zoom_change()
        self.player_input_state = None
        self.cursor.change_image("normal")
        self.battle_ui_updater.remove(self.single_text_popup)
    if mouse_left_up and shoot_ready[0] > 0:
        for this_subunit in shoot_ready_list[0]:
            this_subunit.command_action = ("Action " + str(0), "Range Attack", self.command_mouse_pos)
    elif mouse_right_up and shoot_ready[1] > 0:
        for this_subunit in shoot_ready_list[1]:
            this_subunit.command_action = ("Action " + str(1), "Range Attack", self.command_mouse_pos)
