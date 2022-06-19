def change_formation(self, formation):
    """
    Change current unit formation to the new one
    :param self: Unit object
    :param formation: Name of new formation
    """
    if formation == "original":
        self.subunit_id_array = self.original_subunit_id_array.copy()
    else:
        new_formation = self.formation_list[formation]
        self.subunit_id_array = new_formation
    self.subunit_formation_change()
