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
        self.status_effect[96] = self.status_list[96].copy()
        if self.temperature_count > 100:  # Extremely hot
            self.status_effect[97] = self.status_list[97].copy()
            del self.status_effect[96]
    if self.temperature_count < -50:  # Cold
        self.status_effect[95] = self.status_list[95].copy()
        if self.temperature_count < -100:  # Extremely cold
            self.status_effect[29] = self.status_list[29].copy()
            del self.status_effect[95]
