import pygame


def mouse_process(self, mouse_left_up, mouse_right_up, double_mouse_right, mouse_left_down, key_state):
    if self.terrain_check in self.battle_ui_updater and (self.terrain_check.pos != self.mouse_pos
                                                         or key_state[pygame.K_s] or key_state[pygame.K_w] or
                                                         key_state[pygame.K_a] or key_state[pygame.K_d]):
        self.battle_ui_updater.remove(self.terrain_check)  # remove terrain popup when move mouse or camera

    if self.test_button in self.battle_ui_updater and self.test_button.rect.collidepoint(self.mouse_pos):
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
