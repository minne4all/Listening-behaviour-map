import numpy as np
import pandas as pd
import pickle

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

# Load in needed datasets and variables from the notebooks
countryListening = np.load("Data\Results\countrylistening.npy")
countryListeningUT = np.load("Data\Results\countrylisteningUT.npy")

with open("Data\Results\countryListeningUA.pkl", "rb") as f:
    countryListeningUA = pickle.load(f)

with open("Data\Results\countryListeningUC.pkl", "rb") as f:
    countryListeningUC = pickle.load(f)

with open("Data\Vars\idCountry.pkl", "rb") as f:
    idCountry = pickle.load(f)

with open("Data\Vars\iso3Country.pkl", "rb") as f:
    iso3Country = pickle.load(f)

with open("Data\Vars\iso3ArtistID.pkl", "rb") as f:
    iso3ArtistID = pickle.load(f)

# Go over all the countrylistenings (country x country) and add their data to each country x country combination
data = []
for idc, row in enumerate(zip(countryListening, countryListeningUT, countryListeningUA, countryListeningUC)):
    scountry = idCountry[idc]
    for i in range(len(row[0])):
        iso = idCountry[i]
        data.append([iso3Country[scountry], iso3Country[iso], iso, row[0][i], row[1][i], row[2][i], row[3][i]])
df = pd.DataFrame(data, columns=["selectcountry", "listencountry", "iso", "totalcount", "uniquetrackcount", "uniqueartistcount", "uniquecountrycount"])

# Use logarithmic transformation to bring values closer together
df['logCountT'] = np.log2(df['totalcount'])
df['logCountUT'] = np.log2(df['uniquetrackcount'])
df['logCountUA'] = np.log2(df['uniqueartistcount'])
df['logCountUC'] = np.log2(df['uniquecountrycount'])

# Get all countries user counts
with open("Data\Vars\countryUsercount.pkl", "rb") as f:
    countryUsercount = pickle.load(f)
countryUsercount = {k:int(v.split(" ")[-2]) for (k,v) in countryUsercount.items()}

totalUsers = sum([countryUsercount[x] for x in countryUsercount.keys()])

# Calculate average listening counts or how many times a country gets listened to
avgdict = {}
for lc in df["listencountry"].unique():
    avg = sum(df[df["listencountry"] == lc]["totalcount"]) / len(df["listencountry"].unique()) 
    avgdict[lc] = avg

# Calculate if a countries listening behaviour towards another country is unique to that specific country
tcavg = []
for idx, row in df.iterrows():
    if avgdict[row["listencountry"]] != 0:
        usercount = countryUsercount[row["selectcountry"]]
        tcavg.append(row["totalcount"] / (avgdict[row["listencountry"]] / usercount))
    else:
        tcavg.append(0)

df["relativetotalcount"] = minmax(tcavg)

# Make dataframe for global listening counts for every country
aggCountry = countryListening.sum(axis=0)
globalcount = []
for i, count in enumerate(aggCountry):
    if idCountry[i] in iso3ArtistID.keys():
        globalcount.append(count / len(iso3ArtistID[idCountry[i]]))
    else:
        globalcount.append(0)

globalData = {"Globalcount" : np.log2(globalcount), 
              "iso" : [idCountry[x] for x in range(len(countryListening))],
              "Countryname" : [iso3Country[idCountry[x]] for x in range(len(countryListening))],
              "Totalcount" : aggCountry}
globaldf = pd.DataFrame(data=globalData)

print(globaldf)
df.to_csv("Dash\Mapdf.csv")
globaldf.to_csv("Dash\Globaldf.csv")
