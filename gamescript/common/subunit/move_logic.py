import random

import pygame
from gamescript.common import utility

rotation_xy = utility.rotation_xy
infinity = float("inf")


def move_logic(self, dt):
    if "forced move" not in self.current_action:
        self.base_target = self.command_target  # always attempt to catch up to command target

    if self.base_pos != self.base_target and "move speed" in self.current_action:
        move = self.base_target - self.base_pos
        move_length = move.length()  # convert length
        if move_length > 0:  # movement length longer than 0.1, not reach base_target yet
            move.normalize_ip()
            self.move_speed = self.current_action["move speed"]
            if "use momentum" in self.current_action:
                self.move_speed *= self.momentum
            move *= self.move_speed * dt
            new_move_length = move.length()
            new_pos = self.base_pos + move

            if self.move_speed > 0 and (self.retreat_start or (0 < new_pos[0] < self.map_corner[0] and
                                                               0 < new_pos[1] < self.map_corner[1])):
                # cannot go pass map unless in retreat state
                if new_move_length <= move_length:  # move normally according to move speed
                    self.base_pos += move
                    self.pos = pygame.Vector2((self.base_pos[0] * self.screen_scale[0] * 5,
                                               self.base_pos[1] * self.screen_scale[1] * 5))
                    self.offset_pos = self.pos - self.current_animation[self.sprite_direction][self.show_frame]["center_offset"]
                    self.rect.center = self.offset_pos  # list rect so the sprite gradually move to position on screen
                    self.new_angle = self.set_rotate(self.base_target)
                else:  # move length pass the base_target destination, set movement to stop exactly at base_target
                    move = self.base_target - self.base_pos  # simply change move to whatever remaining distance
                    self.base_pos += move  # adjust base position according to movement

                self.height = self.get_height(self.base_pos)  # Current terrain height
                self.head_height = self.height + (self.troop_size / 10)  # height for checking line of sight

                if self.player_manual_control is False:
                    layer = round(self.base_pos[0] + (self.base_pos[1] * 10), 0)
                    if layer < 0:
                        layer = 1
                    if self._layer != layer:
                        self.battle.battle_camera.change_layer(self, layer)
                else:
                    self.battle.battle_camera.change_layer(self, 999999)

                self.move = True

                self.terrain, self.feature = self.get_feature(self.base_pos,
                                                              self.base_map)  # get new terrain and feature at each subunit position

                self.make_front_pos()

                if self.is_leader:
                    for subunit in self.alive_troop_subordinate:
                        self.formation_pos_list[subunit] =  \
                            rotation_xy(self.base_pos, self.base_pos + self.formation_distance_list[subunit],
                                        self.radians_angle)  # find new follow point for subordinate

                # momentum calculation
                if "use momentum" in self.current_action:
                    if self.momentum < 1:
                        self.momentum += dt * self.acceleration / 100
                        if self.momentum > 1:
                            self.momentum = 1

                elif self.momentum > 0.1:  # reset charge momentum when not running
                    self.momentum -= dt
                    if self.momentum <= 0.1:
                        self.momentum = 0.1

        else:
            self.interrupt_animation = True
            self.command_action = {}  # no longer move, clean action

    elif "move speed" in self.current_action and "repeat" in self.current_action:
        self.interrupt_animation = True
        self.command_action = {}  # no longer move, clean action

    elif self.momentum > 0.1:  # reduce charge momentum when not moving
        self.momentum -= dt
        if self.momentum <= 0.1:
            self.momentum = 0.1
