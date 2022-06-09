def leader_role_change(self, leader):
    """Change stat that related to army position such as in leader dead event"""
    leader.bad_morale = (20, 30)  # sub general morale lost for bad event
    if leader.role == 0:  # if leader become unit commander
        try:
            squad_penal = int(
                (leader.subunit_pos / len(leader.unit.subunit_id_array[
                                              0])) * 10)  # recalculate authority penalty based on subunit position
        except:
            squad_penal = 0
        leader.authority = leader.authority - (
                (leader.authority * squad_penal / 100) / 2)  # recalculate total authority
        leader.bad_morale = (30, 50)  # start_set general morale lost for bad event

        if leader.unit.commander:  # become army commander
            for this_unit in self.battle.all_team_unit[self.team]:
                this_unit.team_commander = leader
                this_unit.authority_recalculation()

