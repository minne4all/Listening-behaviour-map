import pandas as pd
import numpy as np
from Converters import Converters
from Users import Users
from Artists import Artists
from Tracks import Tracks

class MapDf:
    def __init__(self) -> None:
        self.df = pd.DataFrame()

    """
    Add listening count results to df based on a country x country result matrix
    in the kwargs multiple result matrix can be used by adding: columnName = resultMatrixVariable
    """
    def addCountryListeningCounts(self, id_iso3:dict, iso3_countryName:dict, **kwargs):
        data = []
        for idc, row in enumerate(zip(*kwargs.values())):
            scountry = id_iso3[idc]
            for i in range(len(row[0])):
                iso = id_iso3[i]
                addData = [iso3_countryName[scountry], iso3_countryName[iso], iso]
                for count in row:
                    addData.append(count[i])
                data.append(addData)
        cols = ["selectcountry", "listencountry", "iso"]
        for names in kwargs:
            cols.append(names)
        self.df = pd.DataFrame(data, columns=cols)

    """
    Adds logged columns of the country listening counts
    """
    def logResults(self):
        columns = list(set(self.df.columns).difference(["selectcountry", "listencountry", "iso"])) 
        for col in columns:
            self.df[col + "_logged"] = np.log2(self.df[col])

    """
    Creates dictionary which takes iso3 code as input and outputs the country's user count
    Needed for createAverageCounts
    """
    def getCountry_userCount(self, iso3_user:dict):
        self.iso3_userCount = {k:len(v) for (k,v) in iso3_user.items()} 
        self.totalUsers = sum([self.iso3_userCount[x] for x in self.iso3_userCount.keys()])

    """
    Creates the column for relativetotalcount, based on a column used in addCountryListeningCounts
    Divides the total count by the average global listen count.
    Compares the listening behaviour for that country against the global listening behaviour. 
    """
    def createAverageCounts(self, column:str, countryname_iso3:dict):
        avgdict = {}
        for lc in self.df["listencountry"].unique():
            avg = sum(self.df[self.df["listencountry"] == lc][column]) / len(self.df["listencountry"].unique()) 
            avgdict[lc] = avg

        tcavg = []
        for _, row in self.df.iterrows():
            if avgdict[row["listencountry"]] != 0:
                usercount = self.iso3_userCount[countryname_iso3[row["selectcountry"]]]
                tcavg.append(row[column] / (avgdict[row["listencountry"]] / usercount))
            else:
                tcavg.append(0)

        self.df["relativetotalcount"] = minmax(tcavg)

"""
Creates globaldf based on a country result matrix
Used to create the measurement of global listening count
"""
def makeGlobalDf(countryResultMatrix:np.array, id_iso3:dict, iso3_artistID:dict, iso3_countryName:dict) -> pd.DataFrame:
    aggCountry = countryResultMatrix.sum(axis=0)
    globalcount = []
    for i, count in enumerate(aggCountry):
        if id_iso3[i] in iso3_artistID.keys():
            globalcount.append(count / len(iso3_artistID[id_iso3[i]]))
        else:
            globalcount.append(0)

    globalData = {"Globalcount" : np.log2(globalcount), 
                "iso" : [id_iso3[x] for x in range(len(countryResultMatrix))],
                "Countryname" : [iso3_countryName[id_iso3[x]] for x in range(len(countryResultMatrix))],
                "Totalcount" : aggCountry}
    return pd.DataFrame(data=globalData)

"""
MinMax function used in createAverageCounts
"""
def minmax(row):
    newlist = []
    rowmin = min(row)
    rowmax = max(row)
    for num in row:
        if num != 0:
            newlist.append((num - rowmin) / (rowmax - rowmin))
        else:
            newlist.append(0)
    return newlist




if __name__ == "__main__":
    countryListening = np.load("Results\\countrylistening.npy")
    countryListeningUT = np.load("Results\\countrylisteningUT.npy")
    countryListeningUA = np.load("Results\\countrylisteningUA.npy")

    convs = Converters()
    convs.create_iso2_iso3("Data\\CountryInfo.csv", "alpha-2", "alpha-3")
    convs.create_iso3_countryName("Data\\CountryInfo.csv", "alpha-3", "name")

    users = Users()
    users.openFile('LFM-2b\\users.tsv', "user_id", "country")
    users.streamReady(convs.iso2_iso3)
    users.create_user_iso3()

    convs.create_iso3_id(users.df[users.countryCol].unique())

    mapdf = MapDf()
    mapdf.addCountryListeningCounts(convs.id_iso3, convs.iso3_countryName, totalcount = countryListening, uniquetrackcount = countryListeningUT, uniqueartistcount = countryListeningUA)
    mapdf.logResults()
    mapdf.getCountry_userCount(users.iso3_users)
    mapdf.createAverageCounts("totalcount", convs.countryName_iso3)

    tracks = Tracks()
    tracks.openFile('LFM-2b\\tracks.tsv', "track_id", "artist_name", badLines="skip")
    tracks.create_artistName_tracks()
    tracks.create_artistName_artistID()

    artists = Artists()
    artists.openFile("Data\\artists.csv", "artist_mb", "country_mb", "country_lastfm", lowMemory=False)
    artists.checkCountries(1)
    artists.convertCountryName_iso3(convs.countryName_iso3)
    artists.mapArtistId(tracks.artistName_artistID)
    artists.create_artistID_iso3()

    globalDF = makeGlobalDf(countryListening, convs.id_iso3, artists.iso3_artistID, convs.iso3_countryName)
    print(globalDF)

    print(mapdf.df)

    mapdf.df.to_csv("testMapdf.csv")
    globalDF.to_csv("testGlobalDf.csv")
    