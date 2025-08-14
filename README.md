# Instructions:

For a given game-type, take the three most recent games and output the following:

   - The three favourites from each race - with name and V-odds,

   - Whether or not the favourite horse won,

   - The median or average finishing position of the favourite horse across all races,

   - How often does the favourite horse win?

The following end-points will be of use:

  - https://www.atg.se/services/racinginfo/v1/api/products/<gameType>

  - https://www.atg.se/services/racinginfo/v1/api/games/<gameID>

The game types you will consider are: ['V75', 'GS75', 'V86', 'V64', 'V65', 'V5', 'V4', 'V3', 'dd', 'ld']

    e.g. https://www.atg.se/services/racinginfo/v1/api/products/V75

## Pointers:

* Once you find a way to get all relevant data for a race, build a flat data structure for all the races you will be processing and store in a pandas DataFrame,

* The product end-point will provide you with the most recent games with results for the given game-type,

* The game end-point will provide you with each of the game's races, which in turn contain multiple starts/horses,

* Result = 0 is similar to DNF (did not finish),

* V-odds can be found within each start's `pools.vinnare`,

* The favourite horse is the one with the lowest V-odds,

* Don't be afraid to ask questions if you need any assistance.


 ## Solution:

 ### $python3 output_winner_stats.py
 Output a dataframe containing the three most recent games, with the top
 three horses with name and V-odds, favorite's final position, and if they
 won or not (1 indicates a win, 0 everything else). 

 We also output win-%, median finishing position, and mean finishing poistion for the favourite across all different game types. 

### $python3 output_winner_stats.py --test
A simple sanity check to see that we are computing the correct statistics. 
Generates a json where the following stats are true: 

% Fav wins 0.2857142857142857
Median placement 2.0
Mean placement 2.5714285714285716


