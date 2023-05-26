from engine.uimenu import uimenu


def create_team_coa(self, data):
    for team_coa in self.team_coa:
        team_coa.kill()
        del team_coa

    selected_pos = (self.screen_rect.width / 2.75, self.screen_rect.height / 1.9)
    pos = [self.screen_rect.width / 3.5, self.screen_rect.height / 1.6]

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
        uimenu.TeamCoa((pos[0], pos[1]), selected_pos, faction_coa_list, team + 1, self.team_colour[team + 1],
                       faction_name)
        pos[1] += 70 * self.screen_scale[1]
        if team and (team + 1) % 4 == 0:
            pos = [pos[0] + 100, self.screen_rect.height / 1.6]
