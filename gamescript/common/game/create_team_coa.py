from gamescript import menu


def create_team_coa(self, data, ui_class, one_team=False, team1_set_pos=None):
    for team in self.team_coa:
        team.kill()
        del team
    if team1_set_pos is None:
        team1_set_pos = (self.screen_rect.width / 2 - (400 * self.screen_scale[0]), self.screen_rect.height / 3)
    # position = self.map_show[0].get_rect()
    self.team_coa.add(menu.TeamCoa(self.screen_scale, team1_set_pos, self.faction_data.coa_list[data[0]],
                                   1, self.faction_data.faction_list[data[0]]["Name"]))  # team 1

    if one_team is False:
        self.team_coa.add(menu.TeamCoa(self.screen_scale, (
        self.screen_rect.width / 2 + (400 * self.screen_scale[0]), self.screen_rect.height / 3),
                                       self.faction_data.coa_list[data[1]], 2,
                                       self.faction_data.faction_list[data[1]]["Name"]))  # team 2
    ui_class.add(self.team_coa)
