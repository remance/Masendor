Here in this folder is the data files related to sub-unit stat.

The folder unit_ui contain texture images for both unit and sub-unit. Note that the effect to sub-unit stat can be classified into 2 types: Effect (e.g. Charge Effect) and Bonus (e.g. Morale Bonus). Effect modifier will be applied to the stat in percentage. For example, 120 charge effect will be applied in this way: sub-unit's charge * 120 / 100. Meanwhile, Bonus modifier will be applied by addition or substract directly. For example -20 Morale bonus will be applied in this way: Sub-unit's morale - 20. It is acceptable to leave effect column empty and it will be automatically considered as 100. Do not leave other columns empty, if there is no bonus effect then put in 0.


Implement_record: This file is not used in game but for record keeping which effect I still haven't implement

Unit_ability: the data structure of ability is as follows;

Skill Type (0=melee, 1=range) this will affect which damage and elemental effect the skill will boost| Area of Effect (1=self and frontal enemy damage,2=Direct Nearby only, 3=Nearby including corner, 4=whole unit) this also affect the enemy status infliction| Duration of skill in second | Cooldown of skill in second | Mana cost | Discipline Requirement to use the skill | Stamina Cost per use | Stat Effect and bonus modifier as mentioned above| status (only to friendly sub-units according to aoe) | stamina damage (each time sub-unit deal dmg it will also deal damage to stamina) | morale damage (each time sub-unit deal dmg it will deal addtional morale damage)


unit_armour


unit_grade



unit_item: Not yet implemented 


unit_mount


unit_mountarmour: Not yet implemented

unit_property


unit_race: Not yet implemented


unit_status



unit_type:

unit_weapon:


In s