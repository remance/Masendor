import pygame


def loading_screen(self, state):
    if state == "start":
        self.cursor.change_image("load")
        self.screen.blit(self.loading, (0, 0))  # blit loading screen after intro
    elif state == "end":
        self.cursor.change_image("normal")
    pygame.display.update()
