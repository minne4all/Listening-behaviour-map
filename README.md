# Listening-behaviour-map
Some explanation of each folder/files and information on where to get the remaining datasets.

Data
- LFM-2b - not included
  - Download from: http://www.cp.jku.at/datasets/LFM-2b/
  - Needed files are: listening-counts.tsv, tracks.tsv and users.tsv
- Vars - not included
  - Download from: Google drive
- Results - partially included
  - Needed file is also included in the google drive download
- Other files not included
  - Download "all.csv" from: https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv
    - Rename it to "CountryInfo.csv"
  - Download "artists.csv" from: https://www.kaggle.com/code/pieca111/music-production-across-the-world/input
  - Put these files at the root of the data folder
 
Dash
- Map.py
  - Used for loading the map using Dash
- MakeDF.py
  - Used for making the dataframes combining the results from the notebooks
- rank_difference.py
  - Used to make create a ranked difference to display on the map

Notebooks
- Data exploration
  - Used for gettin some exploratory data from the LFM-2b datasets
- Get country of artists
  - Standardize country information for artists
- Get country_s listening counts
  - Used to get the main results from the data
    - Results are artists and country's popularity for every country using several popularity measurements
        
