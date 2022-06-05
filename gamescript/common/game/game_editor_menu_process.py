import pygame


def game_editor_menu_process(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.editor_back_button.event or esc_press:
        self.editor_back_button.event = False
        self.back_mainmenu()

    elif self.unit_edit_button.event:
        self.unit_edit_button.event = False
        self.battle_game.prepare_new_game(self.ruleset, self.ruleset_folder, 1, True, None, 1, (1, 1, 1, 1),
                                          "unit_editor")
        self.battle_game.run_game()
        pygame.mixer.music.unload()
        pygame.mixer.music.set_endevent(self.SONG_END)
        pygame.mixer.music.load(self.music_list[0])
        pygame.mixer.music.play(-1)
