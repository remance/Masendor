import numpy as np

from gamescript.common import utility
rotation_xy = utility.rotation_xy

formation_density_distance = {"Very Tight": 2, "Tight": 4,
                              "Very Loose": 15, "Loose": 8}

unit_density_distance = {"Very Tight": 20, "Tight": 40, "Very Loose": 100, "Loose": 70}


def setup_formation(self, which, phase=None, style=None, density=None, position=None):
    """
    Setup current formation based on the provided setting
    :param self: Subunit object (subunit leader in particularly)
    :param which: which type of formation to setup, troop or unit
    :param phase: New formation phase, None mean use current one
    :param style: New formation style, None mean use current one
    :param density: New formation density, None mean use current one
    :param position: New formation position from leader, None mean use current one
    """
    if which == "troop":
        if phase:
            self.troop_formation_phase = phase
            if self.unit_follow_order != "Free":  # leader follower also change troop formation setting to match higher leader when not in free order
                for leader in self.alive_leader_follower:
                    if not leader.player_control:
                        leader.setup_formation("troop", phase=phase)
        if style:
            self.troop_formation_style = style
            if self.unit_follow_order != "Free":
                for leader in self.alive_leader_follower:
                    if not leader.player_control:
                        leader.setup_formation("troop", style=style)
        if density:
            self.troop_formation_density = density
            if self.unit_follow_order != "Free":
                for leader in self.alive_leader_follower:
                    if not leader.player_control:
                        leader.setup_formation("troop", density=density)
        if position:
            self.troop_formation_position = position
            if self.unit_follow_order != "Free":
                for leader in self.alive_leader_follower:
                    if not leader.player_control:
                        leader.setup_formation("troop", position=position)

        follower_size = self.troop_follower_size
        formation_phase = self.troop_formation_phase
        formation_style = self.troop_formation_style
        formation_density = self.troop_formation_density
        formation_position = self.troop_formation_position
        formation_distance_list = self.troop_distance_list
        formation_pos_list = self.troop_pos_list
        follow_order = self.troop_follow_order
        follower_list = self.alive_troop_follower
        placement_density = formation_density_distance[formation_density]
        formation_preset = self.troop_formation_preset

    elif which == "unit":
        if phase:
            self.unit_formation_phase = phase

        if style:
            self.unit_formation_style = style

        if density:
            self.unit_formation_density = density

        if position:
            self.unit_formation_position = position

        follower_size = self.leader_follower_size
        formation_phase = self.unit_formation_phase
        formation_style = self.unit_formation_style
        formation_density = self.unit_formation_density
        formation_position = self.unit_formation_position
        formation_distance_list = self.unit_distance_list
        formation_pos_list = self.unit_pos_list
        follow_order = self.unit_follow_order
        follower_list = self.alive_leader_follower
        placement_density = unit_density_distance[formation_density]
        formation_preset = self.unit_formation_preset

    if follower_size > 0:
        first_placement = np.zeros((follower_size,
                                    follower_size), dtype=int)  # for placement before consider style and phase

        placement_order = []  # list of formation position placement order
        place_list = list(set(formation_preset["original"].flat))
        place_list.sort(reverse=True)

        for placement_value in place_list:
            placement_position = np.where(formation_preset["original"] == placement_value)
            placement_order += [(placement_position[0][index], placement_position[1][index]) for index, _ in
                                enumerate(placement_position[0])]

        for _ in follower_list:
            for position in placement_order:
                if first_placement[position[0]][position[1]] == 0:  # replace empty position
                    first_placement[position[0]][position[1]] = 1
                    break

        first_placement = np.where(first_placement == 0, 99, first_placement)

        priority_place = {"center-front": [], "center-rear": [], "flank-front": [],
                                  "flank-rear": [], "front": [], "rear": []}  # dict to keep placement priority score of subunit

        # For whatever reason, front and rear placement has to be in opposite of what intend, for example melee troop at the
        # front has to be assigned in "rear" instead
        for who in follower_list:
            if "Melee" in formation_phase:  # melee front
                if (which == "troop" and any(ext in who.troop_class for ext in ("Heavy", "Light"))) or \
                        (which == "unit" and "melee" in who.unit_type):  # melee at front
                    formation_style_check(self, who, which, formation_style, priority_place, "rear")
                else:  # range and other classes at rear
                    formation_style_check(self, who, which, formation_style, priority_place, "front")
            elif "Skirmish" in formation_phase:  # range front
                if (which == "troop" and "Range" in who.troop_class) or (which == "unit" and "range" in who.unit_type):  # range
                    formation_style_check(self, who, which, formation_style, priority_place, "rear")
                elif (which == "troop" and who.troop_class == "Artillery") or (which == "unit" and who.unit_type == "artillery"):  # artillery
                    formation_style_check(self, who, which, formation_style, priority_place, "rear")
                else:  # melee
                    formation_style_check(self, who, which, formation_style, priority_place, "front")
            elif "Bombard" in formation_phase:
                if (which == "troop" and who.troop_class == "Artillery") or (which == "unit" and who.unit_type == "artillery"):  # artillery
                    formation_style_check(self, who, which, formation_style, priority_place, "rear")
                elif (which == "troop" and "Range" in who.troop_class) or (which == "unit" and "range" in who.unit_type):  # range
                    formation_style_check(self, who, which, formation_style, priority_place, "rear")
                else:  # melee
                    formation_style_check(self, who, which, formation_style, priority_place, "front")

        temp_formation_distance_list = np.zeros((follower_size, follower_size),
                                                dtype=object)  # for placement before consider style and phase

        priority_place = {key: value for key, value in priority_place.items() if len(value) > 0}
        for key, value in priority_place.items():  # there should be no excess number of subunit
            formation_sorted = []  # sorted from the highest
            formation_position_list = first_placement * formation_preset[key]
            for placement_value in tuple(sorted(set(formation_position_list.flat))):
                placement_position = np.where(formation_position_list == placement_value)
                formation_sorted += [(placement_position[0][index], placement_position[1][index]) for index, _ in
                                     enumerate(placement_position[0])]
            for who in value:
                for position in formation_sorted:
                    if temp_formation_distance_list[position[0]][position[1]] == 0:  # replace empty position
                        temp_formation_distance_list[position[0]][position[1]] = who
                        break

        temp_formation_distance_list = temp_formation_distance_list[~np.all(temp_formation_distance_list == 0, axis=1)]

        do_order = (list(range(len(temp_formation_distance_list[0]))), list(range(len(temp_formation_distance_list))))

        if formation_position == "Behind":
            start_distance = placement_density + self.troop_size
            distance = [0, start_distance]
            start = (int(len(temp_formation_distance_list[0]) / 2), 0)  # start from center top of formation
            do_order[0].sort(key=lambda x: abs(start[0] - x))

        elif formation_position == "Ahead":
            start_distance = placement_density + self.troop_size
            start = (int(len(temp_formation_distance_list[0]) / 2), len(temp_formation_distance_list))  # start from center bottom of formation
            do_order[0].sort(key=lambda x: abs(start[0] - x))
            do_order[1].sort(reverse=True)
            distance = [0, -start_distance]

        elif formation_position == "Left":  # formation start from left of leader
            start_distance = placement_density + self.troop_size
            start = (len(temp_formation_distance_list[0]) - 1, 0)  # start from right end of formation
            do_order[0].sort(reverse=True)
            distance = [-start_distance, 0]

        elif formation_position == "Right":  # formation start from right of leader
            start_distance = placement_density + self.troop_size
            start = (0, 0)
            distance = [start_distance, 0]

        elif formation_position == "Around":
            start = (int(len(temp_formation_distance_list[0]) / 2), int(len(temp_formation_distance_list) / 2))
            do_order[0].sort(key=lambda x: abs(start[0] - x))
            do_order[1].sort(key=lambda x: abs(start[1] - x))
            distance = [0, 0]

        start_do_order_row = do_order[1][0]
        start_distance = tuple(distance)
        for row_index, row in enumerate(do_order[1]):  # row (y)
            for col_index, col in enumerate(do_order[0]):  # column (x) in row
                if temp_formation_distance_list[row][col] != 0:
                    sprite_size = temp_formation_distance_list[row][col].troop_size
                    formation_distance_list[temp_formation_distance_list[row][col]] = tuple(distance)
                    formation_pos_list[temp_formation_distance_list[row][col]] = \
                        rotation_xy(self.base_pos, self.base_pos + distance,
                                    self.radians_angle)

                    if follow_order != "Stay Here":  # reset follow target
                        temp_formation_distance_list[row][col].follow_target = formation_pos_list[temp_formation_distance_list[row][col]]

                    if col_index + 1 < len(do_order[0]):  # still more to do in this row
                        if do_order[0][col_index + 1] < col:  # left from current, such as 1 to 0, then get the right of next (1)
                            next_who = temp_formation_distance_list[row][do_order[0][col_index + 1] + 1]
                            if next_who != 0:
                                distance[0] = formation_distance_list[next_who][0] - \
                                         (placement_density + sprite_size)
                            else:
                                distance[0] -= placement_density * 2
                        else:  # right from current, such as 0 to 2, then get the left of next (1)
                            next_who = temp_formation_distance_list[row][do_order[0][col_index + 1] - 1]
                            if next_who != 0:
                                distance[0] = formation_distance_list[next_who][0] + \
                                         (placement_density + sprite_size)
                            else:
                                distance[0] += placement_density * 2
                else:  # empty position
                    sprite_size = 0
                    if col_index + 1 < len(do_order[0]):  # still more to do in this row
                        if do_order[0][col_index + 1] < col:  # left from current, such as 1 to 0, then get the right of next (1)
                            next_who = temp_formation_distance_list[row][do_order[0][col_index + 1] + 1]
                            if next_who != 0:
                                distance[0] = formation_distance_list[next_who][0] - \
                                         (placement_density + sprite_size)
                            else:
                                distance[0] -= placement_density * 2
                        else:  # right from current, such as 0 to 2, then get the left of next (1)
                            next_who = temp_formation_distance_list[row][do_order[0][col_index + 1] - 1]
                            if next_who != 0:
                                distance[0] = formation_distance_list[next_who][0] + \
                                         (placement_density + sprite_size)
                            else:
                                distance[0] += placement_density * 2

            distance[0] = start_distance[0]  # end of row, reset starting point x
            if row_index + 1 < len(do_order[1]):
                distance[1] = start_distance[1]
                biggest_height = 0
                if do_order[1][row_index + 1] > row:  # next row
                    for col in temp_formation_distance_list[do_order[1][row_index + 1] - 1]:  # get biggest height in row before next one
                        if col != 0 and col.troop_size > biggest_height:
                            biggest_height = col.troop_size
                else:  # previous row
                    for col in temp_formation_distance_list[do_order[1][row_index + 1] + 1]:  # get biggest height in row after next one
                        if col != 0 and col.troop_size > biggest_height:
                            biggest_height = col.troop_size

                distance[1] += ((placement_density + biggest_height) *
                                (do_order[1][row_index + 1] - start_do_order_row))


