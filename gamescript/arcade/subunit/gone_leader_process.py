import pygame


def gone_leader_process(self, *args):
    """All subunit enter broken state when leader gone in arcade mode"""
    if self.unit_leader:  # leader dead, all subunit enter broken state
        self.unit.state = 99
        for subunit in self.unit.subunit_list:
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
    if self.unit.control:
        self.battle.camera_mode = "Free"  # camera become free when player char die so can look over the battle

