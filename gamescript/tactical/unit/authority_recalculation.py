def authority_recalculation(self):
    """recalculate authority from all alive leaders"""
    self.authority = (self.leader[0].authority / 2) + (self.leader[1].authority / 4) + \
                     (self.leader[2].authority / 4) + (self.leader[3].authority / 10)
    self.leader_social = self.leader[0].social
    if self.authority > 0:
        big_army_size = len(self.subunit_id_array)
        if big_army_size > 20:  # army size larger than 20 will reduce start_set leader authority
            self.authority = (self.team_commander.authority / 2) + (self.leader[0].authority / 2 * (100 - big_army_size) / 100) + \
                             (self.leader[1].authority / 2) + (self.leader[2].authority / 2) + (self.leader[3].authority / 4)
        else:
            self.authority += (self.team_commander.authority / 2)
