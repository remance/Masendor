This folder keep common attribute data related to leader stat.

The leader_class data structure is as follows;

- leader social class on the first column

- discipline modifier bonus to unit according to its grade in each row from the second one

The leader_skill contains skill data similar to the troop skill. With the current way the skill data is structure and
read, troop skill for leader need to also be in the leader skill file for leader to use.

The ID of leader and commander skill has a letter in front of the number (L and C respectively) to make it distinct from
troop skill and their own to avoid python dict key duplication.

The skill has some additional value than the troop skill which are, Range for the activation range of the skill (Not
AOE)

The leader_trait is not really implemented yet. 