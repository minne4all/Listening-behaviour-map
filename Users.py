import pandas as pd
from Converters import Converters

class Users:

    """
    Open CSV file and set the variables for the column names
    """
    def openFile(self, fileName:str, userColumn:str, countryColumn:str, seperator:str = "\t", badLines:str = "error") -> None:
        self.df = pd.read_csv(fileName, sep=seperator, on_bad_lines= badLines)
        self.df = self.df[[userColumn, countryColumn]]
        self.userCol = userColumn
        self.countryCol = countryColumn

    """
    Removes all nana values
    """
    def removeNan(self) -> None:
        self.df = self.df[self.df[self.countryCol].notna()]

    """
    Removes Nan values and converts alpha-iso2 codes to alpha-iso3 codes
    """
    def streamReady(self, isoConverter:dict) -> None:
        self.removeNan()
        self.df[self.countryCol] = self.df[self.countryCol].map(isoConverter)

    """
    Creates dictionaries for converting: user_id <-> alpha-iso3 country codes
    """
    def create_user_iso3(self) -> None:
        self.iso3_users = {}
        self.user_iso3 = {}
        for country in self.df[self.countryCol].unique():
            countrysUsers = self.df[self.df[self.countryCol] == country][self.userCol]
            self.iso3_users[country] = list(countrysUsers)
            for user in countrysUsers:
                self.user_iso3[user] = country
                

if __name__ == "__main__":
    users = Users()
    users.openFile('Data\\LFM-2b\\users.tsv', "user_id", "country")
    convs = Converters()
    convs.create_iso2_iso3("Data\\CountryInfo.csv", "alpha-2", "alpha-3")
    users.streamReady(convs.iso2_iso3)
    users.create_user_iso3()
    print(users.iso3_users)