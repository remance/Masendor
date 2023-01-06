def temperature_cal(self, temp_reach):
    """Temperature mod function from terrain and weather"""
    if temp_reach < 0:  # cold temperature
        temp_reach = temp_reach * (
                100 - self.cold_resistance) / 100  # lowest temperature the subunit will change based on cold resist
    else:  # hot temperature
        temp_reach = temp_reach * (
                100 - self.heat_resistance) / 100  # highest temperature the subunit will change based on heat resist

    if self.temperature_count < temp_reach:
        self.temperature_count += (
                                          101 - self.heat_resistance) / 100 * self.timer  # increase temperature, rate depends on heat resistance
    elif self.temperature_count > temp_reach:
        self.temperature_count -= (
                                          101 - self.cold_resistance) / 100 * self.timer  # decrease temperature, rate depends on cold resistance

    # Temperature effect
    if self.temperature_count > 50:  # Hot
        if "Hot" in self.status_list:
            self.apply_effect(self.status_list["Hot"], self.status_list, self.status_effect)
        if self.temperature_count > 100 and "Heatstroke" in self.status_list:
            self.apply_effect(self.status_list["Heatstroke"], self.status_list, self.status_effect)
    elif self.temperature_count < -50:  # Cold
        if "Cold" in self.status_list:
            self.apply_effect(self.status_list["Cold"], self.status_list, self.status_effect)
        if self.temperature_count < -100 and "Freeze" in self.status_list:  # Extremely cold
            self.apply_effect(self.status_list["Freeze"], self.status_list, self.status_effect)

