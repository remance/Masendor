def check_sprite_collision(self, sprite_a, sprite_b):
    if sprite_a.unit != sprite_b.unit:  # collide with subunit in other unit
        a_front_distance_to_b = sprite_a.front_pos.distance_to(sprite_b.base_pos)
        if sprite_a.team != sprite_b.team:  # enemy team
            if a_front_distance_to_b < sprite_a.hitbox_front_melee_distance:  # at possible hit range
                sprite_a.enemy_in_melee_distance.append(sprite_b)
                if a_front_distance_to_b < sprite_a.hitbox_front_distance:
                    sprite_a.unit.collide = True
        elif a_front_distance_to_b < sprite_a.hitbox_front_distance:  # cannot run pass other unit if either run or in combat
            sprite_a.friend_front.append(sprite_b)
            sprite_a.unit.collide = True
