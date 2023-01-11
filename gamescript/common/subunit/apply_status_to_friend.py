def apply_status_to_friend(self, aoe, status_id):
    """apply status effect to nearby subunit depending on aoe stat"""
    if 1 < aoe < 4:
        for subunit in self.nearby_subunit_list[0:4]:
            if subunit is not None and subunit.state != 100:  # only apply to exist and alive squads
                subunit.apply_effect(status_id, subunit.status_list, subunit.status_effect, subunit.status_duration)
        if aoe > 2:  # all nearby including corner friendly subunit
            for subunit in self.nearby_subunit_list[4:]:
                if subunit is not None and subunit.state != 100:  # only apply to exist and alive squads
                    subunit.apply_effect(status_id, subunit.status_list, subunit.status_effect, subunit.status_duration)
    elif aoe == 4:  # apply to whole unit
        for subunit in self.unit.alive_subunit_list:
            if subunit.state != 100:  # only apply to alive squads
                subunit.apply_effect(status_id, subunit.status_list, subunit.status_effect, subunit.status_duration)
