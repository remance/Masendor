Here in this folder is the data files related to sub-unit stat. The folder unit_ui contain texture images for both unit
and sub-unit. It is possible to modify the item already in the file but do not remove, move or change ID of the item as
it will cause error or incorrect application of the item.

Note that the effect to sub-unit stat can be classified into 2 types: Effect (e.g. Charge Effect) and Bonus (e.g. Morale
Bonus). Effect modifier will be applied to the stat in percentage. For example, 120 charge effect will be applied in
this way: sub-unit's charge * 120 / 100. Meanwhile, Bonus modifier will be applied by addition or substract directly.
For example -20 Morale bonus will be applied in this way: Sub-unit's morale - 20. It is acceptable to leave effect
column empty and it will be automatically considered as 100. Do not leave other columns empty, if there is no bonus
effect then put in 0.

Implement_record: This file is not used in game but for record keeping which effect I still haven't implement

troop_skill: list of all sub-units' abilities. The data structure of ability is as follows;

- Troop Type (0=any, 1=infantry, 2=cavalry) indicate which type of troop can use this skill

- Skill Type (0=melee, 1=range, 2=charge) this will affect which damage and elemental effect the skill will boost| Area
  of Effect (1=self and frontal enemy damage,2=Direct Nearby only, 3=Nearby including corner, 4=whole unit) this also
  affect the enemy status infliction| Duration of skill in second

- Cooldown of skill in second

- Mana cost per use, not yet implemented

- Discipline Requirement to use the skill

- Stamina Cost per use

- Stat Effect and bonus modifier as mentioned above

- Status effect (only to friendly sub-units according to aoe), assign 0 to indicate no status effect

- Stamina damage (each time sub-unit deal dmg it will also deal damage to stamina)

- Morale damage (each time sub-unit deal dmg it will deal addtional morale damage)

- Enemy status, similar to status effect but only to enemy sub-units (will implement range aoe later)

- "Element" addition to the attack (melee or range depends on skill type) 0 = physical, 1 = fire, 2 = water, 3 = air, 4
  = earth, 5 = magic, 6 = poison

- List of "Ruleset" id that skill is available

troop_armour: list of all sub-units' armours. The data structure of armour is as follows;

- "Armour" power that reduce the damage (0 to 100)

- Weight of the armour that will affect speed of the sub-unit (0 to 100)

- Purchase "Cost", not yet implemented

- Trait list that will be applied to the sub-unit that wear this armour

- List of Ruleset id that armour is available

troop_grade: list of all sub-units' grades, which represent the training level or class of the troop. The data structure
of grade is as follows;

- Stat Effect and bonus modifier as mentioned above

- Trait list that will be applied to the sub-unit with this grade

troop_item: Not yet implemented

troop_property: list of all sub-units' properties. The data structure of property is as follows;

troop_race: Not yet implemented

troop_status: list of all sub-units' status effects. The data structure of status is as follows;

- Special Effect list, see troop_special_status
- Status Conflict list that will remove the status effect if there is also any status in the list active

troop_type: list of all sub-units' types. Does not really affect anything yet beside just clarification.

troop_weapon: list of all sub-units' weapons including artillery weapons. The data structure of weapon is as follows;

- "Damage" power per attack

- Armour Penetration percentage (0 to 100) 0 means enemy armour is in full effect and 100 means the weapon completely
  bypass armour

- Weight of the weapon that will affect speed of the sub-unit (0 to 100)

- Skill list that will be applied to the sub-unit, see troop_skill.csv

- Trait list that will be applied to the sub-unit, see troop_trait.csv

- Speed is attack speed for melee weapon, how many times troop deal damage per attack. Reload time for range weapon, how
  long it take to reload in second at speed 1x

- Magazine for range weapon, how many time the unit can shoot before having to reload. 1 magazine is equal to 1 ammo.

- Range for only range weapon, for now this is convert directly to ingame range

- Travel speed for only range weapon, this is speed of sprite traveling to target

- Hand, number of hand required to use weapon, using both 2 hand and 1 hand at once will consider 1 hand weapon as
  sheathed weapon

- ImageID, the id of weapon image that will be used for sub-unit icon

- List of Ruleset id that armour is available

- Common animation type

- Action animation type

- Action properties

List of action properties:
"movable": animation can be performed when moving and moving can be initiate during animation
"uninterruptible": animation can not be interupt by anything else (normally can be interupted like when take damage)
"cancelable": can be cancel with other animation input beside forced animation
"invincible": can not be damaged during animation
"revert": run animation in revert frame
"hold": weapon action can hold at the frame with "hold" property
"holdfront": weapon do damage during hold like spearwall and pikewall
"power": hold start power charging
"timing_": add release timing mechanic for hold (can work with power and block) that improve accuracy, require count
time number and release time window (e.g., timing_1.5_2 for start perfect timing 1.5 second after hold and last for 2
seconds)
"block": use full defence from the weapon and deal no damage when hold
"parry": animation count as blocking and attack with bonus during if got hit by attack
"aoe": effect deal further aoe damage outside of sprite effect in distance, need distance number after "aoe" (
e.g.,aoe10)
"externaleffect": effect use its own external animation frame instead of the frame assigned in animation sprite, accept
only the first frame for starting the effect animation
"duration": effect remain in loop for duration, need duration number in second after "duration" (e.g.,duration60)
"nodmg": effect deal no dmg and will not check in code
"dmgsprite": whole sprite can cause damage instead of a single point
"skip_": skip specific frames from playing use same indexing as list (e.g.skip_0_4_8 for skiping first, fourth, and
eight frame)
"p(number)_fix_main_weapon" or "p(number)_fix_sub_weapon": Use center point instead weapon joint positon and place them
at the specified position instead of automatically at user's hand (main = right hand, sub = left hand)
"afterimage": play faded previous frame image along with the current frame

Weapon Type

mount_preset: list of all sub-units' mounts. The data structure of mount is as follows;

- Speed replacement to the sub-unit original speed

- Health bonus to the sub-unit

- Charge bonus to the sub-unit's charge power

- Purchase Cost

- Properties list that will be applied to the sub-unit with this mount

- List of "Ruleset" id that mount is available

mount_grade: list of mount grade with modifier to mount stat similar to unit_grade

mount_armour: list of mount armour with modifier to mount stat similar to unit_armour. The data structure is slightly
different than unit armour, mount armour provide additional health instead of armour stat.

Spell Preset

Concept:
Intensity affect Penetration power that affect range and duration
Quality affect damage
Quantity affect number of damage sprite per spell cast
Precision affect how accurate the spell will travel to location or occur from targeted area

cast time depends on total mana cost

Type

Instant = instant mana use, no cast time, high mana cost
Casting = instant mana use, cast time depends on mana cost, normal mana cost
Multi-casting = instant mana use, cast time depends on mana cost, cast same magic multiple times at once, exponential
increase mana cost per number of multi cast, use less mana than quantity of same number (e.g., fireball casting type
spell with 2 quantity use more mana but less cast time than fireball multi-casting of 2 times)
Channelling = intensity degradation resistance while cast, drain mana per second