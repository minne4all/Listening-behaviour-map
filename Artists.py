import pandas as pd
import numpy as np
from Converters import Converters
from Tracks import Tracks

class Artists:
    def __init__(self) -> None:
        pass

    """
    Open CSV file and set the variables for the column names
    """
    def openFile(self, fileName:str, artistColumn:str, countryColumn:str, checkCountryColumn:str, seperator:str = ",", lowMemory:bool = True) -> None:
        self.df = pd.read_csv(fileName, sep=seperator, low_memory=lowMemory)
        self.df = self.df[[artistColumn, countryColumn, checkCountryColumn]]
        self.df = self.df[self.df[artistColumn].notna()]
        self.df = self.df.drop_duplicates(subset=["artist_mb"])
        self.artistCol = artistColumn
        self.countryCol = countryColumn
        self.checkCountryCol = checkCountryColumn

    """
    Check 2 country rows for artists to determine whether it's accurate
    accuracy of 1 means both rows need to agree on the country for the country to be accepted 
    accuracy of 0 is same as 1, but if one row is Nan, then it takes the other row's value
    """
    def checkCountries(self, accuracy:int = 0) -> None:
        countryColumn = []
        if accuracy:
            self.df.dropna()
            for _, row in self.df.iterrows():
                if row[self.countryCol] == row[self.checkCountryCol]:
                    countryColumn.append(row[self.countryCol])
                else:
                    countryColumn.append(np.nan)
        else:
            for _, row in self.df.iterrows():
                if type(row[self.checkCountryCol]) == float:
                    countryColumn.append(row[self.countryCol])
                elif type(row[self.countryCol]) == float:
                    countryColumn.append(row[self.checkCountryCol])
                elif row[self.countryCol] == row[self.checkCountryCol]:
                    countryColumn.append(row[self.countryCol])
                else:
                    countryColumn.append(np.nan)
        self.df["country"] = countryColumn
        self.df = self.df[[self.artistCol, "country"]]
        self.df = self.df.dropna()
        self.countryCol = "country"

    """
    Converts the country names form the countryColumn to alpha-iso3 codes
    """
    def convertCountryName_iso3(self, converter:dict) -> None:
        self.df[self.countryCol] = self.df[self.countryCol].map(converter)

    """
    Creates column with artist id from the tracks dataset
    """
    def mapArtistId(self, converter:dict) -> None:
        self.df["artistId"] = self.df[self.artistCol].map(converter)
        self.idCol = "artistId"

    """
    Creates dictionaries for converting: artist id <-> iso3
    Ex: iso3_artistID['UK'] returns all artist id within the UK
    """
    def create_artistID_iso3(self) -> None:
        self.artistID_iso3 = {}
        for _, row in self.df.iterrows():
            self.artistID_iso3[row[self.artistCol]] = row[self.countryCol]
        self.iso3_artistID = {}
        for iso3 in self.df[self.countryCol].unique():
            self.iso3_artistID[iso3] = self.df[self.df[self.countryCol] == iso3][self.idCol].unique()

    """
    Store the artistIds, so tracks doesn't need to be loaded everytime artist id's are needed
    """
    def storeIDs(self, artistName_artistId, path):
        iddf = pd.DataFrame(artistName_artistId.items(), columns=["name", "id"])
        iddf.to_csv(path)

    def loadIDs(self, path):
        iddf = pd.read_csv(path)
        self.artistID_artistName = pd.Series(iddf.name.values,index=iddf.id).to_dict()
        self.artistName_artistID = pd.Series(iddf.id.values,index=iddf.name).to_dict()

        




if __name__ == "__main__":
    artists = Artists()
    # artists.openFile("Data\\artists.csv", "artist_mb", "country_mb", "country_lastfm", lowMemory=False)
    # artists.checkCountries(1)

    # convs = Converters()
    # convs.create_iso3_countryName("Data\\CountryInfo.csv", "alpha-3", "name")

    # tracks = Tracks()
    # tracks.openFile('Data\\LFM-2b\\tracks.tsv', "track_id", "artist_name", badLines="skip")
    # tracks.create_artistName_artistID()

    # artists.storeIDs(tracks.artistName_artistID)

    artists.loadIDs()
    print(artists.artistId_artistName)

    # artists.convertCountryName_iso3(convs.countryName_iso3)
    # artists.mapArtistId(tracks.artistName_artistID)
    # artists.create_artistID_iso3()
    # print(artists.iso3_artistID)