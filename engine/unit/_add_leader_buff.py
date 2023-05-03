def add_leader_buff(self):
    self.leader_social_buff = self.leader.social[self.grade_name]
    self.command_buff = 1 + (self.leader.leader_command_buff[
                                 self.unit_type] / 20)  # Command buff from leader according to this unit type
    self.authority = self.leader.leader_authority
