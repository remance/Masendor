def change_formation(self, formation):
    """
    Change current unit formation to the new one
    :param self: Unit object
    :param formation: Name of new formation
    """
    if formation == "original":
        self.subunit_id_array = self.original_subunit_id_array.copy()
    else:
        new_formation = self.unit_formation_list[formation]
        center = (round(len(self.unit_formation_list[formation][0]) / 2, 0),
                  round(len(self.unit_formation_list[formation]) / 2, 0))
        temp_subunit_object_array = self.subunit_object_array.flat()
        for this_subunit in temp_subunit_object_array:
            if this_subunit.subunit_type == "melee":
                temp_subunit_object_array.remove(this_subunit)
                break
        self.subunit_id_array = new_formation
    self.subunit_formation_change()
