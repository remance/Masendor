This folder contains unit preset data including its historical context/lore.

The unit_preset data structure is as follows;

- Name should not be longer than 20 - 30 characters

- ImageID is which weapon (melee or range)'s imageid sub-unit will used as its weapon icon

- Grade is the training level of the sub-unit. Refer to data\war\unit_grade.csv for detailed data of the grade.

- Race, not yet implemented

- Properties is the list of properties this sub-unit has. If there is none, simply put it as 0. int number (5) and list number (1,66,93) are acceptable.

- Abilities similar to properties list

- Base "cost", this does not include equipment cost, not yet implemented

- Upkeep, not yet implemented

- Stat of the sub-unit. The higher the number, the better the unit perform in that aspect. Reload is slightly different than the other, the lower the number, the shorter reload time before unit can shoot.

- Charge skill is the skill that unit use for charging. It is possible to use other skill than the "charge one" but it may has some unexpected result. Does not accept list number. Use 21 for default charge

- Melee weapon is the melee weapon this sub-unit equipped with. The format must be (weaponid,quality). The quality is as follows; 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect

- Range weapon is similar to melee weapon but is only used when perform range attack. it is acceptable to be unarmed for range weapon, simply put in 1,0. Note that unarmed does not stop sub-unit from doing range attack if it has ammunition.

- Size is the size of the troop and will take more slot in the unit. Default is 1 slot. The larger unit (2) will take 4 slot. Not yet implemented

- Troop is the total number of troop per sub-unit. Each troop has starting health as put in the health column. For example, sub-unit with 100 troops and 100 health = 10000 total health. 1000 damage would mean 10 troops would be killed.

- Unit type is the type of this sub-unit, not really used for any calculation yet.

- Mount that this unit is equiped with and its grade. 1,0 mean the sub-unit does not have any mount. Note that equipped with mount will make the sub-unit be considered as calvary.

- Spell, not yet implemented

- Item, not yet implemented