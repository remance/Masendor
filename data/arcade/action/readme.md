Sub-unit action

the file need to be in this format:
id,action name, gear/equipment related to the action, animation name to play, list of propoerties 

List of action properties:
"movable": animation can be performed when moving and moving can be initiate during animation
"uninteruptable": animation can not be interupt by anything else (normally can be interupted like when take damage)
"cancelable": can be cancel with other animation input beside forced animation
"invincible": can not be damaged during animation
"revert": run animation in revert frame
"holdfront": weapon do damage during hold like spearwall and pikewall
"power": start power version and deal no damage during hold
"timing_": add hold and release timing mechanic (can work with power and block) that improve accuracy, require count time number and release time window (e.g., timing_1.5_2 for start perfectiming 1.5 second after hold and last for 2 seconds) 
"block": use full defence from the weapon and deal no damage when hold
"parry": will do parry animation after get hit during this animation
"aoe": effect deal further aoe damage outside of sprite effect in distance, need distance number after "aoe" (e.g.,aoe10)
"externaleffect": effect use its own external animation frame instead of the frame assigned in animation sprite, accept only the first frame for starting the effect animation 
"duration": effect remain in loop for duration, need duration number in second after "duration" (e.g.,duration60)
"nodmg": effect deal no dmg and will not check in code
"dmgsprite": whole sprite can cause damage instead of a single point
"skip_": skip specific frames from playing use same indexing as list (e.g.skip_0_4_8 for skiping first, fourth, and eight frame)
