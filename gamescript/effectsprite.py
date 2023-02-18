import pygame

from gamescript.common import utility

from gamescript.common.damagesprite import play_animation


class EffectSprite(pygame.sprite.Sprite):
    effect_sprite_pool = None
    effect_animation_pool = None
    screen_scale = (1, 1)

    set_rotate = utility.set_rotate
    clean_object = utility.clean_object

    play_animation = play_animation.play_animation  # use play_animation from damage sprite

    def __init__(self, attacker, start_pos, target, angle, duration, sprite_type, sprite_name):
        self._layer = 10000000
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.show_frame = 0
        self.animation_timer = 0
        self.angle = angle
        self.rotate = False
        self.repeat_animation = False

        self.pos = start_pos
        self.base_target = target
        self.duration = duration

        animation_name = "".join(sprite_name[1].split("_"))[-1]
        if animation_name.isdigit():
            animation_name = "".join([string + "_" for string in sprite_name[1].split("_")[:-1]])[:-1]
        else:
            animation_name = sprite_name[1]

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

        if self.duration:
            self.duration -= dt
            if self.duration <= 0:  # kill effect when duration end
                self.clean_object()
                return
        elif done:  # no duration, kill effect when animation end
            if self.show_frame:
                self.clean_object()
                return

        if just_start:
            self.rect = self.image.get_rect(center=self.pos)
