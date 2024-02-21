import pandas as pd 

class Tracks:
    def __init__(self) -> None:
        pass

    """
    Open CSV file and set the variables for the column names
    """
    def openFile(self, fileName:str, trackColumn:str, artistColumn:str, seperator:str = "\t", badLines:str = "error") -> None:
        self.df = pd.read_csv(fileName, sep=seperator, on_bad_lines= badLines)
        self.df = self.df[[trackColumn, artistColumn]]
        self.df = self.df[self.df[artistColumn].notna()]
        self.trackCol = trackColumn
        self.artistCol = artistColumn

    """
    Gives every artist an ID as well as making dicts to convert the names and ID's 
    """
    def create_artistName_artistID(self) -> None:
        allArtist = self.df[self.artistCol].unique()
        self.artistName_artistID = dict(zip(allArtist, range(len(allArtist))))
        self.artistID_artistName = dict(zip(range(len(allArtist)), allArtist))
        # for id, artist in enumerate(self.df[self.artistCol].unique()):
        #     self.artistName_artistID[artist] = id
        #     self.artistID_artistName[id] = artist

    """
    Creates the dictionaries for converting: ArtistName <-> Tracks
    """
    def create_artistName_tracks(self) -> None:
        self.artistName_tracks = {artist:[] for artist in self.df[self.artistCol].unique()}
        self.track_artistName = {}
        for _, row in self.df.iterrows():
            self.artistName_tracks[row[self.artistCol]] += [row[self.trackCol]]
            self.track_artistName[row[self.trackCol]] = row[self.artistCol]


if __name__ == "__main__":
    tracks = Tracks()
    tracks.openFile('Data\\LFM-2b\\tracks.tsv', "track_id", "artist_name", badLines="skip")
    # tracks.create_artistName_tracks()
    tracks.create_artistName_artistID()
    print(max(tracks.artistID_artistName.keys()), len(tracks.artistID_artistName))