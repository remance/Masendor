equip_header = ("Primary", "Secondary")


def swap_weapon_command(self, choice):
    if "Troop" in choice:
        for this_subunit in self.alive_subunit_list:
            if this_subunit.leader is None and this_subunit.state < 90:  # skip leader
                if "Melee" in choice:
                    if len(this_subunit.melee_weapon_set) > 0:
                        this_subunit.equipped_weapon = this_subunit.melee_weapon_set[0]
                        this_subunit.swap_weapon()
                elif "Range" in choice:
                    if len(this_subunit.range_weapon_set) > 0:
                        for this_set in this_subunit.range_weapon_set:
                            if this_subunit.magazine_count[this_set][0] > 0 or this_subunit.magazine_count[this_set][1] > 1:  # check if set has any ammo
                                this_subunit.equipped_weapon = this_set
                                this_subunit.swap_weapon()
                                break
                else:
                    for index, value in enumerate(equip_header):
                        if value in choice:
                            this_subunit.equipped_weapon = index
                            this_subunit.swap_weapon()
                            break
    else:  # change only leader equipment
        for index, value in enumerate(equip_header):
            if value in choice:
                self.leader[0].subunit.equipped_weapon = index
                self.leader[0].subunit.swap_weapon()
                break
