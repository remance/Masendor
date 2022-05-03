import random
import pygame

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

rotation_list = (90, 120, 45, 0, -90, -45, -120, 180, -180)
rotation_name = ("l_side", "l_sidedown", "l_sideup", "front", "r_side", "r_sideup", "r_sidedown", "back", "back")
rotation_dict = {key: rotation_name[index] for index, key in enumerate(rotation_list)}


def rotate(self):
    """rotate sprite image may use when subunit can change direction independently of unit, this is not use
    for animation sprite"""
    if self.zoom != self.max_zoom:
        self.image = pygame.transform.rotate(self.inspect_image_original, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
    if self.unit.selected and self.state != 100:
        self.selected_inspect_image = pygame.transform.rotate(self.selected_inspect_image_original, self.angle)
        self.image.blit(self.selected_inspect_image, self.selected_inspect_image_rect)


def combat_pathfind(self):
    # v Pathfinding
    self.combat_move_queue = []
    move_array = self.battle.subunit_pos_array.copy()
    int_base_target = (int(self.close_target.base_pos[0]), int(self.close_target.base_pos[1]))
    for y in self.close_target.pos_range[0]:
        for x in self.close_target.pos_range[1]:
            move_array[x][y] = 100  # reset path in the enemy sprite position

    int_base_pos = (int(self.base_pos[0]), int(self.base_pos[1]))
    for y in self.pos_range[0]:
        for x in self.pos_range[1]:
            move_array[x][y] = 100  # reset path for subunit sprite position

    start_point = (min([max(0, int_base_pos[0] - 5), max(0, int_base_target[0] - 5)]),  # start point of new smaller array
                   min([max(0, int_base_pos[1] - 5), max(0, int_base_target[1] - 5)]))
    end_point = (max([min(999, int_base_pos[0] + 5), min(999, int_base_target[0] + 5)]),  # end point of new array
                 max([min(999, int_base_pos[1] + 5), min(999, int_base_target[1] + 5)]))

    move_array = move_array[start_point[1]:end_point[1]]  # cut 1000x1000 array into smaller one by row
    move_array = [this_array[start_point[0]:end_point[0]] for this_array in move_array]  # cut by column

    # if len(move_array) < 100 and len(move_array[0]) < 100: # if too big then skip combat pathfinding
    grid = Grid(matrix=move_array)
    grid.cleanup()

    start = grid.node(int_base_pos[0] - start_point[0], int_base_pos[1] - start_point[1])  # start point
    end = grid.node(int_base_target[0] - start_point[0], int_base_target[1] - start_point[1])  # end point

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)
    path = [(this_path[0] + start_point[0], this_path[1] + start_point[1]) for this_path in path]  # remake pos into actual map pos

    path = path[4:]  # remove some starting path that may clip with friendly subunit sprite

    self.combat_move_queue = path  # add path into combat movement queue
    if len(self.combat_move_queue) < 1:  # simply try walk to target anyway if pathfinder return empty
        self.combat_move_queue = [self.close_target.base_pos]


def find_close_target(self, subunit_list):
    """Find close enemy subunit to move to fight"""
    close_list = {subunit: subunit.base_pos.distance_to(self.base_pos) for subunit in subunit_list}
    close_list = dict(sorted(close_list.items(), key=lambda item: item[1]))
    max_random = 3
    if len(close_list) < 4:
        max_random = len(close_list) - 1
        if max_random < 0:
            max_random = 0
    close_target = None
    if len(close_list) > 0:
        close_target = list(close_list.keys())[random.randint(0, max_random)]
        # if close_target.base_pos.distance_to(self.base_pos) < 20: # in case can't find close target
    return close_target
