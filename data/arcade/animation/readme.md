Animation

direction name, filename, base position x, base position y, angle, flip (0=none,1=hori,2=verti,3=both), layer

The position is based on the default side before any rotation (face right for side, corner up and corner down).

layer value is similar to pygame layer, the higher value get drew first and lower value get drew later and above the higher value layer. Layer must start from 1 and should not have duplcate value, layer 0 will not be drew.

List of animation frame properties:
"movable": animation can be performed when moving and moving can be initiate during animation
"uninterupt": animation can not be interupt by anything else (normally can be interupted like when take damage)
"cancelable": can be cancel with other animation input
"invincible": can not be damaged during animation
"revert": run animation in revert frame

List of animation frame properties:
"hold": frame can be hold with input, weapon do damage during hold (e.g., spearwall)
"power": similar to hold but start power version and deal no damage
"block": similar to hold but use full defence from the weapon and deal no damage
"parry": will do parry animation after if hit during this animation
"turret": not sure how it will work yet but for when sprite can face other direction while walking in other direction 
"effect_": add special image effect (not animation effect) like blur, need effect name after and related input value "effect_" (e.g., effect_blur50)

List of animation effect propertiers:
"aoe": effect deal further aoe damage outside of sprite effect in distance, need distance number after "aoe" (e.g.,aoe10)
"dmgsprite": whole sprite can cause damage instead of a single point
"externaleffect": effect use its own external animation frame instead of the frame assigned in animation sprite, accept only the first frame for starting the effect animation 
"duration": effect remain in loop for duration, need duration number in second after "duration" (e.g.,duration60)
"nodmg": effect deal no dmg and will not check in code
"interuptrevert": effect run revert back to first frame when animation is interupted, can only be use with external effect