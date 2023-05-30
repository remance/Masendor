import pygame

from pygame.transform import rotate

from engine.uimenu.uimenu import UIMenu


class MenuRotate(UIMenu):
    def __init__(self, pos, image, rotate_speed):
        UIMenu.__init__(self, player_interact=False, has_containers=True)
        self.image = image
        self.image_base = self.image.copy()
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.rotate_speed = rotate_speed
        self.angle = 0

    def update(self):
        self.angle += self.game.dt * self.rotate_speed
        if self.angle > 360:  # reset back
            self.angle -= 360
        self.image = rotate(self.image_base.copy(), self.angle)
        self.rect = self.image.get_rect(center=self.pos)


class MenuActor(UIMenu):
    def __init__(self, pos, images):
        UIMenu.__init__(self, has_containers=True)
        self.current_animation = images
        self.pos = pos
        self.frame_timer = 0
        self.animation_frame_play_time = 0.1
        self.show_frame = 0
        self.image = self.current_animation[self.show_frame]["sprite"]
        self.rect = self.image.get_rect(midbottom=self.pos)

    def update(self):
        self.frame_timer += self.game.dt
        if self.frame_timer >= self.animation_frame_play_time:
            self.frame_timer = 0
            if self.show_frame < len(self.current_animation) - 1:
                self.show_frame += 1
                self.image = self.current_animation[self.show_frame]["sprite"]
            else:
                self.show_frame = 0
                self.image = self.current_animation[self.show_frame]["sprite"]
            self.rect = self.image.get_rect(midbottom=self.pos)

        # self.image = rotate(self.image, self.angle)
