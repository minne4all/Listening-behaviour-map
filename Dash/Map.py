import plotly.express as px
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import pickle
from dash import dash_table as dt
from rank_difference import RankDifference

# Loading in all datasets
df = pd.read_csv("Dash\\Mapdf.csv")
globaldf = pd.read_csv("Dash\\Globaldf.csv")
countryArtistsUT = np.load("Data\\Results\\countryArtistsUT.npy")
topGlobal = np.load("Data\\Results\\topGlobal.npy")

# Loading in all needed variables from the notebooks
with open("Data\\Vars\\countryISO3.pkl", "rb") as f:
    countryISO3 = pickle.load(f)

with open("Data\\Vars\\iso3Country.pkl", "rb") as f:
    iso3Country = pickle.load(f)

with open("Data\\Vars\\iso3ArtistID.pkl", "rb") as f:
    iso3ArtistID = pickle.load(f)

with open("Data\\Vars\\countryID.pkl", "rb") as f:
    countryID = pickle.load(f)

with open("Data\\Vars\\idArtist.pkl", "rb") as f:
    idArtist = pickle.load(f)

with open("Data\\Vars\\countryUsercount.pkl", "rb") as f:
    countryUsercount = pickle.load(f)

with open("Data\\Vars\\artistISO3.pkl", "rb") as f:
    artistISO3 = pickle.load(f)

# Used for getting right info for choropleth options
datadict = {"T" : ["totalcount", "logCountT"], 
            "UT" : ["uniquetrackcount", "logCountUT"], 
            "UA" : ["uniqueartistcount","logCountUA"], 
            "UC" : ["uniquecountrycount", "logCountUC"],
            "RTC" : ["relativetotalcount", "relativetotalcount"]}


app = Dash(__name__)


app.layout = html.Div([
    html.Div([ 
        dcc.Graph(id="graph"),
    ], style={"position" : "absolute", "width" : "100vw"}),
    html.Div([ 
        html.Div([ 
            html.H4('Country listening behaviour'),
            html.Div([
                html.P("Select popularity measurement:"),
                dcc.RadioItems(
                id='pop', 
                options= {"T" : "Total listening count", 
                          "UT" : "Unique listener and track combinations", 
                          "UA" : "Unique listener and artist combinations", 
                          "UC" : "Unique listener and country combinations",
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
                            options=countryUsercount,
                            value="United States",
                            labelStyle={'display': 'block'}
                        )
                    ], style={"overflow-y" : "auto", "overflow-x" : "clip", "max-height" : "80vh"}),
            ])
        ], style={"z-index" : "10", "width" : "20vw", "background" : "white", "height": "100vh"}),
        html.Div([
            html.P(id="mainstreamtitle", style={"position" : "relative", "left" : "56px", "margin" : "0px"}),
            dcc.Graph(id="mainstream", style={'width': '50vw', 'height': '33vh'})
        ], style={"bottom" : "0px", "left" : '22vw', "display" : "flex", "flex-direction" : "column"}),
        html.Div([
            html.Div([
                html.P("Top artists from clicked on country", style={"position" : "relative", "margin" : "0px", "background" : "white", "padding" : "2px", "max-width" : "17vw"}),
                html.Div(id="ranking")
            ]), 
            html.Div([
                html.P("Top artists for selected country based on the ranked difference", style={"position" : "relative", "margin" : "0px", "background" : "white", "padding" : "2px", "max-width" : "17vw"}),
                html.Div(id="rankedDiff")
            ])
        ], style={"right" : "0", "bottom" : "15vh", "overflow-x" : "clip", "width" : "auto"})
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
    if pop == "GC":
        dfc = globaldf
        colorCol = "Globalcount"
        nameCol = "Countryname"
        hoverCol = ["Totalcount"]
    else:
        dfc = df[df["selectcountry"] == country]
        colorCol = datadict[pop][1]
        nameCol = "listencountry"
        hoverCol = [datadict[pop][0]]
    fig = px.choropleth(dfc, color=colorCol, 
                        locations="iso",
                        hover_name=nameCol,
                        hover_data=hoverCol,
                        color_continuous_scale="reds")
    fig.update_layout(
        autosize=False,
        margin = dict(
            l=0,
            r=0,
            b=0,
            t=0
        )
    )
    fig.update_coloraxes(showscale=False)

    return fig

'''
Callback for making the artist ranking for each country by clicking on the country
'''
@app.callback(
    Output("ranking", "children"), 
    [Input('graph', 'clickData')],
    Input("country", "value"))
def make_ranking(clickData, country):
    selectcode = countryISO3[country]
    i = countryID[selectcode]
    if clickData == None: # No country was clicked, use selected country
        listencountry = selectcode
        cArtists = iso3ArtistID[selectcode]
    else:
        listencountry = clickData["points"][0]["location"]
        cArtists = iso3ArtistID[listencountry]
    sortArtists = np.argsort(countryArtistsUT[i])
    k = 1 # Counts over each artists that gets in the list
    l = 1 # Counts over every artist
    ranks = []
    while k <= 10 and l < len(countryArtistsUT[i]):
        if sortArtists[-l] in cArtists:
            ranks.append([idArtist[sortArtists[-l]], countryArtistsUT[i][sortArtists[-l]]])
            k += 1
        l += 1
    ranksdf = pd.DataFrame(columns=[iso3Country[listencountry] + " artists", "Listeners"], data = ranks)
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
    Input("country", "value"))
def make_rankedDiff(country):
    selectcode = countryISO3[country]
    i = countryID[selectcode]
    length = 1000
    globallist = list(topGlobal[:length])
    countrylist = list(np.argsort(countryArtistsUT[i]))[::-1][:length]
    instance = RankDifference(fileA=globallist, fileB=countrylist, listOnly=False, limit=10)
    rankDiff = instance.computeRankDifference()
    dfdata = [[idArtist[x[0]], countryArtistsUT[i][x[0]]] for x in rankDiff]
    rankedDiffdf = pd.DataFrame(columns=["Artists", "Listeners"], data = dfdata)
    return dt.DataTable(rankedDiffdf.to_dict('records'), [{"name": i, "id": i} for i in rankedDiffdf.columns],
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
    countryArtistCount = countryArtistsUT[countryID[countryISO3[country]]]
    topCount = []
    for idx, artist in enumerate(topGlobal):
        if idArtist[artist] in artistISO3.keys():
            topCount.append([idx, countryArtistCount[artist], idArtist[artist], artistISO3[idArtist[artist]]])
        else:
            topCount.append([idx, countryArtistCount[artist], idArtist[artist], "N/A"])
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


app.run_server(debug=True)