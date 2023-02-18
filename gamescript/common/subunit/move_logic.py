import random

import pygame
from gamescript.common import utility

rotation_xy = utility.rotation_xy
infinity = float("inf")


def move_logic(self, dt):
    if "forced move" not in self.current_action:
        self.base_target = self.command_target  # always attempt to catch up to command target
    else:
        self.base_target = self.forced_target

    if self.move_speed:
        if "movable" in self.current_action:  # animation allow movement
            if self.base_pos != self.base_target:
                move = self.base_target - self.base_pos
                require_move_length = move.length()  # convert length
                move.normalize_ip()
                move *= self.move_speed * dt
                new_pos = self.base_pos + move

                if (self.retreat_start or (0 < new_pos[0] < self.map_corner[0] and
                                           0 < new_pos[1] < self.map_corner[1])):
                    # cannot go pass map unless in retreat state
                    if move.length() <= require_move_length:  # move normally according to move speed
                        self.base_pos += move
                        if "forced move" not in self.current_action:  # damaged or knockdown does not change direction
                            self.new_angle = self.set_rotate(self.base_target)
                    else:  # move length pass the base_target destination, set movement to stop exactly at base_target
                        move = self.base_target - self.base_pos  # simply change move to whatever remaining distance
                        self.base_pos += move  # adjust base position according to movement
                        if "forced move" not in self.current_action:  # damaged or knockdown does not change direction
                            self.new_angle = self.set_rotate(new_pos)

                    self.pos = pygame.Vector2((self.base_pos[0] * self.screen_scale[0] * 5,
                                               self.base_pos[1] * self.screen_scale[1] * 5))
                    self.offset_pos = self.pos - self.current_animation[self.sprite_direction][self.show_frame][
                        "center_offset"]
                    self.rect.center = self.offset_pos
                    self.hitbox.rect.midtop = self.pos

                    self.height = self.get_height(self.base_pos)  # Current terrain height

                    if self.player_manual_control is False:
                        layer = int(self.base_pos[0] + (self.base_pos[1] * 10))
                        if layer < 0:
                            layer = 1
                        if self._layer != layer:
                            self.battle.battle_camera.change_layer(self, layer)

                    self.move = True

                    self.terrain, self.feature = self.get_feature(self.base_pos,
                                                                  self.base_map)  # get new terrain and feature at each subunit position

                    self.make_front_pos()

                    # momentum calculation
                    if "use momentum" in self.current_action:
                        if self.momentum < 1:
                            self.momentum += dt * self.acceleration / 100
                            if self.momentum > 1:
                                self.momentum = 1

                    elif self.momentum:  # reset charge momentum when not running
                        self.momentum -= dt
                        if self.momentum < 0:
                            self.momentum = 0

            else:  # reach target, interrupt moving animation
                if "movable" in self.current_action:  # in moving animation, interrupt it
                    self.interrupt_animation = True
                self.move_speed = 0

        elif "movable" not in self.command_action:  # has move speed but not movable animation, reset speed
            self.move_speed = 0

    else:
        if "movable" in self.current_action:  # in moving animation, interrupt it
            self.interrupt_animation = True
        if self.momentum:  # reduce charge momentum when not moving
            self.momentum -= dt
            if self.momentum < 0:
                self.momentum = 0
