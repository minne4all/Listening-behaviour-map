import plotly.express as px
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output
from dash import dash_table as dt
from RankDifference import RankDifference
from Converters import Converters
from Users import Users
from Artists import Artists

# Loading in all datasets
df = pd.read_csv("Data\\Mapdf.csv")
globaldf = pd.read_csv("Data\\Globaldf.csv")
countryArtistsUT = np.load("Results\\countryArtistsUT.npy")
topGlobal = np.load("Results\\topGlobal.npy")

convs = Converters()
convs.create_iso2_iso3("Data\\CountryInfo.csv", "alpha-2", "alpha-3")
convs.create_iso3_countryName("Data\\CountryInfo.csv", "alpha-3", "name")

users = Users()
users.openFile('LFM-2b\\users.tsv', "user_id", "country")
users.streamReady(convs.iso2_iso3)
users.create_user_iso3()

convs.create_iso3_id(users.df[users.countryCol].unique())

artists = Artists()
artists.loadIDs("Data\\artistId.csv")
artists.openFile("Data\\artists.csv", "artist_mb", "country_mb", "country_lastfm", lowMemory=False)
artists.checkCountries(1)
artists.convertCountryName_iso3(convs.countryName_iso3)
artists.mapArtistId(artists.artistName_artistID)
artists.create_artistID_iso3()

#Dict for making the country options for selected country
countryUserCount = {}
sortedUserCounts = {k: v for k, v in sorted(users.iso3_users.items(), key=lambda item: len(item[1]), reverse=True)}
for iso3, users in sortedUserCounts.items():
    countryUserCount[convs.iso3_countryName[iso3]] = f"{convs.iso3_countryName[iso3]}: {len(users)} users"

#Dict for getting right columns for each measurement. In this case total count is for hover_data and the second is used for deciding the color. 
#Adding more measurements also need to be added to the options of 
popDict = {"T" : ["totalcount", "totalcount_logged"], 
            "UT" : ["uniquetrackcount", "uniquetrackcount_logged"], 
            "RTC" : ["totalcount", "relativetotalcount"]}

app = Dash(__name__)


app.layout = html.Div([
    html.Div([ 
        dcc.Graph(id="graph"),
    ], style={"position" : "absolute", "width" : "98vw"}),
    html.Div([ 
        html.Div([ 
            html.H4('Country listening behaviour'),
            html.Div([
                html.Div([
                    html.P(children=["Top artist for tables:"], style={"margin": "0px"}),
                    dcc.Input(id="Top", type="number", min=1, max=50, step=1, value=10),
                ], style={"display": "flex"}),
                html.P("Select popularity measurement:"),
                dcc.RadioItems(
                id='pop', 
                options= {"T" : "Total listening count", 
                          "UT" : "Unique listener and track combinations", 
                          "RTC" : "Total count divided by country average",
                          "GC" : "Global listening count divided by number of artists"},
                value="T",
                labelStyle={'display': 'block'}
                )
            ]),
            html.Div([
                    html.P("Select a country:"),
                    html.Div([
                        dcc.RadioItems(
                            id='country', 
                            options=countryUserCount,
                            value=next(iter(countryUserCount)),
                            labelStyle={'display': 'block'}
                        )
                    ], style={"overflow-y" : "auto", "overflow-x" : "clip", "max-height" : "80vh"}),
            ])
        ], style={"z-index" : "10", "width" : "19vw", "background" : "white", "height": "100vh"}),
        html.Div([
            html.P(id="mainstreamtitle", style={"position" : "relative", "left" : "56px", "margin" : "0px"}),
            dcc.Graph(id="mainstream", style={'width': '50vw', 'height': '33vh'})
        ], style={"bottom" : "-2vh", "left" : '22vw', "display" : "flex", "flex-direction" : "column", "position": "absolute"}),
        html.Div([
            dcc.Tabs([
                dcc.Tab(label="Click top", children=[
                    html.Div([
                    html.P("Top artists from clicked on country", style={"position" : "relative", "margin" : "0px", "background" : "white", "padding" : "2px", "max-width" : "17vw"}),
                    html.Div(id="ranking")
                    ])
                ]),
                dcc.Tab(label="Ranked diff", children=[
                    html.Div([
                    html.P("Top artists for selected country based on the ranked difference", style={"position" : "relative", "margin" : "0px", "background" : "white", "padding" : "2px", "max-width" : "17vw"}),
                    html.Div(id="rankedDiff")
                    ])
                ]), 
                dcc.Tab(label="Select top", children=[
                    html.Div([
                    html.P("Top artists for selected country", style={"position" : "relative", "margin" : "0px", "background" : "white", "padding" : "2px", "max-width" : "17vw"}),
                    html.Div(id="Top artists")
                    ])
                ])
            ]),
        ], style={"right" : "0", "top" : "5vh", "overflow-x" : "clip", "width" : "18vw", "z-index": "10", "position": "absolute"})
    ], style={"display": "flex", "justify-content" : "space-between", "align-items" : "flex-end", "height": "100%", "width": "100%", "z-index" : "10"})
])

'''
Callback for changing the input country and popularity measurement for the choropleth
'''
@app.callback(
    Output("graph", "figure"), 
    Input("country", "value"),
    Input("pop", "value"))
