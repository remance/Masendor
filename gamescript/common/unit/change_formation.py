import numpy as np

dynamic_setting = ()


def change_formation(self, formation, dynamic=False):
    """
    Change current unit formation to the new one
    :param self: Unit object
    :param formation: Name of new formation
    :param dynamic: Include phase and style in formation change
    """
    if formation == "original" and dynamic is False:  # change formation to exact original
        self.subunit_id_array = self.original_subunit_id_array.copy()
    else:
        if formation == "Original":  # original formation but change placement
            new_formation = self.original_formation_score
        else:
            new_formation = self.unit_formation_list[formation]

        self.subunit_id_array = np.where(self.subunit_id_array > 0, 0, self.subunit_id_array)  # change all to empty
        temp_subunit_object_array = self.subunit_object_array.flat

        placement_order = []  # list of formation position placement order
        for placement_value in tuple(set(new_formation.tolist())):
            placement_position = np.where(new_formation == placement_value)
            placement_order += [(placement_position[0][index], placement_position[1][index]) for index, _ in enumerate(placement_position[0])]

        priority_subunit_score = {"front": [], "rear": [], "flank": [], "outer": [], "inner": []}  # dict to keep placement priority score of subunit
        for this_subunit in temp_subunit_object_array:
            if this_subunit is not None:
                # Formation style score, closer to front mean higher score
                if "Inner" in self.formation_style:
                    if this_subunit.subunit_type < 2 and "Infantry" in self.formation_style:
                        score += 2
                    elif this_subunit.subunit_type >= 2 and "Cavalry" in self.formation_style:
                        score += 2
                elif "Flank" in self.formation_style:
                    if this_subunit.subunit_type >= 2 and "Infantry" in self.formation_style:
                        score += 1
                    elif this_subunit.subunit_type < 2 and "Cavalry" in self.formation_style:
                        score += 1

                # Formation phase score
                if "Melee" in self.formation_phase:
                    if this_subunit.subunit_type in (0, 2):
                        score += 2
                elif "Skirmish" in self.formation_phase:
                    if this_subunit.subunit_type in (1, 3):
                        score += 2
                    elif this_subunit.subunit_type == 4:
                        score += 1
                elif "Bombard" in self.formation_phase:
                    if this_subunit.subunit_type in (1, 3):
                        score += 1
                    elif this_subunit.subunit_type == 4:
                        score += 2
                elif "Heroic" in self.formation_phase:
                    if this_subunit.subunit_type in (0, 2):
                        score += 1
                    elif this_subunit.leader is not None:
                        score += 2
                priority_subunit_score[this_subunit] = score + score
        priority_subunit_score = sorted(priority_subunit_score.items(), key=lambda x: x[1])

        print(self.formation_style, self.formation_phase)
        print(placement_order)
        print(priority_subunit_score)
        placement_count = 0
        while placement_count < len(temp_subunit_object_array):  # there should be no excess number of subunit
            for position in enumerate(placement_order):
                placement_scoring = (position[0], position[1])
                for this_subunit, score in priority_subunit_score.items():
                    if this_subunit.state != 100:
                        self.subunit_id_array[position[0]][position[1]] = this_subunit.game_id
                        temp_subunit_object_array.remove(this_subunit)
                        priority_subunit_score.remove(this_subunit)
                        placement_count += 1
                        break

    self.subunit_formation_change()
