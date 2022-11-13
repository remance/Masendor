import pygame
import pygame.freetype


class Weather:
    weather_icons = {}

    def __init__(self, time_ui, weather_type, level, weather_data):
        self.weather_type = weather_type
        if weather_data is not None:
            stat = weather_data[weather_type]
            self.name = stat["Name"]
            self.level = level  # weather level 0 = Light, 1 = Normal, 2 = Strong
            if self.level > 2:  # in case adding higher level number by mistake
                self.level = 2
            elif self.level < 0:  # can not be negative level
                self.level = 0
            cal_level = self.level + 1

            self.melee_atk_buff = stat["Melee Attack Bonus"] * cal_level
            self.melee_def_buff = stat["Melee Defense Bonus"] * cal_level
            self.range_def_buff = stat["Range Defense Bonus"] * cal_level
            self.speed_buff = stat["Speed Bonus"] * cal_level
            self.accuracy_buff = stat["Accuracy Bonus"] * cal_level
            self.range_buff = stat["Range Bonus"] * cal_level
            self.reload_buff = stat["Reload Bonus"] * cal_level
            self.charge_buff = stat["Charge Bonus"] * cal_level
            self.charge_def_buff = stat["Charge Defense Bonus"] * cal_level
            self.hp_regen_buff = stat["HP Regeneration Bonus"] * cal_level
            self.stamina_regen_buff = stat["Stamina Regeneration Bonus"] * cal_level
            self.morale_buff = stat["Morale Bonus"] * cal_level
            self.discipline_buff = stat["Discipline Bonus"] * cal_level
            self.sight_buff = stat["Sight Bonus"] * cal_level
            self.hidden_buff = stat["Hide Bonus"] * cal_level
            self.temperature = stat["Temperature"] * cal_level
            self.element = tuple([(element, cal_level) for element in stat["Element"] if element != ""])
            self.status_effect = stat["Status"]
            self.spawn_rate = stat["Spawn Rate"] / cal_level  # divide to make spawn increase with strength
            self.spawn_angle = stat["Travel Angle"]
            self.speed = stat["Travel Speed"] * cal_level
            image = self.weather_icons[self.name + "_" + str(self.level)]
            cropped = pygame.Surface((image.get_width(), image.get_height()))
            cropped.blit(time_ui.image_original, (0, 0), (0, 0, 80, 80))
            crop_rect = cropped.get_rect(topleft=(0, 0))
            cropped.blit(image, crop_rect)
            image = cropped

            rect = image.get_rect(topright=(time_ui.image.get_width() - 5, 0))
            time_ui.image.blit(image, rect)


class MatterSprite(pygame.sprite.Sprite):
    def __init__(self, pos, target, speed, image):
        self._layer = 9
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.speed = speed
        self.pos = pygame.Vector2(pos)  # should be at the end corner of screen
        self.target = pygame.Vector2(target)  # should be at another end corner of screen
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt, timer):
        """Update sprite position movement"""
        move = self.target - self.pos
        move_length = move.length()
        if move_length > 0.1:
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.pos += move
                self.rect.center = list(int(v) for v in self.pos)
            else:
                self.pos = self.target
                self.rect.center = self.target
        else:  # kill when it reach the end of screen
            self.kill()


class SpecialEffect(pygame.sprite.Sprite):
    """Special effect from weather beyond sprite such as thunder, fog etc."""

    def __init__(self, pos, target, speed, image, end_time):
        self._layer = 8
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pygame.Vector2(pos)
        self.target = pygame.Vector2(target)
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)
        self.end_time = end_time

    def update(self, dt, timer):
        """Update sprite movement and removal"""
        move = self.target - self.pos
        move_length = move.length()
        if (self.rect.midleft[0] > 0 and timer < self.end_time) or (
                self.end_time is not None and timer >= self.end_time and self.rect.midright[0] > 0):
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.pos += move
                if timer < self.end_time and self.pos[0] > 0:  # do not go beyond 0 if weather event not end yet
                    self.rect.midleft = list(int(v) for v in self.pos)
                else:
                    self.rect.midleft = pygame.Vector2(0, self.pos[1])
            else:
                self.rect.midleft = self.target
        elif timer >= self.end_time and self.rect.midright[0] < 0:
            self.kill()


class SuperEffect(pygame.sprite.Sprite):
    """Super effect that affect whole screen"""

    def __init__(self, pos, image):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self)
