# Listening-behaviour-map

# How to run
**Data and Results folder**

Still needs some extra files, which can be downloaded at: https://drive.google.com/drive/folders/1lLbNQ0dvjjS_jnC7g3R2iTUgjJxeFaPv?usp=sharing.

**LFM-2b folder**

To run the map download "users.tsv.bz2" from: http://www.cp.jku.at/datasets/LFM-2b/
Extract and put "users.tsv" into "LFM-2b" folder.

After putting these files in their respective folders, run "Map.py" to run the map. 

# Files
Map.py
- Used for loading the map visualization in Dash.
- Uses dataframes created in "makeMapDf.py".

Artists.py
- Uses artists' country information to create converters that converts artists to their countries and vice versa.

Tracks.py
- Uses LFM-2b track data to make converters.

Users.py
- Uses LFM-2b user data to convert users to their countries.

Converters.py
- Used to create more general converters not tied to any data set.
  
makeMapDf.py
- Used to make dataframes compatible with "Map.py".
- Also uses the results from "streams.py" and other sepcific datasets classes mentioned above.

Streams.py
- Creates the listening behaviour matrices which is used by "makeMapDf.py" to create the dataframes for the map. 

RankDifference.py
  - Used to make create a ranked difference to display on the map.
