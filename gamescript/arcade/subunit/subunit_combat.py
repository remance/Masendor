import random
import pygame
import numpy as np

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier
infinity = float("inf")


def change_leader(self, event):
    """Leader is subunit in arcode mode, so can't change to other subunit"""
    pass


def find_shooting_target(self, unit_state):
    """get nearby enemy base_target from list if not targeting anything yet"""
    self.attack_pos = list(self.unit.near_target.values())[0]  # replace attack_pos with enemy unit pos
    self.attack_target = list(self.unit.near_target.keys())[0]  # replace attack_target with enemy unit id
    for shoot_range in self.shoot_range:
        if shoot_range >= self.attack_pos.distance_to(self.base_pos):
            self.state = 11
            if unit_state in (1, 3, 5):  # Walk and shoot
                self.state = 12
            elif unit_state in (2, 4, 6):  # Run and shoot
                self.state = 13


def attack_logic(self, dt, combat_timer, parent_state):
    from gamescript import rangeattack

    collide_list = []
    self.melee_target = None
    if self.enemy_front != [] or self.enemy_side != []:  # Check if in combat or not with collision
        collide_list = self.enemy_front + self.enemy_side
        for subunit in collide_list:
            if self.state not in (96, 98, 99):
                self.state = 10
                self.melee_target = subunit
                if self.enemy_front == []:  # no enemy in front try to rotate to enemy at side
                    # self.base_target = self.melee_target.base_pos
                    self.new_angle = self.set_rotate(self.melee_target.base_pos)
            else:  # no way to retreat, Fight to the death
                if self.enemy_front != [] and self.enemy_side != []:  # if both front and any side got attacked
                    if 9 not in self.status_effect:
                        self.status_effect[9] = self.status_list[9].copy()  # fight to the death status
            if parent_state not in (10, 96, 98, 99):
                parent_state = 10
                self.unit.state = 10
            if self.melee_target is not None:
                self.unit.attack_target = self.melee_target.unit
            break

    # TODO fix range attack later
    # if self.state != 10 and self.magazine_left > 0 and self.unit.fire_at_will == 0 and (self.arc_shot or self.frontline) and \
    #         self.charge_momentum == 1:  # Range attack when unit in melee state with arc_shot
    #     self.state = 11
    #     if self.unit.near_target != {} and (self.attack_target is None or self.attack_pos == 0):
    #         self.find_shooting_target(parent_state)
    # ^ End melee check

    # else:  # range attack
    #     if self in self.battle.combat_path_queue:
    #         self.battle.combat_path_queue.remove(self)
    #     self.attack_target = None
    #     self.combat_move_queue = []
    #
    #     # v Range attack function
    #     if parent_state == 11:  # Unit in range attack state
    #         self.state = 0  # Default state at idle
    #         if (self.magazine_left > 0 or self.ammo_now > 0) and self.attack_pos != 0 and \
    #                 self.shoot_range >= self.attack_pos.distance_to(self.base_pos):
    #             self.state = 11  # can shoot if troop have magazine_left and in shoot range, enter range combat state
    #
    #     elif self.magazine_left > 0 and self.unit.fire_at_will == 0 and \
    #             (self.state == 0 or (self.state not in (95, 96, 97, 98, 99) and
    #                                  parent_state in (1, 2, 3, 4, 5, 6) and self.shoot_move)):  # Fire at will
    #         if self.unit.near_target != {} and self.attack_target is None:
    #             self.find_shooting_target(parent_state)  # shoot the nearest target
    #
    # if self.state in (11, 12, 13) and self.magazine_left > 0 and self.ammo_now == 0:  # reloading magazine_left
    #     self.reload_time += dt
    #     if self.reload_time >= self.reload:
    #         self.ammo_now = self.magazine_size
    #         self.magazine_left -= 1
    #         self.reload_time = 0
    #     self.stamina = self.stamina - (dt * 2)  # use stamina while reloading
    # ^ End range attack function

    if combat_timer >= 0.5:  # combat is calculated every 0.5 second in self time
        if self.state == 10:  # if melee combat (engaging anyone on any side)
            collide_list = [subunit for subunit in self.enemy_front]
            for subunit in collide_list:
                angle_check = abs(self.angle - subunit.angle)  # calculate which side arrow hit the subunit
                if angle_check >= 135:  # front
                    hit_side = 0
                elif angle_check >= 45:  # side
                    hit_side = 1
                else:  # rear
                    hit_side = 2
                self.hit_register(subunit, 0, hit_side, self.battle.troop_data.status_list, combat_timer)
                self.stamina = self.stamina - (combat_timer * 5)

        elif self.state in (11, 12, 13):  # range combat
            if self.attack_target is not None:  # For fire at will
                if self.attack_target.state == 100:  # enemy dead
                    self.attack_pos = 0  # reset attack_pos to 0
                    self.attack_target = None  # reset attack_target to 0

                    for target, pos in self.unit.near_target.items():  # find other nearby base_target to shoot
                        self.attack_pos = pos
                        self.attack_target = target
                        break  # found new target, break loop
            elif self.attack_target is None:
                self.attack_target = self.unit.attack_target

            if self.ammo_now > 0 and ((self.attack_target is not None and self.attack_target.state != 100) or
                                      (self.attack_target is None and self.attack_pos != 0)) \
                    and (self.arc_shot or (self.arc_shot is False and self.unit.shoot_mode != 1)):
                # can shoot if reload finish and base_target existed and not dead. Non arc_shot cannot shoot if forbid
                # TODO add line of sight for range attack
                rangeattack.RangeAttack(self, self.base_pos.distance_to(self.attack_pos), self.shoot_range, self.zoom)  # Shoot
                self.ammo_now -= 1  # use 1 magazine_left in magazine
            elif self.attack_target is not None and self.attack_target.state == 100:  # if base_target destroyed when it about to shoot
                self.unit.range_combat_check = False
                self.unit.attack_target = 0  # reset range combat check and base_target

    return parent_state, collide_list


