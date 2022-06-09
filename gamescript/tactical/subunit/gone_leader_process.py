import random


def gone_leader_process(self, event):
    """Leader change when subunit or gone/destroyed, event can be "Destroyed" or "Broken" """
    check_state = [100]
    if event == "Broken":
        check_state = [99, 100]
    if self.leader is not None and self.leader.state != 100:  # Find new subunit for leader if there is one in this subunit
        for this_subunit in self.nearby_subunit_list:
            if this_subunit != 0 and this_subunit.state not in check_state and this_subunit.leader is None:
                this_subunit.leader = self.leader
                self.leader.subunit = this_subunit
                for index, subunit2 in enumerate(self.unit.subunit_list):  # loop to find new subunit pos based on new subunit_sprite list
                    if subunit2 == self.leader.subunit:
                        self.leader.subunit_pos = index
                        if self.unit_leader:  # set leader subunit to new one
                            self.unit.leader_subunit = subunit2
                            subunit2.unit_leader = True
                            self.unit_leader = False
                        break

                self.leader = None
                break

        if self.leader is not None:  # if can't find near subunit to move leader then find from first subunit to last place in unit
            for index, this_subunit in enumerate(self.unit.subunit_list):
                if this_subunit.state not in check_state and this_subunit.leader is None:
                    this_subunit.leader = self.leader
                    self.leader.subunit = this_subunit
                    this_subunit.leader.subunit_pos = index
                    self.leader = None
                    if self.unit_leader:  # set leader subunit to new one
                        self.unit.leader_subunit = this_subunit
                        this_subunit.unit_leader = True

                    break

            if self.leader is not None and event == "Destroyed":  # Still can't find new subunit so leader disappear with chance of different result
                self.leader.state = random.randint(97, 100)  # captured, retreated, wounded, dead
                self.leader.health = 0
                self.leader.gone()

        self.unit_leader = False
