from gamescript import menu


def create_team_coa(self, data, ui_class):
    for team_coa in self.team_coa:
        team_coa.kill()
        del team_coa

    pos = [self.screen_rect.width / 10, self.screen_rect.height / 8]

    for team, coa in enumerate(data):
        if type(data[team]) == str and "," in data[team]:
            faction_coa_list = data[team].split(",")
            first_faction = int(faction_coa_list[0])
            faction_coa_list = [self.faction_data.coa_list[int(faction)] for faction in faction_coa_list]
        else:
            faction_coa_list = [self.faction_data.coa_list[data[team]]]
            first_faction = data[team]
        self.team_coa.add(menu.TeamCoa((int(120 * self.screen_scale[0]), int(120 * self.screen_scale[1])),
                                       pos, faction_coa_list, coa, self.team_colour[team + 1],
                                       self.faction_data.faction_list[first_faction]["Name"]))
        pos[1] += 130 * self.screen_scale[1]
        if team == 6:
            pos = [self.screen_rect.width / 9, self.screen_rect.height / 8]

    ui_class.add(self.team_coa)
