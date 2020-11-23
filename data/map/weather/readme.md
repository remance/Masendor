This folder keeps all data related to game weather. 

- The number folders are sprite texture folders that spawn during the weather, all texture files in the folder will be spawned as sprite randomly at the rate and travel at speed as assigned in weather.csv. 

- Effect folder consists of special weather effect texture sub-folder (name in weatherid) that spawn during the weather. If the special effect for that weather existed, there must be three images file (0,1,2) that will be used for each weather level. 

- weather.csv contain all weather and modifcation for sub-unit stat, sprite spawn rate (0 mean no sprite), sprite travel angle and speed. Special effect is the texture effect id that will be draw into the whole screen (e.g. fog), the effect travel logic also used the sprite travel logic in the previous two columns. Every value in this file is the value at weakest level of the weather (0 = Light, 1 = Normal, 2 = Strong). The second level double all value and the third level triple all value including sprite speed and spawn rate.

To create new weather and use it, a texture folder with the id must also be created even if there is no sprite, same for effect folder. Icon must also be created for all 3 levels (for example weather id 20: 20_0, 20_1, 20_2).