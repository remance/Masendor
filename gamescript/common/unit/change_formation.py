import numpy as np

dynamic_setting = ()


def change_formation(self, formation=None, phase=None, style=None):
    """
    Change current unit formation to the new one
    :param self: Unit object
    :param formation: Name of new formation, None mean use current one
    :param phase: New formation phase, None mean use current one
    :param style: New formation style, None mean use current one
    """
    if formation == "true original":  # change formation to exact original
        self.subunit_id_array = self.original_subunit_id_array.copy()
    else:
        if formation is not None:
            self.formation = formation
        if phase is not None:
            self.formation_phase = phase
        if style is not None:
            self.formation_style = style

        if self.formation == "Original":  # original formation but change placement
            new_formation = self.original_formation.copy()
        else:
            new_formation = self.unit_formation_list[self.formation].copy()
            if self.formation == "Cluster":
                new_formation = {key: value * np.random.randint(10, size=self.unit_size) for key, value in
                                 new_formation.items()}  # make cluster formation

        self.subunit_id_array = np.zeros(self.unit_size, dtype=int)  # change all to empty
        first_placement = np.zeros(self.unit_size, dtype=int)  # for placement before consider style and phase

        placement_order = []  # list of formation position placement order
        for placement_value in tuple(set(new_formation["original"].flat)):
            placement_position = np.where(new_formation["original"] == placement_value)
            placement_order += [(placement_position[0][index], placement_position[1][index]) for index, _ in enumerate(placement_position[0])]

        for this_subunit in self.alive_subunit_list:
            if this_subunit is not None:
                for position in placement_order:
                    if first_placement[position[0]][position[1]] == 0:  # replace empty position
                        first_placement[position[0]][position[1]] = 1
                        break

        first_placement = np.where(first_placement == 0, 99, first_placement)

        priority_subunit_place = {"center-front": [], "center-rear": [], "flank-front": [],
                                  "flank-rear": [], "inner-front": [], "inner-rear": [],
                                  "outer-front": [], "outer-rear": []}  # dict to keep placement priority score of subunit
        for this_subunit in self.alive_subunit_list:
            if "Melee" in self.formation_phase:  # melee front
                if this_subunit.subunit_type in (0, 2):  # melee
                    formation_style_check(self, this_subunit, priority_subunit_place, "front")
                else:  # range
                    formation_style_check(self, this_subunit, priority_subunit_place, "rear")
            elif "Skirmish" in self.formation_phase:  # range front
                if this_subunit.subunit_type in (1, 3):  # range
                    formation_style_check(self, this_subunit, priority_subunit_place, "front")
                elif this_subunit.subunit_type == 4:  # artillery
                    formation_style_check(self, this_subunit, priority_subunit_place, "front")
                else:  # melee
                    formation_style_check(self, this_subunit, priority_subunit_place, "rear")
            elif "Bombard" in self.formation_phase:
                if this_subunit.subunit_type == 4:  # artillery
                    formation_style_check(self, this_subunit, priority_subunit_place, "front")
                elif this_subunit.subunit_type in (1, 3):  # range
                    formation_style_check(self, this_subunit, priority_subunit_place, "front")
                else:  # melee
                    formation_style_check(self, this_subunit, priority_subunit_place, "rear")
            elif "Heroic" in self.formation_phase:
                if this_subunit.leader is not None:  # leader
                    formation_style_check(self, this_subunit, priority_subunit_place, "front")
                elif this_subunit.subunit_type in (0, 2):  # melee
                    formation_style_check(self, this_subunit, priority_subunit_place, "front")
                else:  # range
                    formation_style_check(self, this_subunit, priority_subunit_place, "rear")

        priority_subunit_place = {key: value for key, value in priority_subunit_place.items() if len(value) > 0}
        for key, value in priority_subunit_place.items():  # there should be no excess number of subunit
            formation_sorted = []  # sorted from the lowest score to highest
            formation_position = first_placement * new_formation[key]
            for placement_value in tuple(sorted(set(formation_position.flat))):
                placement_position = np.where(formation_position == placement_value)
                formation_sorted += [(placement_position[0][index], placement_position[1][index]) for index, _ in
                                     enumerate(placement_position[0])]

            for this_subunit in value:
                for position in formation_sorted:
                    if self.subunit_id_array[position[0]][position[1]] == 0:  # replace empty position
                        self.subunit_id_array[position[0]][position[1]] = this_subunit.game_id
                        break

    self.subunit_formation_change()


def formation_style_check(self, this_subunit, priority_subunit_place, side):
    if "Inner" in self.formation_style:
        if "Infantry" in self.formation_style:
            if this_subunit.subunit_type < 2:  # infantry
                priority_subunit_place["inner-" + side].append(this_subunit)
            elif this_subunit.subunit_type >= 2:  # cavalry
                priority_subunit_place["outer-" + side].append(this_subunit)
        elif "Cavalry" in self.formation_style:
            if this_subunit.subunit_type < 2:  # infantry
                priority_subunit_place["outer-" + side].append(this_subunit)
            elif this_subunit.subunit_type >= 2:  # cavalry
                priority_subunit_place["inner-" + side].append(this_subunit)
    elif "Flank" in self.formation_style:
        if "Infantry" in self.formation_style:
            if this_subunit.subunit_type < 2:  # infantry
                priority_subunit_place["flank-" + side].append(this_subunit)
            elif this_subunit.subunit_type >= 2:  # cavalry
                priority_subunit_place["center-" + side].append(this_subunit)
        elif "Cavalry" in self.formation_style:
            if this_subunit.subunit_type < 2:  # infantry
                priority_subunit_place["center-" + side].append(this_subunit)
            elif this_subunit.subunit_type >= 2:  # cavalry
                priority_subunit_place["flank-" + side].append(this_subunit)