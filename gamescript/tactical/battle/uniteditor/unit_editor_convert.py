from gamescript.common.battle.generate_unit import generate_unit


def unit_editor_convert(self, which_army, row, colour, coa, subunit_game_id):
    print(row)
    for key, value in row.items():  # convert string to number
        if type(value) == str and value.isdigit():
            row[key] = int(value)
        elif type(value) == list:
            row[key] = [int(item) for item in value]
    generate_unit(self, which_army, row, True, True, colour, coa, subunit_game_id)
