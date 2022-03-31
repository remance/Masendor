import pygame


def ui_mouse_over(self):
    """mouse over ui that is not subunit card and unitbox (topbar and commandbar)"""
    for this_ui in self.ui_updater:
        if this_ui in self.battle_ui_updater and this_ui.rect.collidepoint(self.mouse_pos):
            self.click_any = True
            break
    return self.click_any


def leader_mouse_over(self, mouse_right):  # TODO make it so button and leader popup not show at same time
    """process user mouse input on leader portrait in command ui"""
    leader_mouse_over = False
    for this_leader in self.leader_now:
        if this_leader.rect.collidepoint(self.mouse_pos):
            if this_leader.unit.commander:
                army_position = self.leader_level[this_leader.army_position]
            else:
                army_position = self.leader_level[this_leader.army_position + 4]

            self.leader_popup.pop(self.mouse_pos, army_position + ": " + this_leader.name)  # popup leader name when mouse over
            self.battle_ui_updater.add(self.leader_popup)
            leader_mouse_over = True

            if mouse_right:
                self.popout_lorebook(8, this_leader.leader_id)
            break
    return leader_mouse_over


def effect_icon_mouse_over(self, icon_list, mouse_right):
    effect_mouse_over = False
    for icon in icon_list:
        if icon.rect.collidepoint(self.mouse_pos):
            check_value = self.troop_card_ui.value2[icon.icon_type]
            self.effect_popup.pop(self.mouse_pos, check_value[icon.game_id])
            self.battle_ui_updater.add(self.effect_popup)
            effect_mouse_over = True
            if mouse_right:
                if icon.icon_type == 0:  # Trait
                    section = 7
                elif icon.icon_type == 1:  # Skill
                    section = 6
                else:
                    section = 5  # Status effect
                self.popout_lorebook(section, icon.game_id)
            break
    return effect_mouse_over


def troop_card_button_click(self, who):
    for button in self.troop_card_button:  # Change subunit card option based on button clicking
        if button.rect.collidepoint(self.mouse_pos):
            self.click_any = True
            if self.troop_card_ui.option != button.event:
                self.troop_card_ui.option = button.event
                self.troop_card_ui.value_input(who=who, weapon_data=self.weapon_data,
                                               armour_data=self.armour_data,
                                               change_option=1, split=self.split_happen)

                if self.troop_card_ui.option == 2:
                    self.trait_skill_blit()
                    self.effect_icon_blit()
                    self.countdown_skill_icon()
                else:
                    self.kill_effect_icon()
            break


def camera_process(self, key_state):
    if self.camera_mode == "Free":
        if key_state[pygame.K_s] or self.mouse_pos[1] >= self.bottom_corner:  # Camera move down
            self.base_camera_pos[1] += 4 * (
                    11 - self.camera_zoom)  # need "11 -" for converting cameral scale so the further zoom camera move faster
            self.camera_pos[1] = self.base_camera_pos[1] * self.camera_zoom  # resize camera pos
            self.camera_fix()

        elif key_state[pygame.K_w] or self.mouse_pos[1] <= 5:  # Camera move up
            self.base_camera_pos[1] -= 4 * (11 - self.camera_zoom)
            self.camera_pos[1] = self.base_camera_pos[1] * self.camera_zoom
            self.camera_fix()

        if key_state[pygame.K_a] or self.mouse_pos[0] <= 5:  # Camera move left
            self.base_camera_pos[0] -= 4 * (11 - self.camera_zoom)
            self.camera_pos[0] = self.base_camera_pos[0] * self.camera_zoom
            self.camera_fix()

        elif key_state[pygame.K_d] or self.mouse_pos[0] >= self.right_corner:  # Camera move right
            self.base_camera_pos[0] += 4 * (11 - self.camera_zoom)
            self.camera_pos[0] = self.base_camera_pos[0] * self.camera_zoom
            self.camera_fix()

        if self.map_scale_delay > 0:  # player change map scale once before
            self.map_scale_delay += self.ui_dt
            if self.map_scale_delay >= 0.1:  # delay for 1 second until user can change scale again
                self.map_scale_delay = 0
    elif self.camera_mode == "Follow":
        self.base_camera_pos = self.player_char.base_pos
        self.camera_pos = self.base_camera_pos * self.camera_zoom
        self.camera_fix()
