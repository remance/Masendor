import datetime

dawn_start = datetime.datetime.strptime("05:00:00", "%H:%M:%S")
dawn_start = datetime.timedelta(hours=dawn_start.hour, minutes=dawn_start.minute, seconds=dawn_start.second)

morning_start = datetime.datetime.strptime("07:00:00", "%H:%M:%S")
morning_start = datetime.timedelta(hours=morning_start.hour, minutes=morning_start.minute, seconds=morning_start.second)

dusk_start = datetime.datetime.strptime("17:00:00", "%H:%M:%S")
dusk_start = datetime.timedelta(hours=dusk_start.hour, minutes=dusk_start.minute, seconds=dusk_start.second)

night_start = datetime.datetime.strptime("19:00:00", "%H:%M:%S")
night_start = datetime.timedelta(hours=night_start.hour, minutes=night_start.minute, seconds=night_start.second)


def time_update(self):
    if self.time_number.time_number >= dawn_start:
        self.day_time = "Twilight"
        if self.time_number.time_number >= morning_start:
            self.day_time = "Day"
            if self.time_number.time_number >= dusk_start:
                self.day_time = "Twilight"
                if self.time_number.time_number >= night_start:
                    self.day_time = "Night"
        if self.old_day_time != self.day_time:
            self.old_day_time = self.day_time
            self.battle_map.add_effect(effect_image=self.weather_effect_images[self.current_weather.name][self.current_weather.level],
                                       time_image=self.day_effect_images[self.day_time])
