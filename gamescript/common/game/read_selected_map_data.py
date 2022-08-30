from gamescript.common import utility

csv_read = utility.csv_read


def read_selected_map_data(self, map_list, file, source=False):
    if self.menu_state == "preset_map" or self.last_select == "preset_map":
        if source:
            data = csv_read(self.main_dir, file,
                            ["data", "ruleset", self.ruleset_folder, "map", map_list[self.current_map_select],
                             str(self.map_source), self.genre])
        else:
            data = csv_read(self.main_dir, file,
                            ["data", "ruleset", self.ruleset_folder, "map", map_list[self.current_map_select]])
    else:
        data = csv_read(self.main_dir, file, ["data", "ruleset", self.ruleset_folder, "map/custom",
                                              map_list[self.current_map_select]])
    header = list(data.values())[0]
    del data[list(data.keys())[0]]  # remove header from dict
    data = {key: {header[index]: value[index] for index, value2 in enumerate(value)} for key, value in data.items()}
    return data
