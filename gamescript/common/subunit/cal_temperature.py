def cal_temperature(self, temp_reach):
    """Temperature mod function from terrain and weather"""
    if temp_reach < 0:  # cold temperature, the lowest temperature the subunit can reach change based on cold resist
        temp_reach = temp_reach * (100 - self.cold_resistance) / 100
    else:  # hot temperature, the highest temperature the subunit can reach change based on heat resist
        temp_reach = temp_reach * (100 - self.heat_resistance) / 100

    if self.temperature_count < temp_reach:  # increase temperature, rate depends on heat resistance
        self.temperature_count += (101 - self.heat_resistance) / 100 * self.timer
    elif self.temperature_count > temp_reach:  # decrease temperature, rate depends on cold resistance
        self.temperature_count -= (101 - self.cold_resistance) / 100 * self.timer

    # Temperature effect
    if self.temperature_count > 50:  # Hot
        if "Hot" in self.status_list:
            self.apply_effect(self.status_list["Hot"], self.status_list, self.status_effect, self.status_duration)
        if self.temperature_count > 100 and "Heatstroke" in self.status_list:
            self.apply_effect(self.status_list["Heatstroke"], self.status_list, self.status_effect, self.status_duration)
    elif self.temperature_count < -50:  # Cold
        if "Cold" in self.status_list:
            self.apply_effect(self.status_list["Cold"], self.status_list, self.status_effect, self.status_duration)
        if self.temperature_count < -100 and "Freeze" in self.status_list:  # Extremely cold
            self.apply_effect(self.status_list["Freeze"], self.status_list, self.status_effect, self.status_duration)

