from engine.effect.cal_dmg import cal_dmg_penetrate


def cal_effect_hit(self, target, hit_angle):
    impact = self.knock_power
    troop_dmg, element_effect = cal_dmg_penetrate(self, target, reduce_penetrate=False)

    if self.aoe:
        distance = target.base_pos.distance_to(self.base_pos)
        if distance > self.aoe / 2:
            distance_mod = distance / (self.aoe + 1)
            impact *= distance_mod
            troop_dmg *= distance_mod
            for key in element_effect:
                element_effect[key] *= distance_mod

    morale_dmg = troop_dmg / 10

    # Damage cannot be negative (it would heal instead), same for morale dmg
    if troop_dmg < 0:
        troop_dmg = 0
    if morale_dmg < 0:
        morale_dmg = 0

    target.cal_loss(troop_dmg, impact, morale_dmg, element_effect, hit_angle)
    target.take_aoe_dmg = 3
