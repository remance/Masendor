import pygame

from random import choice

from gamescript.common import utility

from gamescript.common.damagesprite import play_animation, adjust_sprite


class EffectSprite(pygame.sprite.Sprite):
    effect_sprite_pool = None
    effect_animation_pool = None
    effect_list = None
    sound_effect_pool = None
    battle = None
    screen_scale = (1, 1)

    set_rotate = utility.set_rotate
    clean_object = utility.clean_object

    play_animation = play_animation.play_animation  # use play_animation from damage sprite
    adjust_sprite = adjust_sprite.adjust_sprite

    def __init__(self, attacker, base_pos, pos, target, angle, duration, sprite_type, sprite_name):
        """Effect sprite that does not affect subunit in any way"""
        self._layer = 10000000
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.show_frame = 0
        self.frame_timer = 0
        self.angle = angle
        self.rotate = False
        self.repeat_animation = False

        self.base_pos = base_pos
        self.pos = pos
        self.base_target = target
        self.duration = duration

        self.sound_effect_name = None
        self.sound_timer = 0
        self.sound_duration = 0
        self.repeat_animation = False
        self.scale_size = 1

        animation_name = "".join(sprite_name[1].split("_"))[-1]
        if animation_name.isdigit():
            animation_name = "".join([string + "_" for string in sprite_name[1].split("_")[:-1]])[:-1]
        else:
            animation_name = sprite_name[1]

        if sprite_type in self.sound_effect_pool:
            self.travel_sound_distance = self.effect_list[sprite_type]["Sound Distance"]
            self.travel_shake_power = self.effect_list[sprite_type]["Shake Power"]
            self.sound_effect_name = choice(self.sound_effect_pool[sprite_type])
            self.sound_duration = pygame.mixer.Sound(self.sound_effect_name).get_length()
            self.sound_timer = 0  # start playing right away when first update

        if "(team)" in sprite_type:
            self.current_animation = self.effect_animation_pool[sprite_type][attacker.team][animation_name]
        else:
            self.current_animation = self.effect_animation_pool[sprite_type][animation_name]

        self.image = self.current_animation[self.show_frame]

        self.base_image = self.image.copy()

        if self.angle != 0:
            self.image = pygame.transform.rotate(self.angle)

        self.rect = self.image.get_rect(center=self.pos)

    def update(self, subunit_list, dt):
        done, just_start = self.play_animation(0.1, dt, False)

        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                self.travel_sound_distance > self.battle.true_camera_pos.distance_to(self.base_pos):
            # play sound, check for distance here to avoid timer reset when not on screen
            self.battle.add_sound_effect_queue(self.sound_effect_name, self.base_pos,
                                               self.travel_sound_distance,
                                               self.travel_shake_power)
            self.sound_timer = 0

        if self.duration:
            self.duration -= dt
            if self.duration <= 0:  # kill effect when duration end
                self.clean_object()
                return
        elif done:  # no duration, kill effect when animation end
            if self.show_frame:
                self.clean_object()
                return
