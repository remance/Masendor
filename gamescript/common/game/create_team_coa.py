from gamescript import menu


def create_team_coa(self, data, ui_class):
    for team_coa in self.team_coa:
        team_coa.kill()
        del team_coa

    pos = [self.screen_rect.width / 10, self.screen_rect.height / 8]

    for team, coa in enumerate(data):
        if type(coa) is list:
            faction_name = self.faction_data.faction_list[int(coa[0])]["Name"]
            faction_coa_list = {int(faction): self.faction_data.coa_list[int(faction)] for faction in coa}
        elif coa:
            faction_coa_list = {coa: self.faction_data.coa_list[coa[0]]}
            faction_name = self.faction_data.faction_list[coa]["Name"]
        else:  # empty team for custom map
            faction_coa_list = {0: None}
            faction_name = "None"
        self.team_coa.add(menu.TeamCoa((int(120 * self.screen_scale[0]), int(120 * self.screen_scale[1])),
                                       pos, faction_coa_list, team + 1, self.team_colour[team + 1], faction_name))
        pos[1] += 130 * self.screen_scale[1]
        if team == 4:
            pos = [self.screen_rect.width / 3.5, self.screen_rect.height / 8]

    ui_class.add(self.team_coa)
