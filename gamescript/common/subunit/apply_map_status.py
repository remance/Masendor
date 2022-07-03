def apply_map_status(self, map_feature_mod):
    if 0 not in map_feature_mod["Status"]:  # Some terrain feature can also cause status effect such as swimming in water
        if 1 in map_feature_mod["Status"]:  # Shallow water type terrain
            self.status_effect[31] = self.status_list[31].copy()  # wet
        if 4 in map_feature_mod["Status"] or 5 in map_feature_mod["Status"]:  # Deep water type terrain
            if 5 in map_feature_mod["Status"]:
                self.status_effect[93] = self.status_list[93].copy()  # drench

            if self.weight > 60 or self.stamina <= 0:  # weight too much or tired will cause drowning
                self.status_effect[102] = self.status_list[102].copy()  # Drowning

            elif self.weight > 30:  # Medium weight subunit has trouble travel through water and will sink and progressively lose troops
                self.status_effect[101] = self.status_list[101].copy()  # Sinking

            elif self.weight < 30:  # Lightweight subunit has no trouble travel through water
                self.status_effect[104] = self.status_list[104].copy()  # Swimming

        if 2 in map_feature_mod["Status"]:  # Rot type terrain
            self.status_effect[54] = self.status_list[54].copy()

        if 3 in map_feature_mod["Status"]:  # Poison type terrain
            self.element_status_check["Poison"] += ((100 - self.element_resistance["Poison"]) / 100)

        if 6 in map_feature_mod["Status"]:  # Mud terrain
            self.status_effect[106] = self.status_list[106].copy()
