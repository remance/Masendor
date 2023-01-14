from gamescript.common.battle.generate_unit import generate_unit


def deploy_unit_editor(self, which_army, row, colour, coa, subunit_game_id):
    for key, value in row.items():  # convert string to number
        if "Row" not in key:  # generate_unit use string item array for subunit data
            if type(value) == str and value.isdigit():
                row[key] = int(value)
            elif type(value) == list:
                row[key] = [int(item) for item in value]
    generate_unit(self, which_army, row, True, True, colour, coa, subunit_game_id, self.troop_data.troop_list,
                  self.leader_data.leader_list)
