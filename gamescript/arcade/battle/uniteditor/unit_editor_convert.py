from gamescript.common.battle.generate_unit import generate_unit


def unit_editor_convert(self, which_army, row, colour, coa, subunit_game_id):
    for n, i in enumerate(row):
        if type(i) == str and i.isdigit():
            row[n] = int(i)
        if n in range(1, 12):
            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
    subunit_game_id = generate_unit(self, which_army, row, True, True, colour, coa, subunit_game_id)
