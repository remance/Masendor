def gone_leader_process(self, *args):
    """All subunit enter broken state when leader gone in arcade mode"""
    if self.unit_leader:  # leader dead, all subunit enter broken state
        self.unit.state = 99
        for subunit in self.unit.alive_subunit_list:
            subunit.state = 99  # Broken state
            subunit.broken = True
            subunit.retreat_start = True
