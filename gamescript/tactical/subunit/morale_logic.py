import random

import pygame

infinity = float("inf")


def morale_logic(self, dt, parent_state):
    """Morale check"""
    if self.morale > 1000:
        print(self.morale, self.base_morale, self.max_morale, self.original_morale, self.name)
    if self.max_morale != infinity:
        if self.base_morale < self.max_morale:
            if self.morale <= 10:  # Enter retreat state when morale reach 0
                if self.state not in (98, 99):
                    self.state = 98  # retreat state
                    max_random = 1 - (self.mental / 100)
                    if max_random < 0:
                        max_random = 0
                    self.morale_regen -= random.uniform(0, max_random)  # morale regen slower per broken state
                    if self.morale_regen < 0:  # begin checking broken state
                        self.state = 99  # Broken state
                        self.gone_leader_process("Broken")

                        corner_list = [[0, self.base_pos[1]], [1000, self.base_pos[1]], [self.base_pos[0], 0],
                                       [self.base_pos[0], 1000]]
                        which_corner = [self.base_pos.distance_to(corner_list[0]),
                                        self.base_pos.distance_to(corner_list[1]),
                                        self.base_pos.distance_to(corner_list[2]),
                                        self.base_pos.distance_to(
                                            corner_list[3])]  # find the closest map corner to run to
                        found_corner = which_corner.index(min(which_corner))
                        self.base_target = pygame.Vector2(corner_list[found_corner])
                        self.command_target = self.base_target
                        self.new_angle = self.set_rotate()

                    for subunit in self.unit.subunit_list:
                        subunit.base_morale -= (
                                15 * subunit.mental)  # reduce morale of other subunit, creating panic when seeing friend panic and may cause mass panic
                if self.morale < 0:
                    self.morale = 0  # morale cannot be lower than 0

            if self.state not in (95, 99) and parent_state not in (
            10, 99):  # If not missing start_set leader can replenish morale
                self.base_morale += (
                            dt * self.stamina_state_cal * self.morale_regen)  # Morale replenish based on stamina

            if self.base_morale < 0:  # morale cannot be negative
                self.base_morale = 0

        elif self.base_morale > self.max_morale:
            self.base_morale -= dt  # gradually reduce morale that exceed the starting max amount

        if self.state == 95:  # disobey state, morale gradually decrease until recover
            self.base_morale -= dt * self.mental

        elif self.state == 98:
            if parent_state not in (98, 99):
                self.subunit_health -= (
                            dt * 100)  # Unit begin to desert (die) if retreating but unit not retreat/broken
                if self.morale_state > 0.2:
                    self.state = 0  # Reset state to 0 when exit retreat state
