def element_effect_count(self):
    """Count elemental value and apply status"""
    self.element_status_check["Fire"] = self.element_threshold_count(self.element_status_check["Fire"], "Burn", "Severe Burning")
    self.element_status_check["Water"] = self.element_threshold_count(self.element_status_check["Water"], "Wet", "Drench")
    self.element_status_check["Air"] = self.element_threshold_count(self.element_status_check["Air"], "Shock", "Electrocution")
    self.element_status_check["Earth"] = self.element_threshold_count(self.element_status_check["Earth"], "Stun", "Petrify")
    self.element_status_check["Poison"] = self.element_threshold_count(self.element_status_check["Poison"], "Poison", "Deadly Poison")
    self.element_status_check = {key: value - self.timer if value > 0 else value for key, value in
                                 self.element_status_check.items()}