def die(self):
    self.image_original3.blit(self.health_image_list[5], self.health_image_rect)  # blit white hp bar
    self.block_original.blit(self.health_image_rect[5], self.health_block_rect)
    self.zoom_scale()
    self.last_health_state = 0
    self.skill_cooldown = {}  # remove all cooldown
    self.skill_effect = {}  # remove all skill effects

    self.block.blit(self.block_original, self.corner_image_rect)
    self.red_border = True  # to prevent red border appear when dead

    self.unit.dead_change = True

    if self in self.battle.battle_camera:
        self.battle.battle_camera.change_layer(sprite=self, new_layer=1)
    self.battle.alive_subunit_list.remove(self)
    self.unit.subunits.remove(self)

    self.command_action = ("Die", "uninterruptible")
    self.reset_animation()

    for subunit in self.unit.subunits_array.flat:  # remove from index array
        if subunit == self.game_id:
            self.unit.subunit_list = np.where(self.unit.subunit_list == self.game_id, 0, self.unit.subunit_list)
            break

    if self.unit_leader:  # leader dead, all subunit enter broken state
        for subunit in self.unit.subunits:
            subunit.state = 99  # Broken state

            corner_list = [[0, subunit.base_pos[1]], [1000, subunit.base_pos[1]], [subunit.base_pos[0], 0],
                           [subunit.base_pos[0], 1000]]
            which_corner = [subunit.base_pos.distance_to(corner_list[0]), subunit.base_pos.distance_to(corner_list[1]),
                            subunit.base_pos.distance_to(corner_list[2]),
                            subunit.base_pos.distance_to(corner_list[3])]  # find the closest map corner to run to
            found_corner = which_corner.index(min(which_corner))
            subunit.base_target = pygame.Vector2(corner_list[found_corner])
            subunit.command_target = subunit.base_target
            subunit.new_angle = subunit.set_rotate()

    self.battle.event_log.add_log([0, str(self.board_pos) + " " + str(self.name)
                                   + " in " + self.unit.leader[0].name
                                   + "'s unit is destroyed"], [3])  # add log to say this subunit is destroyed in subunit tab