def formation_style_check(self, who, formation_type, formation_style, priority_subunit_place, side):
    if (formation_type == "troop" and self.formation_consider_flank) or \
            (formation_type == "unit" and self.unit_consider_flank):
        if "Infantry" in formation_style:  # Infantry at flank
            if formation_type == "troop":
                if who.subunit_type < 2:  # infantry
                    priority_subunit_place["flank-" + side].append(who)
                elif who.subunit_type == 2:  # cavalry
                    priority_subunit_place["center-" + side].append(who)
            elif formation_type == "unit":
                if "inf" in who.unit_type:  # infantry
                    priority_subunit_place["flank-" + side].append(who)
                elif "cav" in who.unit_type:  # cavalry
                    priority_subunit_place["center-" + side].append(who)
        elif "Cavalry" in formation_style:  # Cavalry at flank
            if formation_type == "troop":
                if who.subunit_type < 2:  # infantry
                    priority_subunit_place["center-" + side].append(who)
                elif who.subunit_type == 2:  # cavalry
                    priority_subunit_place["flank-" + side].append(who)
            elif formation_type == "unit":
                if "inf" in who.unit_type:  # infantry
                    priority_subunit_place["center-" + side].append(who)
                elif "cav" in who.unit_type:  # cavalry
                    priority_subunit_place["flank-" + side].append(who)
    else:  # no need to consider flank and center since has either only infantry or cavalry troops, not both types
        priority_subunit_place[side].append(who)
