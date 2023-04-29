Animation

This folder contains list of animation for each direction.

The animation file need to be in this structure:
Animation name, each p1 and p2 parts, effect, special, frame and animation properties

Animation name should be like this

for general animation "race name"_"animation name"_"animation varient number"/"frame number"  (e.g., human_walk_0/0)

for weapon animation: "weapon type"_"hand variation either Main or Sub"_"name"_"animation varient number"/"frame
number"  (e.g., human_Main_1hand_Slash/1)

Each animation part need to be in this format:
race/type,direction name, part name, position x, position y, angle, flip (0=none,1=hori,2=verti,3=both), layer, scale (1
for default)

THERE MUST BE NO SPACE BETWEEN COMMA IN ANY VALUE

The position is based on the default side before any flip (face right for side, corner up and corner down).

layer value is similar to pygame layer, the higher value get drew first and lower value get drew later and above the
higher value layer. Layer must start from 1 and should not have duplcate value, layer 0 will not be drew.

List of animation frame properties:
"hold": frame can be hold with input
"turret": not sure how it will work yet but for when sprite can face other direction while walking in other direction
"effect_": add special image effect (not animation effect) like blur, need effect name after and related input value "
effect_" (e.g., effect_blur_50)

List of animation effect propertiers:  # only need to be put in at the first frame row.
"dmgsprite": sprite will do damage with the whole sprite instead of just damage effect
"interuptrevert": effect run revert back to first frame when animation is interupted, can only be use with external
effect
"norestart": animation will use the last frame instead of restart when continue with the same animation