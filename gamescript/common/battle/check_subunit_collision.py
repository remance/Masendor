def check_subunit_collision(self, a, b):
    if a.unit != b.unit:  # collide with subunit in other unit
        a_front_distance_to_b = a.front_pos.distance_to(b.base_pos)
        if a.team != b.team:  # enemy team
            if a_front_distance_to_b < a.hitbox_front_melee_distance:  # at possible hit range
                a.enemy_in_melee_distance.append(b)
                if a_front_distance_to_b < a.hitbox_front_distance:
                    a.unit.collide = True
                    a.front_collide.append(b)
        elif a_front_distance_to_b < a.hitbox_front_distance:  # cannot run pass other unit if either run or in combat
            a.front_collide.append(b)
            a.unit.collide = True
