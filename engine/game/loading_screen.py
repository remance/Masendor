import pygame


def loading_screen(self, state):
    if state == "start":
        # self.cursor.change_image("load")
        self.screen.blit(self.loading, (0, 0))  # blit loading screen after intro
    elif state == "end":
        self.cursor.change_image("normal")
    else:
        loading = self.loading.copy()
        font = pygame.font.Font(self.ui_font["main_button"], int(60 * self.screen_scale[1]))
        text_surface = font.render(state, True, (255, 255, 255))
        text_rect = text_surface.get_rect(bottomleft=(0, self.screen.get_height()))
        loading.blit(text_surface, text_rect)
        self.screen.blit(loading, (0, 0))
    pygame.display.update()
