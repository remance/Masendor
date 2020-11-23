This folder contains data related to the battle map, terrain and weather.

- texture folder keeps all feature texture file for each terrain feature combination in respective subfolder that will be drawn in slightly random position based on the beatiful map colour. the subfolder name must not have space and be fullname of the combination (e.g.Desert Forest = desertforest). The texture image must be in png file and has transparency channel or the map will look very ugly.

- Colourchange file contain list of new colour in (r,g,b) format for each terrain feature combination used in beautiful map. The game will draw texture by texture using these colours based on base and feature map images.

- Effect.png is the special effect that make map look like old map parchment, the image can be replaced with other effect as long as it is in png file with 1000x1000 size and has transparency channel. Image Opacity is recommended at around 50 - 60. This image will be applied after finish drawing beautiful map with both colour and feature texture.

- unit_terrainbonus is the record of modification effect to sub-unit stat for each terrain feature combination. Each terrain may affect infantry and cavalry units differently. The order of terrain feature combination is sorted based on base terrain type (See Mapguide table 3 for the exact sort ordered). 

Note that to add in new terrain or feature. the new terrain must be add as the last one with every feature. The new feature must be add to all previous based terrain as the last in list of the appropiate base terrain. "None" can be used for terrain feature combination that does not existed and will not be used.

These files must be changed accordingly: unit_terrainbonus, colourchange.csv, new texture subfolder in the texture folder. 

- For weather data and information, go inside weather folder. 