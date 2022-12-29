This folder is the data for leader preset.

There are currently two main components for leader presets which are:

Unique leader (leader.csv): This is the list of named leader preset with historical context. The first leader in this
file must always be "None" leader.

Common leader: This is the list of unnamed leader based on job/class instead with somewhat basic stat and common ability

Currently all leader stat data structure are in the same structure

ID | Name | Authority 0-100 | Melee Command 0 - 10 | Range Command 0 - 10 | Cav Command 0 - 10 | Personal combat skill 0
- 10 | Social class (refer to in data/leader/leader_class.csv) | Description

Then there are leader lore files for both unique and common leader seperate which contain information for encyclopedia

Lastly, there is a folder for keeping leader portrait. The portrait file name must be the leader id for identification
process. The portrait image should be a circle but it can also be a square or other shapes (Maybe ugly on leader ui).
The last portrait image in name ordered is used for leader with no portrait and the first is used for "None" leader.