import pandas as pd
import numpy as np
from Tracks import Tracks
from Users import Users
from Converters import Converters
from Artists import Artists

class Streams:
    def __init__(self) -> None:
        self.c = "c"

    """
    Open CSV file and set the variables for the column names
    If events are counted, provide countcolumn
    If events are not counted, then leave countColumn empty and program will group the events by itself
    """
    def openFile(self, fileName:str, userColumn:str, trackColumn:str, countColumn:str = "", seperator:str = "\t", badLines:str = "error") -> None:
        self.df = pd.read_csv(fileName, sep=seperator, on_bad_lines= badLines)
        self.userCol = userColumn
        self.trackCol = trackColumn
        if countColumn:
            self.df = self.df[[userColumn, trackColumn, countColumn]]
            self.countCol = countColumn
        else:
            self.df = self.df.groupby([self.userCol, self.trackCol]).size().reset_index().rename(columns={0:'count'})
            self.countCol = "count"

    """
    Filter out events from tracks and users that don't appear in there respective datasets
    """
    def filterUsersTracks(self, userList:list, trackList:list) -> None: 
        self.df = self.df[self.df[self.userCol].isin(userList)]
        self.df = self.df[self.df[self.trackCol].isin(trackList)]

    """
    Adds column for artist of the track and then group all artist user combinations
    """
    def createArtistColumn(self, track_artist:dict) -> None:
        artistColumn = []
        countDict = {}
        for _, row in self.df.iterrows():
            artist = track_artist[row[self.trackCol]]
            user = row[self.userCol]
            artistColumn.append(artist)
            if (user, artist) in countDict.keys():
                countDict[(user, artist)] += row[self.countCol]
            else:
                countDict[(user, artist)] = row[self.countCol]
        self.df["artist"] = artistColumn
        self.artistCol = "artist"
        self.df = self.df.groupby([self.userCol,self.artistCol]).size().reset_index().rename(columns={0:'countUT'})
        self.countUTCol = "countUT"
        totalCountColumn = []
        for _, row in self.df.iterrows():
            totalCountColumn.append(countDict[row[self.userCol], row[self.artistCol]])
        self.df["totalCount"] = totalCountColumn
        self.totalCountCol = "totalCount"

    """
    Creates 2 result matrices based on all unique artist and user combinations and stores them in .npy file
    CountryListening file groups all users and artists into their respective countries
    CountryArtist file only groups all users to their respective countries
    UA: Unique Artist
    """
    def createResultMatrix(self, country_id:dict, user_iso3:dict, artistName_id:dict, artistID_iso3:dict) -> None:
        ListCountUA = self.df.groupby([self.userCol,self.artistCol]).size().reset_index().rename(columns={0:'count'})
        countryArtistsUA = np.array([[0] * len(artistName_id)] * len(country_id))
        countryListeningUA = np.array([[0] * len(country_id)] * len(country_id))
        i = 0
        for _, row in ListCountUA.iterrows():
            print("1:", i, "/", len(ListCountUA), end="\r")
            i += 1
            userCountry = country_id[user_iso3[row[self.userCol]]]
            artist = row[self.artistCol]
            artID = artistName_id[artist]
            countryArtistsUA[userCountry][artID] += 1 # Add one for every unique combination
            # If the artist has country information add that to it's own array
            if artist in artistID_iso3.keys():
                artistCode = artistID_iso3[artist]
                if artistCode in country_id.keys():
                    artistCountry = country_id[artistCode]
                    countryListeningUA[userCountry][artistCountry] += 1
        np.save("Results\\countrylisteningUA.npy", countryListeningUA)
        np.save("Results\\countryArtistsUA.npy", countryArtistsUA)


    """
    Creates 2 result matrices based every single listening event and stores them in a .npy file
    Creates 2 result matrices based on every user track combination and stores them in a .npy file
    CountryListening file groups all users and artists into their respective countries
    CountryArtist file only groups all users to their respective countries
    UT: Unique Track
    """
    def createResultMatrix2(self, country_id:dict, user_iso3:dict, artistName_id:dict, artistID_iso3:dict):
        countryArtists = np.array([[0] * len(artistName_id)] * len(country_id))  
        countryArtistsUT = np.array([[0] * len(artistName_id)] * len(country_id))
        countrylistening = np.array([[0] * len(country_id)] * len(country_id))
        countrylisteningUT = np.array([[0] * len(country_id)] * len(country_id))
        i = 0
        for _, row in self.df.iterrows():
            print("2:", i, "/", len(self.df), end="\r")
            country = country_id[user_iso3[row[self.userCol]]]
            artist = row[self.artistCol]
            aid = artistName_id[artist]
            countryArtists[country][aid] += row[self.totalCountCol] # Add count to get actual listening counts
            countryArtistsUT[country][aid] += 1 # Add one for every unique combination 
            if artist in artistID_iso3.keys():
                artistCode = artistID_iso3[artist]
                if artistCode in country_id.keys():
                    artistCountry = country_id[artistCode]
                    countrylistening[country][artistCountry] += row[self.totalCountCol]
                    countrylisteningUT[country][artistCountry] += 1
            i += 1
        np.save("Results\\countryArtists.npy", countryArtists)
        np.save("Results\\countryArtistsUT.npy", countryArtistsUT)
        np.save("Results\\countrylistening.npy", countrylistening)
        np.save("Results\\countrylisteningUT.npy", countrylisteningUT)




if __name__ == "__main__":
    convs = Converters()
    convs.create_iso2_iso3("Data\\CountryInfo.csv", "alpha-2", "alpha-3")
    convs.create_iso3_countryName("Data\\CountryInfo.csv", "alpha-3", "name")

    users = Users()
    users.openFile('LFM-2b\\users.tsv', "user_id", "country")
    users.streamReady(convs.iso2_iso3)
    users.create_user_iso3()
    
    convs.create_iso3_id(users.df[users.countryCol].unique())

    tracks = Tracks()
    tracks.openFile('LFM-2b\\tracks.tsv', "track_id", "artist_name", badLines="skip")
    tracks.create_artistName_tracks()
    tracks.create_artistName_artistID()

    artists = Artists()
    artists.openFile("artists.csv", "artist_mb", "country_mb", "country_lastfm", lowMemory=False)
    artists.checkCountries(0)
    artists.convertCountryName_iso3(convs.countryName_iso3)
    artists.mapArtistId(tracks.artistName_artistID)
    artists.create_artistID_iso3()
    
    streams = Streams()
    streams.openFile("LFM-2b\\listening-counts.tsv", "user_id", "track_id", countColumn = "count")
    streams.filterUsersTracks(users.df[users.userCol], tracks.df[tracks.trackCol])
    streams.createArtistColumn(tracks.track_artistName)
    
    streams.createResultMatrix(convs.iso3_id, users.user_iso3, tracks.artistName_artistID, artists.artistID_iso3)
    streams.createResultMatrix2(convs.iso3_id, users.user_iso3, tracks.artistName_artistID, artists.artistID_iso3)

    print(streams.df)
    