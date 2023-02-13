import numpy as np

from gamescript.common import utility
rotation_xy = utility.rotation_xy

formation_density_distance = {"Very Tight": 2, "Tight": 4,
                              "Very Loose": 15, "Loose": 8}


def setup_formation(self, phase=None, style=None, density=None, position=None):
    """
    Setup current formation based on the provided setting
    :param self: Subunit object (subunit leader in particularly)
    :param phase: New formation phase, None mean use current one
    :param style: New formation style, None mean use current one
    :param density: New formation density, None mean use current one
    :param position: New formation position from leader, None mean use current one
    """
    if phase is not None:
        self.formation_phase = phase
    if style is not None:
        self.formation_style = style
    if density is not None:
        self.formation_density = density
    if position is not None:
        self.formation_position = position

    first_placement = np.zeros((self.troop_follower_size,
                                self.troop_follower_size), dtype=int)  # for placement before consider style and phase

    placement_order = []  # list of formation position placement order
    place_list = list(set(self.formation_preset["original"].flat))
    place_list.sort(reverse=True)

    for placement_value in place_list:
        placement_position = np.where(self.formation_preset["original"] == placement_value)
        placement_order += [(placement_position[0][index], placement_position[1][index]) for index, _ in
                            enumerate(placement_position[0])]

    for _ in self.alive_troop_subordinate:
        for position in placement_order:
            if first_placement[position[0]][position[1]] == 0:  # replace empty position
                first_placement[position[0]][position[1]] = 1
                break

    first_placement = np.where(first_placement == 0, 99, first_placement)

    priority_subunit_place = {"center-front": [], "center-rear": [], "flank-front": [],
                              "flank-rear": [], "front": [], "rear": []}  # dict to keep placement priority score of subunit

    # For whatever reason, front and rear placement has to be in opposite of what intend, for example melee troop at the
    # front has to be assigned in "rear" instead
    for this_subunit in self.alive_troop_subordinate:
        if "Melee" in self.formation_phase:  # melee front
            if any(ext in this_subunit.troop_class for ext in ("Heavy", "Light")):  # melee at front
                formation_style_check(self, this_subunit, priority_subunit_place, "rear")
            else:  # range and other classes at rear
                formation_style_check(self, this_subunit, priority_subunit_place, "front")
        elif "Skirmish" in self.formation_phase:  # range front
            if "Range" in this_subunit.troop_class:  # range
                formation_style_check(self, this_subunit, priority_subunit_place, "rear")
            elif this_subunit.troop_class == "Artillery":  # artillery
                formation_style_check(self, this_subunit, priority_subunit_place, "rear")
            else:  # melee
                formation_style_check(self, this_subunit, priority_subunit_place, "front")
        elif "Bombard" in self.formation_phase:
            if this_subunit.troop_class == "Artillery":  # artillery
                formation_style_check(self, this_subunit, priority_subunit_place, "rear")
            elif "Range" in this_subunit.troop_class:  # range
                formation_style_check(self, this_subunit, priority_subunit_place, "rear")
            else:  # melee
                formation_style_check(self, this_subunit, priority_subunit_place, "front")

    formation_distance_list = np.zeros((self.troop_follower_size,
                                   self.troop_follower_size),
                                       dtype=object)  # for placement before consider style and phase

    priority_subunit_place = {key: value for key, value in priority_subunit_place.items() if len(value) > 0}
    for key, value in priority_subunit_place.items():  # there should be no excess number of subunit
        formation_sorted = []  # sorted from the highest
        formation_position = first_placement * self.formation_preset[key]
        for placement_value in tuple(sorted(set(formation_position.flat))):
            placement_position = np.where(formation_position == placement_value)
            formation_sorted += [(placement_position[0][index], placement_position[1][index]) for index, _ in
                                 enumerate(placement_position[0])]
        for this_subunit in value:
            for position in formation_sorted:
                if formation_distance_list[position[0]][position[1]] == 0:  # replace empty position
                    formation_distance_list[position[0]][position[1]] = this_subunit
                    break

    placement_density = formation_density_distance[self.formation_density]
    formation_distance_list = formation_distance_list[~np.all(formation_distance_list == 0, axis=1)]

    do_order = (list(range(len(formation_distance_list[0]))), list(range(len(formation_distance_list))))

    if self.formation_position == "Behind":
        start_distance = placement_density + self.default_sprite_size[1]
        distance = [0, start_distance]
        start = (int(len(formation_distance_list[0]) / 2), 0)  # start from center top of formation
        do_order[0].sort(key=lambda x: abs(start[0] - x))

    elif self.formation_position == "Ahead":
        start_distance = placement_density + self.default_sprite_size[1]
        start = (int(len(formation_distance_list[0]) / 2), len(formation_distance_list))  # start from center bottom of formation
        do_order[0].sort(key=lambda x: abs(start[0] - x))
        do_order[1].sort(reverse=True)
        distance = [0, -start_distance]

    elif self.formation_position == "Left":  # formation start from left of leader
        start_distance = placement_density + self.default_sprite_size[0]
        start = (len(formation_distance_list[0]) - 1, 0)  # start from right end of formation
        do_order[0].sort(reverse=True)
        distance = [-start_distance, 0]

    elif self.formation_position == "Right":  # formation start from right of leader
        start_distance = placement_density + self.default_sprite_size[0]
        start = (0, 0)
        distance = [start_distance, 0]

    elif self.formation_position == "Around":
        start = (int(len(formation_distance_list[0]) / 2), int(len(formation_distance_list) / 2))
        do_order[0].sort(key=lambda x: abs(start[0] - x))
        do_order[1].sort(key=lambda x: abs(start[1] - x))
        distance = [0, 0]

    start_distance = tuple(distance)
    for row_index, row in enumerate(do_order[1]):  # row (y)
        for col_index, col in enumerate(do_order[0]):  # column (x) in row
            if formation_distance_list[row][col] != 0:
                sprite_size = formation_distance_list[row][col].default_sprite_size
                self.formation_distance_list[formation_distance_list[row][col]] = tuple(distance)
                self.formation_pos_list[formation_distance_list[row][col]] = \
                    rotation_xy(self.base_pos, self.base_pos + distance,
                                self.radians_angle)

                if self.follow_order != "Stay Here":  # reset follow target
                    formation_distance_list[row][col].follow_target = self.formation_pos_list[formation_distance_list[row][col]]

                if col_index + 1 < len(do_order[0]):  # still more to do in this row
                    if do_order[0][col_index + 1] < col:  # left from current, such as 1 to 0, then get the right of next (1)
                        next_subunit = formation_distance_list[row][do_order[0][col_index + 1] + 1]
                        if next_subunit != 0:
                            distance[0] = self.formation_distance_list[next_subunit][0] - \
                                     (placement_density + sprite_size[0])
                        else:
                            distance[0] -= placement_density * 2
                    else:  # right from current, such as 0 to 2, then get the left of next (1)
                        next_subunit = formation_distance_list[row][do_order[0][col_index + 1] - 1]
                        if next_subunit != 0:
                            distance[0] = self.formation_distance_list[next_subunit][0] + \
                                     (placement_density + sprite_size[0])
                        else:
                            distance[0] += placement_density * 2
            else:  # empty position
                sprite_size = (0, 0)
                if col_index + 1 < len(do_order[0]):  # still more to do in this row
                    if do_order[0][col_index + 1] < col:  # left from current, such as 1 to 0, then get the right of next (1)
                        next_subunit = formation_distance_list[row][do_order[0][col_index + 1] + 1]
                        if next_subunit != 0:
                            distance[0] = self.formation_distance_list[next_subunit][0] - \
                                     (placement_density + sprite_size[0])
                        else:
                            distance[0] -= placement_density * 2
                    else:  # right from current, such as 0 to 2, then get the left of next (1)
                        next_subunit = formation_distance_list[row][do_order[0][col_index + 1] - 1]
                        if next_subunit != 0:
                            distance[0] = self.formation_distance_list[next_subunit][0] + \
                                     (placement_density + sprite_size[0])
                        else:
                            distance[0] += placement_density * 2

        distance[0] = start_distance[0]  # end of row, reset starting point x
        if row_index + 1 < len(do_order[1]):
            if do_order[1][row_index + 1] > row:  # next row
                biggest_height = 0
                for col in formation_distance_list[do_order[1][row_index + 1] - 1]:  # get biggest height in row before next one
                    if col != 0 and col.default_sprite_size[1] > biggest_height:
                        biggest_height = col.default_sprite_size[1]
                distance[1] += (placement_density + biggest_height)
            else:  # previous row
                biggest_height = 0
                for col in formation_distance_list[do_order[1][row_index + 1] + 1]:  # get biggest height in row after next one
                    if col != 0 and col.default_sprite_size[1] > biggest_height:
                        biggest_height = col.default_sprite_size[1]
                distance[1] -= (placement_density + biggest_height)


def formation_style_check(self, this_subunit, priority_subunit_place, side):
    if self.formation_consider_flank:
        if "Infantry" in self.formation_style:  # Infantry at flank
            if this_subunit.subunit_type < 2:  # infantry
                priority_subunit_place["flank-" + side].append(this_subunit)
            elif this_subunit.subunit_type == 2:  # cavalry
                priority_subunit_place["center-" + side].append(this_subunit)
        elif "Cavalry" in self.formation_style:  # Cavalry at flank
            if this_subunit.subunit_type < 2:  # infantry
                priority_subunit_place["center-" + side].append(this_subunit)
            elif this_subunit.subunit_type == 2:  # cavalry
                priority_subunit_place["flank-" + side].append(this_subunit)
    else:  # no need to consider flank and center since has either only infantry or cavalry troops, not both types
        priority_subunit_place[side].append(this_subunit)
