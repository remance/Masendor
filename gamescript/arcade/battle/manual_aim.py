import pygame


def manual_aim(self, key_press, mouse_pos, mouse_left_up, mouse_right_up):
    ammo_text = ""
    if self.player_input_state == "leader aim":
        if self.player_char.equipped_weapon in self.player_char.ammo_now:
            for weapon in self.player_char.ammo_now[self.player_char.equipped_weapon]:
                ammo_text += str(self.player_char.ammo_now[self.player_char.equipped_weapon][weapon]) + " " + \
                             str(int(self.player_char.weapon_cooldown[weapon])) + "/" + \
                             str(int(self.weapon_speed[weapon])) + ", "
            ammo_text = ammo_text[:-2]
    elif self.player_input_state == "volley aim":
        shoot_ready = 0
        self.player_char.unit
        ammo_text = + "/" + str(len(self.player_char.unit.alive_subunit_list))
    # elif self.player_input_state == "troop aim":
    #     ammo_text =

    self.single_text_popup.pop(self.cursor.rect.bottomright, ammo_text)
    if key_press == pygame.K_q:  # Cancel manual aim
        self.camera_zoom = 10
        self.camera_zoom_change()
        self.player_input_state = None
        self.cursor.change_image("normal")
        self.battle_ui_updater.remove(self.single_text_popup)
    if mouse_left_up:
        pass
