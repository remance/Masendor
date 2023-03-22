from gamescript.common import utility

csv_read = utility.csv_read


def read_selected_map_data(self, map_list, file, source=False):
    if self.menu_state == "preset_map" or self.last_select == "preset_map":
        if source:
            data = csv_read(self.main_dir, file,
                            ("data", "ruleset", self.ruleset_folder, "map", "preset", map_list[self.current_map_select],
                             str(self.map_source)))
        else:
            data = csv_read(self.main_dir, file,
                            ("data", "ruleset", self.ruleset_folder, "map", "preset", map_list[self.current_map_select]))
    else:
        if map_list[self.current_map_select] != "Random":
            try:
                data = csv_read(self.main_dir, file, ("data", "ruleset", self.ruleset_folder, "map", "custom",
                                                      map_list[self.current_map_select]))
            except FileNotFoundError:  # try from preset list
                data = csv_read(self.main_dir, file, ("data", "ruleset", self.ruleset_folder, "map", "preset",
                                                      map_list[self.current_map_select]))
        else:
            data = {"Name": ["Description 1", "Description 2"], 'Random': ["", ""]}
    header = tuple(data.values())[0]
    del data[list(data.keys())[0]]  # remove header from dict
    data = {key: {header[index]: value[index] for index, value2 in enumerate(value)} for key, value in data.items()}
    return data
