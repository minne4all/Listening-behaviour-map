import pandas as pd

class Converters:
    def __init__(self) -> None:
        pass

    """
    Function for making simple convertion dictionaries 
    """
    def createConvertionDict(self, df:pd.DataFrame, keyColumn:str, valueColumn:str, bothWays:bool = False):
        dct = {}
        if bothWays:
            revdct = {}
        for _, row in df[[keyColumn, valueColumn]].iterrows():
            dct[row[keyColumn]] = row[valueColumn]
            if bothWays:
                revdct[row[valueColumn]] = row[keyColumn]
        return (dct, revdct) if bothWays else dct
    
    """
    Creates dictionaries for converting: alpha-iso2 codes <-> alpha-iso3 codes
    """
    def create_iso2_iso3(self, file:str, iso2Column:str, iso3Column:str) -> None:
        df = pd.read_csv(file)
        self.iso2_iso3 = self.createConvertionDict(df, iso2Column, iso3Column)

    """
    Gives every country an id and creates dictionaries for converting: country id <-> alpha-iso3 code
    """
    def create_iso3_id(self, countryList:list) -> None:
        self.iso3_id = {}
        self.id_iso3 = {}
        for id, country in enumerate(countryList):
            self.iso3_id[country] = id
            self.id_iso3[id] = country
    
    def create_iso3_countryName(self, file:str, iso3Column:str, countryNameColumn:str) -> None:
        df = pd.read_csv(file)
        self.iso3_countryName, self.countryName_iso3 = self.createConvertionDict(df, iso3Column, countryNameColumn, bothWays=True)