def display_choropleth(country, pop):
    if pop == "GC": # Global count is not in popDict, because it needs different dataset.
        dfChoro = globaldf
        dataCol = "Globalcount"
        nameCol = "Countryname"
        hoverCol = ["Totalcount"]
    else:
        dfChoro = df[df["selectcountry"] == country]
        dataCol = popDict[pop][1]
        nameCol = "listencountry"
        hoverCol = [popDict[pop][0]]
    fig = px.choropleth(dfChoro, color=dataCol, 
                        locations="iso",
                        hover_name=nameCol,
                        hover_data=hoverCol,
                        color_continuous_scale="reds")
    fig.update_layout(autosize=False, margin = dict(l=0,r=0,b=0,t=0))
    fig.update_coloraxes(showscale=False)
    return fig

'''
Callback for making the artist ranking for each country by clicking on the country
'''
@app.callback(
    Output("ranking", "children"), 
    [Input('graph', 'clickData')],
    Input("country", "value"),
    Input("Top", "value"))
def make_ranking(clickData, country, top):
    selectcode = convs.countryName_iso3[country]
    selectId = convs.iso3_id[selectcode]
    if clickData == None: # No country was clicked, use selected country
        listencountry = selectcode
        countryArtistsIds = artists.iso3_artistID[selectcode]
    else:
        listencountry = clickData["points"][0]["location"]
        countryArtistsIds = artists.iso3_artistID[listencountry]
    sortArtists = np.argsort(countryArtistsUT[selectId])
    k = 1 # Counts over each artists that gets in the list
    l = 1 # Counts over every artist
    ranks = []
    while k <= top and l < len(countryArtistsUT[selectId]):
        if sortArtists[-l] in countryArtistsIds:
            ranks.append([artists.artistID_artistName[sortArtists[-l]], countryArtistsUT[selectId][sortArtists[-l]]])
            k += 1
        l += 1
    ranksdf = pd.DataFrame(columns=[convs.iso3_countryName[listencountry] + " artists", "Listeners"], data = ranks)
    return dt.DataTable(ranksdf.to_dict('records'), [{"name": i, "id": i} for i in ranksdf.columns],
                        style_data={
                            'whiteSpace': 'normal',
                            'width': 'auto',
                        })

'''
Callback for making the ranked difference for each country
'''
@app.callback(
    Output("rankedDiff", "children"),
    Input("country", "value"),
    Input("Top", "value"))
def make_rankedDiff(country, top):
    selectcode = convs.countryName_iso3[country]
    selectId = convs.iso3_id[selectcode]
    length = 1000
    globallist = list(topGlobal[:length])
    countrylist = list(np.argsort(countryArtistsUT[selectId]))[::-1][:length]
    instance = RankDifference(fileA=globallist, fileB=countrylist, listOnly=False, limit=top)
    rankDiff = instance.computeRankDifference()
    dfdata = [[artists.artistID_artistName[x[0]], countryArtistsUT[selectId][x[0]]] for x in rankDiff]
    rankedDiffdf = pd.DataFrame(columns=["Artists", "Listeners"], data = dfdata)
    return dt.DataTable(rankedDiffdf.to_dict('records'), [{"name": i, "id": i} for i in rankedDiffdf.columns],
                        style_data={
                            'whiteSpace': 'normal',
                            'width': 'auto',
                        })

'''
Callback for making the top artists for the selected country
'''
@app.callback(
    Output("Top artists", "children"),
    Input("country", "value"),
    Input("Top", "value"))
def make_rankedDiff(country, top):
    selectcode = convs.countryName_iso3[country]
    selectId = convs.iso3_id[selectcode]
    sortArtists = np.argsort(countryArtistsUT[selectId])
    ranks = [[artists.artistID_artistName[sortArtists[-x]], countryArtistsUT[selectId][sortArtists[-x]]] for x in range(1, top + 1)]
    ranksdf = pd.DataFrame(columns=["Artists", "Listeners"], data = ranks)
    return dt.DataTable(ranksdf.to_dict('records'), [{"name": i, "id": i} for i in ranksdf.columns],
                        style_data={
                            'whiteSpace': 'normal',
                            'width': 'auto',
                        })


'''
Callback for making the mainstreaminess graph by taking the top 50k global artists and using the selected country's listening data
'''
@app.callback(
    Output("mainstream", "figure"),
    Output("mainstreamtitle", "children"),
    Input("country", "value"))
def mainstream_graph(country):
    countryArtistCount = countryArtistsUT[convs.iso3_id[convs.countryName_iso3[country]]]
    topCount = []
    for idx, artist in enumerate(topGlobal):
        if artists.artistID_artistName[artist] in artists.artistID_iso3.keys():
            topCount.append([idx, countryArtistCount[artist], artists.artistID_artistName[artist], artists.artistID_iso3[artists.artistID_artistName[artist]]])
        else:
            topCount.append([idx, countryArtistCount[artist], artists.artistID_artistName[artist], "N/A"])
    mainstreamdf  = pd.DataFrame(topCount, columns = ['Top artists', 'Listen count', 'Name', "Country"]) 
    fig = px.scatter(mainstreamdf, x="Top artists", y="Listen count", hover_name="Name", color="Country")
    fig.update_layout(  
        autosize=False,
        margin = dict(
            l=0,
            r=0,
            b=0,
            t=0
        )
    )
    title = "Mainstreaminess of " + country
    return fig, title


app.run_server(debug=False)