def apply_status_to_friend(self, aoe, status_id, status_stat):
    """apply status effect to nearby subunit depending on aoe stat"""
    if aoe in (2, 3):
        if aoe > 1:  # only direct nearby friendly subunit
            for subunit in self.nearby_subunit_list[0:4]:
                if subunit != 0 and subunit.state != 100:  # only apply to exist and alive squads
                    subunit.status_effect[status_id] = status_stat  # apply status effect
        if aoe > 2:  # all nearby including corner friendly subunit
            for subunit in self.nearby_subunit_list[4:]:
                if subunit != 0 and subunit.state != 100:  # only apply to exist and alive squads
                    subunit.status_effect[status_id] = status_stat  # apply status effect
    elif aoe == 4:  # apply to whole unit
        for subunit in self.unit.alive_subunit_list:
            if subunit.state != 100:  # only apply to alive squads
                subunit.status_effect[status_id] = status_stat  # apply status effect
