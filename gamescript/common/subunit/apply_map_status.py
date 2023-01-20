def apply_map_status(self, map_feature_mod):
    if 0 not in map_feature_mod["Status"]:  # Some terrain feature can cause status effect such as swimming in water
        if 1 in map_feature_mod["Status"]:
            if "Wet" in self.status_list:  # Shallow water type terrain
                self.apply_effect(self.status_list["Wet"], self.status_list, self.status_effect, self.status_duration)
        if 4 in map_feature_mod["Status"] or 5 in map_feature_mod["Status"]:  # Deep water type terrain
            if 5 in map_feature_mod["Status"] and "Drench" in self.status_list:
                self.apply_effect(self.status_list["Drench"], self.status_list, self.status_effect,
                                  self.status_duration)

            if self.weight > 60 or self.stamina <= 0:  # weight too much or tired will cause drowning
                if "Drown" in self.status_list:
                    self.apply_effect(self.status_list["Drown"], self.status_list, self.status_effect,
                                      self.status_duration)

            elif self.weight > 30:  # Medium weight subunit has trouble travel through water and will sink and progressively lose troops
                if "Sink" in self.status_list:
                    self.apply_effect(self.status_list["Sink"], self.status_list, self.status_effect,
                                      self.status_duration)

            elif self.weight < 30:  # Lightweight subunit has no trouble travel through water
                if "Swimming" in self.status_list:
                    self.apply_effect(self.status_list["Swimming"], self.status_list, self.status_effect,
                                      self.status_duration)

        if 2 in map_feature_mod["Status"]:  # Rot type terrain
            if "Decay" in self.status_list:
                self.apply_effect(self.status_list["Decay"], self.status_list, self.status_effect, self.status_duration)

        if 3 in map_feature_mod["Status"]:  # Poison type terrain
            self.element_status_check["Poison"] += ((100 - self.element_resistance["Poison"]) / 100)

        if 6 in map_feature_mod["Status"]:  # Mud terrain
            if "Muddy Leg" in self.status_list:
                self.apply_effect(self.status_list["Muddy Leg"], self.status_list, self.status_effect,
                                  self.status_duration)
