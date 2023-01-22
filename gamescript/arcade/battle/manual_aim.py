import math

import pygame


def manual_aim(self, mouse_left_up, mouse_right_up, mouse_scroll_up, mouse_scroll_down, key_state, key_press):
    """
    Range attack aim with player manual control.
    """
    shoot_text = ""
    shoot_ready = [0, 0]
    has_ammo = [0, 0]
    shoot_ready_list = [[], []]
    self.battle_ui_updater.add(self.single_text_popup)
    base_target_pos = self.command_mouse_pos
    target_pos = self.base_mouse_pos

    who_shoot = ()
    if self.player_input_state == "leader aim":
        who_shoot = (self.player_char,)
    elif self.player_input_state == "line aim" or self.player_input_state == "focus aim":
        who_shoot = self.player_char.unit.alive_subunit_list

    for this_subunit in who_shoot:
        clip_list = [False, False]
        range_weapon_check = [False, False]
        can_shoot = [False, False]
        arc_shot = [False, False]

        if this_subunit.state < 90:
            this_subunit.manual_shoot = True

            if self.player_input_state == "line aim":
                angle = this_subunit.unit.set_rotate(self.command_mouse_pos)
                distance = this_subunit.unit.base_pos.distance_to(self.command_mouse_pos)
                base_target_pos = pygame.Vector2(
                    this_subunit.base_pos[0] - (distance * math.sin(math.radians(angle))),
                    this_subunit.base_pos[1] - (distance * math.cos(math.radians(angle))))
                target_pos = (base_target_pos[0] * self.camera_zoom * self.screen_scale[0],
                              base_target_pos[1] * self.camera_zoom * self.screen_scale[1])

            for weapon in (0, 1):
                if this_subunit.equipped_weapon in this_subunit.ammo_now:
                    if weapon in this_subunit.ammo_now[this_subunit.equipped_weapon]:
                        range_weapon_check[weapon] = True
                        has_ammo[weapon] += 1
                        if this_subunit.ammo_now[this_subunit.equipped_weapon][weapon] > 0:
                            if this_subunit.shoot_range[weapon] >= this_subunit.base_pos.distance_to(base_target_pos):
                                weapon_arc_shot = this_subunit.check_special_effect("Arc Shot", weapon=weapon)
                                if this_subunit.check_special_effect("Arc Shot Only", weapon=weapon) is False:
                                    clip = this_subunit.check_line_of_sight(base_target_pos)
                                    clip_list[weapon] = clip
                                    if clip is False:
                                        can_shoot[weapon] = True

                                if can_shoot[weapon] is False and this_subunit.unit.shoot_mode == 0 and \
                                        weapon_arc_shot:  # check for arc shot
                                    clip_list[weapon] = False
                                    can_shoot[weapon] = True
                                    arc_shot[weapon] = True

                                if can_shoot[weapon]:
                                    shoot_ready_list[weapon].append(this_subunit)
                                    shoot_ready[weapon] += 1

        if True in range_weapon_check:
            if this_subunit.shoot_line not in self.battle_camera:  # add back shoot line
                self.battle_camera.add(this_subunit.shoot_line)
            this_subunit.shoot_line.update(base_target_pos, target_pos, clip_list, can_shoot,
                                           self.camera_zoom_image_scale, arc_shot)
        else:  # no weapon in current equipped weapon set
            if this_subunit.shoot_line in self.battle_camera:  # remove shoot line
                self.battle_camera.remove(this_subunit.shoot_line)

        shoot_text = str(shoot_ready[0]) + "/" + str(has_ammo[0]) + ", " + str(shoot_ready[1]) + "/" + str(has_ammo[1])

    self.single_text_popup.pop(self.cursor.rect.bottomright, shoot_text)

    if key_press in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d) or self.player_char.state == 100:  # Cancel manual aim when move or player die
        self.camera_zoom = self.max_camera_zoom
        self.camera_zoom_change()
        self.cursor.change_image("normal")
        self.battle_ui_updater.remove(self.single_text_popup)
        self.previous_player_input_state = self.player_input_state
        self.player_input_state = None
        for this_subunit in self.player_char.unit.alive_subunit_list:
            if this_subunit.equipped_weapon != this_subunit.player_equipped_weapon:
                this_subunit.player_weapon_selection()
        for shoot_line in self.shoot_lines:
            shoot_line.delete()  # reset shoot guide lines

    elif mouse_left_up or mouse_right_up:
        weapon = 0
        action = "Action 0"
        if mouse_right_up:
            weapon = 1
            action = "Action 1"
        if shoot_ready[weapon] > 0:
            for this_subunit in shoot_ready_list[weapon]:
                this_subunit.new_angle = this_subunit.set_rotate(this_subunit.shoot_line.base_target_pos)
                this_subunit.command_action = {"name": action, "range attack": True,
                                               "pos": this_subunit.shoot_line.base_target_pos,
                                               "arc shot": this_subunit.shoot_line.arc_shot[weapon]}

    elif self.map_scale_delay == 0 and (mouse_scroll_up or mouse_scroll_down):
        if mouse_scroll_up:
            try:
                self.camera_zoom = self.camera_zoom_level[self.camera_zoom_level.index(self.camera_zoom) + 1]
                self.camera_zoom_change()
            except IndexError:
                pass

        elif mouse_scroll_down:
            if self.camera_zoom_level.index(self.camera_zoom) > 1:
                self.camera_zoom = self.camera_zoom_level[self.camera_zoom_level.index(self.camera_zoom) - 1]
                self.camera_zoom_change()

    else:
        if key_press is not None:
            self.battle_keyboard_process(key_press)
        self.current_selected.player_input(self.command_mouse_pos, key_state=key_state)
