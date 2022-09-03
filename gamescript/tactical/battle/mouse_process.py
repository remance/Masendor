import pygame


def mouse_process(self, mouse_left_up, mouse_right_up, double_mouse_right, mouse_left_down, key_state):
    if self.terrain_check in self.battle_ui_updater and (
            self.terrain_check.pos != self.mouse_pos or key_state[pygame.K_s] or key_state[pygame.K_w] or key_state[
        pygame.K_a] or key_state[pygame.K_d]):
        self.battle_ui_updater.remove(self.terrain_check)  # remove terrain popup when move mouse or camera

    if self.mini_map.rect.collidepoint(self.mouse_pos):  # mouse position on mini map
        self.click_any = True
        if mouse_left_up:  # move self camera to position clicked on mini map
            self.base_camera_pos = pygame.Vector2(
                int(self.mouse_pos[0] - self.mini_map.rect.x) * self.screen_scale[0] * self.mini_map.map_scale_width,
                int(self.mouse_pos[1] - self.mini_map.rect.y) * self.screen_scale[1] * self.mini_map.map_scale_height)
            self.camera_pos = self.base_camera_pos * self.camera_zoom
            self.camera_fix()
    elif self.unit_selector.scroll.rect.collidepoint(
            self.mouse_pos):  # Must check mouse collide for scroll before unit select ui
        self.click_any = True
        if mouse_left_down or mouse_left_up:
            new_row = self.unit_selector.scroll.player_input(self.mouse_pos)
            if self.unit_selector.current_row != new_row:
                self.unit_selector.current_row = new_row
                self.unit_selector.setup_unit_icon(self.unit_icon, self.all_team_unit[self.team_selected])

    elif self.unit_selector.rect.collidepoint(self.mouse_pos):  # check mouse collide for unit selector ui
        self.click_any = True
        self.unit_icon_mouse_over(mouse_left_up, mouse_right_up)

    elif self.test_button in self.battle_ui_updater and self.test_button.rect.collidepoint(self.mouse_pos):
        self.click_any = True
        if mouse_left_up:
            if self.test_button.event == 0:
                self.test_button.event = 1
                new_mode = "battle"

            elif self.test_button.event == 1:
                self.test_button.event = 0
                new_mode = "editor"
            self.game_state = new_mode
            self.change_state()
