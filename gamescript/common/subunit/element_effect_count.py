def element_effect_count(self):
    """Count elemental value and apply status"""
    self.element_status_check["Fire"] = self.element_threshold_count(self.element_status_check["Fire"], 28, 92)
    self.element_status_check["Water"] = self.element_threshold_count(self.element_status_check["Water"], 31, 93)
    self.element_status_check["Air"] = self.element_threshold_count(self.element_status_check["Air"], 30, 94)
    self.element_status_check["Earth"] = self.element_threshold_count(self.element_status_check["Earth"], 23, 35)
    self.element_status_check["Poison"] = self.element_threshold_count(self.element_status_check["Poison"], 26, 27)
    self.element_status_check = {key: value - self.timer if value > 0 else value for key, value in self.element_status_check.items()}
