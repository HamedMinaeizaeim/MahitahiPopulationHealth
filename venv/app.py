import json
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import matplotlib
import matplotlib.cm as cm
import plotly.graph_objs as go
import os
import random
from SQLDataFetching import SQLDataFetching
import time
from datetime import datetime
import pandas as pd
import copy
import numpy as np

mapbox_key = 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2oyY2M4YW55MDF1YjMzbzhmemIzb290NiJ9.sT6pncHLXLgytVEj21q43A'
if not mapbox_key:
    raise RuntimeError("Mapbox key not specified! Edit this file and add it.")


FullPathJson = ('https://github.com/HamedMinaeizaeim/MahitahiPopulationHealth/blob/Test/venv/AU_RC_Northland_RegionCorrectFile.json')
# FullPathJson
lep_df = gpd.read_file(FullPathJson)
Test = lep_df.head(1)

lep_df['LON'] = lep_df['geometry'].centroid.x
lep_df['LAT'] = lep_df['geometry'].centroid.y

lon = lep_df['LON'][0]
lat = lep_df['LAT'][0]

lengthdata = lep_df['LON'].count()
# global lep_df, FullPath
overlay_choiceMempory = 'Smoking'

# Copy the lep_df for creating mapforsocialEconomic Status
SocialEconmic_df = copy.deepcopy(lep_df)


def ImportDataFrameFROMCSV(overlay_choice='Smoking'):
    fullPathcsv = 'https://github.com/HamedMinaeizaeim/MahitahiPopulationHealth/blob/Test/venv/'+str(overlay_choice) + '.csv'
    DiseasData = pd.read_csv(fullPathcsv)
    DiseasData['Quarter_Start_Date'] = pd.to_datetime(DiseasData['Quarter_Start_Date'], dayfirst=True)
    DiseasData['Quarter_Start_Date'] = DiseasData['Quarter_Start_Date'].dt.date
    DiseasData['Quarter_Start_Date'] = DiseasData['Quarter_Start_Date'].astype(str)
    DiseasData = DiseasData[DiseasData['Quarter_Start_Date'] > '2015-01-01']
    DiseasData.set_index('Quarter_Start_Date', inplace=True)

    column = DiseasData.columns.tolist()
    #    print len(column)
    for i in range(0, len(column)):
        column[i] = unicode(column[i], "utf-8")
    DiseasData.columns = column

    column2 = DiseasData.columns.tolist()
    return DiseasData


def ComputeDate(overlay_choice):
    DiseasData = ImportDataFrameFROMCSV(overlay_choice)
    Date = DiseasData.index.tolist()
    return Date

    # return DiseasData


def valuesforMap(lep_df, year_slider, overlay_choice='Smoking'):
    DiseasData = ImportDataFrameFROMCSV(overlay_choice)
    Date = DiseasData.index.tolist()

    for index in lep_df.index:
        Name = lep_df.loc[(index), 'AU_NAME']
        columnName = Name + 'Total'
        FixedIndex = year_slider
        IndexList = DiseasData.index.tolist()
        A = IndexList[0]
        print type(IndexList[0])
        lep_df.loc[index, 'NUM_LEP'] = DiseasData.loc[FixedIndex, columnName]

    lep_dfFilter = lep_df.dropna(subset=['NUM_LEP'])
    return lep_dfFilter


def ReadScocialTable(fullPath):
    return pd.read_csv(fullPath)


def ValuesforSocialMap(SocialEconmic_df, Choice='Deprivation Index'):
    fullPath = 'https://github.com/HamedMinaeizaeim/MahitahiPopulationHealth/blob/Test/venv/SocialEconomicTable.csv'
    SocialEconomicTable = pd.read_csv(fullPath)
    SocialEconomicTable.set_index('Name', inplace=True)

    for index in SocialEconmic_df.index:
        Name = SocialEconmic_df.loc[index, 'AU_NAME']
        SocialEconmic_df.loc[index, 'NUM_LEP'] = SocialEconomicTable.loc[Name, Choice]
    SocialEconmic_dfFilter = SocialEconmic_df.dropna(subset=['NUM_LEP'])
    return SocialEconmic_dfFilter


SocialEconomicTable = ReadScocialTable(
    'https://github.com/HamedMinaeizaeim/MahitahiPopulationHealth/blob/Test/venv/SocialEconomicTable.csv')
lep_dfFilter = valuesforMap(lep_df, year_slider='2018-10-01', overlay_choice='Smoking')
SocialEconmic_dfFilter = ValuesforSocialMap(SocialEconmic_df, Choice='Deprivation Index')

overlay_choice = 'Smoking'
lep_df['NUM_LEP'].fillna(0, inplace=True)
lep_df['HOVER'] = 'Area unit name: ' + lep_df.AU_NAME + \
                  '<br /> percentage of ' + overlay_choice + ' ' + lep_df.NUM_LEP.astype(int).astype(str) + "%"

Choice = 'Deprivation Index'
SocialEconmic_df['NUM_LEP'].fillna(0, inplace=True)
SocialEconmic_df['HOVER'] = 'Area unit name: ' + lep_df.AU_NAME + \
                            '<br />' + Choice + ' ' + lep_df.NUM_LEP.astype(int).astype(str) + "%"

mcolors = matplotlib.colors


def set_overlay_colors(dataset):
    """Create overlay colors based on values

    :param dataset: gpd.Series, array of values to map colors to

    :returns: dict, hex color value for each language or index value
    """
    minima = dataset.min()
    maxima = dataset.max()
    norm = mcolors.Normalize(vmin=minima, vmax=maxima, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.viridis)
    colors = [mcolors.to_hex(mapper.to_rgba(v)) for v in dataset]

    overlay_color = {
        idx: shade
        for idx, shade in zip(dataset.index, colors)
    }

    return overlay_color


def set_colors_Scale(dataset):
    """Create overlay colors based on values

    :param dataset: gpd.Series, array of values to map colors to

    :returns: dict, hex color value for each language or index value
    """

    dataset = dataset.sort_values(ascending=True)
    minima = dataset.min()
    maxima = dataset.max()
    databetween = np.linspace(minima, maxima, 10)
    RelativeValue = np.linspace(0, 1, 10)
    norm = mcolors.Normalize(vmin=minima, vmax=maxima, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.viridis)

    w, h = 2, len(databetween)
    colorscale = [[0 for x in range(w)] for y in range(h)]

    for i in range(0, len(databetween)):
        colorsmaxArray = [mcolors.to_rgb(mapper.to_rgba(databetween[i]))]
        colorsmaxArray = colorsmaxArray[0]
        colorsmaxArray = tuple(map(lambda x: x * 255, colorsmaxArray))
        colorsmax = 'rgb(' + str(int(colorsmaxArray[0])) + ',' + str(int(colorsmaxArray[1])) + ',' + str(
            int(colorsmaxArray[2])) + ')'
        colorscale[i][0] = RelativeValue[i]
        colorscale[i][1] = colorsmax

    return colorscale


abnomalityList = ['Smoking', 'DAR', 'Diabetes', 'Stroke', 'Myocardial_Infarction', \
                  'Heart_Failure', 'CVDRA']
opts = [{'label': abnormality, 'value': abnormality} for abnormality in abnomalityList]

SocialList = ['Deprivation Index', 'Median family income',
              'Precentage of Family with No Access to Telecommunication Systems',
              'Precentage of Family with No Access to CellPhone', 'Precentage of Family with No Access to TelePhone',
              'Precentage of Family with No Access to Internet',
              'Precentage of Family with No Motor Vehicle', 'Precentage of People with No Qualification',
              'Precentage of People with Below Deploma Qualification',
              'Precentage of People with Diploma Qualification',
              'Precentage of People with Bachelor Degree', 'Precentage of People with Postgraduate Degree',
              'Precentage of People employed Full time', 'Precentage of People employed Part time',
              'Precentage of People Unemployed']

optsSocial = [{'label': Social, 'value': Social} for Social in SocialList]
# opts.append(all_opt)


map_layout = {
    'data': [{
        'lon': lep_df['LON'],
        'lat': lep_df['LAT'],
        'mode': 'markers',
        'marker': {
            'opacity': 0.8,

            'colorbar': dict(
                thicknessmode="fraction",
                title="Time of<br>Day",
                x=0.935,
                xpad=0,
                nticks=24,
                tickfont=dict(
                    color='white'
                ),
                titlefont=dict(
                    color='white'
                ),
                titleside='left'
            ),
        },
        'type': 'scattermapbox',
        'name': 'Portland LEP',
        'text': lep_df['HOVER'],
        'hoverinfo': 'text',
        'anotation': [dict(
            showarrow=True,
            align='right',
            text='<b>Test1<br>Test2</b>',
            x=0.95,
            y=0.95,
        )],
        'showlegend': False,
    }],
    'layout': {
        'autosize': True,
        'hovermode': 'closest',
        'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0},
        'mapbox': {
            'accesstoken': mapbox_key,
            'center': {
                'lat': lat,
                'lon': lon
            },
            'zoom': 6.0,
            'bearing': 0.0,
            'pitch': 0.0,
        },
    }
}

map_layoutSocial = {
    'title': 'Portland LEP',
    'data': [{
        'lon': SocialEconmic_df['LON'],
        'lat': SocialEconmic_df['LAT'],
        'mode': 'markers',
        'marker': {
            'opacity': 0.0,
        },
        'type': 'scattermapbox',
        'text': SocialEconmic_df['HOVER'],
        'hoverinfo': 'text',
        'showlegend': True,
    }],
    'layout': {
        'autosize': True,
        'hovermode': 'closest',
        'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0},
        'anotation': [],
        'mapbox': {
            'accesstoken': mapbox_key,
            'center': {
                'lat': lat,
                'lon': lon
            },
            'zoom': 6.0,
            'bearing': 0.0,
            'pitch': 0.0,

        },
    }
}

app = dash.Dash()
app.config['suppress_callback_exceptions'] = True
Date = ComputeDate(overlay_choice)
Dates = sorted(Date, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
Dates = pd.to_datetime(Dates)
epoch = datetime.fromtimestamp(0)


def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int((dt - epoch).total_seconds())
    # return int(time.mktime(dt.timetuple()))-int(epoch)


def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix, unit='s')


def getMarks(start, end, Dates):
    ''' Returns the marks for labeling.
        Every Nth value will be used.
    '''

    result = {}
    for i, Onedate in enumerate(Dates):
        # Append value to dict
        # date = datetime.strptime(date, '%Y-%m-%d')
        result[unixTimeMillis(Onedate)] = str(Onedate.strftime('%Y-%m'))

    return result


app.layout = html.Div([

    html.Div(
        [
            html.H1(children='Percentage of diseases in each area'),
            dcc.Dropdown(
                id='overlay-choice',
                options=opts,
                value='Smoking'
            )
        ],
        style={'width': '48%', 'display': 'inline-block', 'textAlign': 'center', 'padding': 10}
    ),
    html.Div(
        [
            html.H1(children='Socioeconomic status for each statues'),
            dcc.Dropdown(
                id='SocialDropDown',
                options=optsSocial,
                value='Deprivation Index'
            )
        ],
        style={'width': '48%', 'display': 'inline-block', 'textAlign': 'center', 'padding': 10}
    ),

    html.Div([
        dcc.Graph(id='map-display', hoverData={u'points': [{u'curveNumber': 0,
                                                            u'text': u'Area unit name: Karikari Peninsula-Maungataniw<br /> percentage of Diabetes 5%',
                                                            u'pointNumber': 30, u'lon': 173.44121481150123,
                                                            u'pointIndex': 30, u'lat': -35.0545956157133}]}),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': 10}),
    html.Div([
        dcc.Graph(id='map-social', hoverData={u'points': [{u'curveNumber': 0,
                                                           u'text': u'Area unit name: Karikari Peninsula-Maungataniw<br /> percentage of Diabetes 5%',
                                                           u'pointNumber': 30, u'lon': 173.44121481150123,
                                                           u'pointIndex': 30, u'lat': -35.0545956157133}]}),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': 10}),

    html.Div([
        html.Label('Diseases in each quarter'),
        dcc.Slider(
            id='year-slider',
            min=unixTimeMillis(min(Dates)),
            max=unixTimeMillis(max(Dates)),
            value=unixTimeMillis((Dates[1])),
            marks=getMarks(min(Dates), max(Dates), Dates)
        ),
    ], style={'padding': 10},
    ),

    html.Div(children=[
        html.Div(
            dcc.Graph(id='BarGraph-Area'), style={'width': '28%', 'display': 'inline-block', 'padding': 10}),
        html.Div(
            dcc.Graph(id='PieCahrt-Maori'), style={'width': '28%', 'display': 'inline-block', 'padding': 10}),
        html.Div(
            dcc.Graph(id='PieCahrt-Male'), style={'width': '28%', 'display': 'inline-block', 'padding': 10})]),

    html.Div([
        dcc.Graph(id='BarGarph')], style={'padding': 10}),

    # Hidden div inside the app that stores the intermediate value

    # Hidden div inside the app that stores the intermediate value
    html.Div(id='def_lefFilter-value', style={'display': 'none'}),
    html.Div(id='Diseas-value', style={'display': 'none'}),
    html.Div(id='SocialEconomic-Value', style={'display': 'none'}),
    html.Div(id='Pi-Chart-Maori', style={'display': 'none'}),
    html.Div(id='Pi-Chart-Male', style={'display': 'none'})
])


# Hidden value for Diseases
@app.callback(
    dash.dependencies.Output('Diseas-value', 'children'),
    [dash.dependencies.Input('overlay-choice', 'value')])
def UpdateDiseases(overlay_choice):
    fullPathcsv = 'https://github.com/HamedMinaeizaeim/MahitahiPopulationHealth/blob/Test/venv/'+str(overlay_choice) + '.csv'
    DiseasData = pd.read_csv(fullPathcsv)
    DiseasData['Quarter_Start_Date'] = pd.to_datetime(DiseasData['Quarter_Start_Date'], dayfirst=True)
    DiseasData['Quarter_Start_Date'] = DiseasData['Quarter_Start_Date'].dt.date
    DiseasData['Quarter_Start_Date'] = DiseasData['Quarter_Start_Date'].astype(str)
    # DiseasData.set_index('Quarter_Start_Date', inplace=True)
    DiseasData = DiseasData[DiseasData['Quarter_Start_Date'] > '2015-01-01']
    column = DiseasData.columns.tolist()
    # print len(column)
    for i in range(0, len(column)):
        column[i] = unicode(column[i], "utf-8")
    DiseasData.columns = column
    return DiseasData.to_json(date_format='iso', orient='split')


# Hidden value for lep_deffilter
@app.callback(
    dash.dependencies.Output('def_lefFilter-value', 'children'),
    [dash.dependencies.Input('Diseas-value', 'children'),
     dash.dependencies.Input('overlay-choice', 'value'),
     dash.dependencies.Input('year-slider', 'value')
     ])
def UpdateThelep_defFilter(DiseasDatajason, overlay_choice, year_slider):
    DiseasData = pd.read_json(DiseasDatajason, orient='split')
    DiseasData.set_index('Quarter_Start_Date', inplace=True)
    month = int(datetime.fromtimestamp(year_slider).strftime('%m'))
    year = datetime.fromtimestamp(year_slider).strftime('%Y')
    if month == 9 or month == 11 or month == 10:
        month = str(10)
    elif month == 12 or month == 2 or month == 1:
        month = "0" + str(1)
    elif month == 3 or month == 5 or month == 4:
        month = "0" + str(4)
    elif month == 06 or month == 8 or month == 7:
        month = "0" + str(7)
    year_slider = year + "-" + (month) + "-01"

    Date = DiseasData.index.tolist()

    for index in lep_df.index:
        # print "index is "+str(index)+"\n"
        Name = lep_df.loc[(index), 'AU_NAME']
        columnName = Name + 'Total'
        FixedIndex = year_slider

        lep_df.loc[index, 'NUM_LEP'] = DiseasData.loc[FixedIndex, columnName]

    lep_dfFilter = lep_df.dropna(subset=['NUM_LEP'])
    print "Hidden lep_dfFilter has run"
    return lep_dfFilter.to_json()


# Social Ecnomic Table
@app.callback(
    dash.dependencies.Output('map-social', 'figure'),
    [dash.dependencies.Input('SocialDropDown', 'value')
     ])
def update_mapSocial(SocialDropDown):
    tmpSocial = map_layoutSocial.copy()
    lep_dfFilterSocial = ValuesforSocialMap(SocialEconmic_df, SocialDropDown)
    colors = set_overlay_colors(lep_dfFilterSocial.NUM_LEP)
    colorscaleSocial = set_colors_Scale(lep_dfFilterSocial.NUM_LEP)

    # Create a layer for each region colored by LEP value
    layers = [{
        'name': SocialDropDown,
        'source': json.loads(lep_dfFilterSocial.loc[lep_dfFilterSocial.index == i, :].to_json()),
        'sourcetype': 'geojson',
        'type': 'fill',
        'opacity': 1.0,
        'color': colors[i]
    } for i in lep_dfFilterSocial.index]

    data = [{
        'lon': lep_dfFilterSocial['LON'],
        'lat': lep_dfFilterSocial['LAT'],
        'mode': 'markers',
        'marker': {
            'opacity': 0.8,
            'reversescale': False,
            'autocolorscale': False,
            'colorscale': colorscaleSocial,
            'cmin': lep_dfFilterSocial['NUM_LEP'].min(),
            'color': lep_dfFilterSocial['NUM_LEP'],
            'cmax': lep_dfFilterSocial['NUM_LEP'].max(),
            'colorbar': dict(
                thicknessmode="fraction",
                title=dict(text=SocialDropDown,
                           side='right'),
                x=0.1,
                xanchor='right',
                xpad=0,
                nticks=24,
                tickfont=dict(
                    color='black'
                ),
                titlefont=dict(
                    color='black'
                ),
                titleside='black'
            ),
        },

        'type': 'scattermapbox',
        'text': lep_dfFilterSocial['HOVER'],
        'hoverinfo': 'text',
        'showlegend': False,
    }]
    lep_dfFilterSocial['NUM_LEP'].fillna(0, inplace=True)
    tmpSocial['data'][0]['text'] = 'Area unit name: ' + lep_dfFilterSocial.AU_NAME + \
                                   '<br /> ' + SocialDropDown + '<br /> ' + lep_dfFilterSocial.NUM_LEP.astype(
        int).astype(str) + "%"

    tmpSocial['data'] = data
    tmpSocial['data'][0]['text'] = 'Area unit name: ' + lep_dfFilterSocial.AU_NAME + \
                                   '<br /> ' + SocialDropDown + '<br /> ' + lep_dfFilterSocial.NUM_LEP.astype(
        int).astype(str)
    tmpSocial['layout']['mapbox']['layers'] = layers

    return tmpSocial


# Diseases map CallBack
@app.callback(
    dash.dependencies.Output('map-display', 'figure'),
    [dash.dependencies.Input('def_lefFilter-value', 'children'),
     dash.dependencies.Input('overlay-choice', 'value')
     ])
def update_map(lep_dfFilterjason, overlay_choice):
    tmp = map_layout.copy()
    lep_dfFilter = gpd.read_file(lep_dfFilterjason)

    colors = set_overlay_colors(lep_dfFilter.NUM_LEP)
    colorscale = set_colors_Scale(lep_dfFilter.NUM_LEP)
    lep_dfFilter['NUM_LEP'].fillna(0, inplace=True)

    # Create a layer for each region colored by LEP value
    layers = [{
        'name': overlay_choice,
        'source': json.loads(lep_dfFilter.loc[lep_dfFilter.index == i, :].to_json()),
        'sourcetype': 'geojson',
        'type': 'fill',
        'opacity': 1.0,
        'color': colors[i]
    } for i in lep_dfFilter.index]

    data = [{
        'lon': lep_dfFilter['LON'],
        'lat': lep_dfFilter['LAT'],
        'mode': 'markers',
        'marker': {
            'opacity': 0.8,
            'reversescale': False,
            'autocolorscale': False,
            'colorscale': colorscale,
            'cmin': lep_dfFilter['NUM_LEP'].min(),
            'color': lep_dfFilter['NUM_LEP'],
            'cmax': lep_dfFilter['NUM_LEP'].max(),
            'colorbar': dict(
                thicknessmode="fraction",
                title=dict(text="Percentage of " + overlay_choice,
                           side='right'),
                x=0.1,
                xanchor='right',
                xpad=0,
                nticks=24,
                tickfont=dict(
                    color='black'
                ),
                titlefont=dict(
                    color='black'
                ),
                titleside='left'
            ),
        },

        'type': 'scattermapbox',
        'name': 'Portland LEP',
        'text': lep_dfFilter['HOVER'],
        'hoverinfo': 'text',
        'showlegend': False,
    }]

    tmp['data'] = data
    #    print "................................"
    tmp['data'][0]['text'] = 'Area unit name: ' + lep_dfFilter.AU_NAME + \
                             '<br /> percentage of ' + overlay_choice + ' ' + lep_dfFilter.NUM_LEP.astype(int).astype(
        str) + "%"
    tmp['layout']['mapbox']['layers'] = layers
    return tmp


# End update_map()

@app.callback(
    dash.dependencies.Output('BarGarph', 'figure'),
    [dash.dependencies.Input('def_lefFilter-value', 'children'),
     dash.dependencies.Input('overlay-choice', 'value')])
def update_graph(lep_dfFilterjason, overlay_choice):
    lep_dfFilter = gpd.read_file(lep_dfFilterjason)
    trace1 = go.Bar(x=lep_dfFilter.AU_NAME, y=lep_dfFilter[('NUM_LEP')], name=overlay_choice)
    return {
        'data': [trace1],
        'layout':
            go.Layout(
                title='Percentage of ' + overlay_choice + "for all areas",
                barmode='stack',
                yaxis=dict(
                    title='Percentage of ' + overlay_choice,
                    titlefont=dict(
                        size=18,
                        color='Black'
                    ),
                    showticklabels=True,
                )

            )
    }


@app.callback(
    dash.dependencies.Output('BarGraph-Area', 'figure'),
    [dash.dependencies.Input('map-display', 'hoverData'),
     dash.dependencies.Input('Diseas-value', 'children'),
     dash.dependencies.Input('overlay-choice', 'value')
     ])
def update_graph(hoverData, DiseasDataJason, overlay_choice):
    # print "History of data is running\n"
    DiseasData = pd.read_json(DiseasDataJason, orient='split')
    DiseasData.set_index('Quarter_Start_Date', inplace=True)
    # print hoverData
    TotalName = hoverData['points'][0]['text']
    Name = TotalName[TotalName.find(": ") + 2:TotalName.find("<br /> ")]
    # print "Name is: "+Name+"\n"
    # DiseasData = ImportDataFrameFROMCSV(overlay_choice)
    DiseasDataSorted = DiseasData.sort_index()
    data = DiseasDataSorted.loc[:, Name + 'Total']
    #    print "list is: "+DiseasDataSorted.index.values.tolist()+'\n'
    trace1 = go.Bar(x=DiseasDataSorted.index.values.tolist(), y=DiseasDataSorted.loc[:, Name + 'Total'],
                    name=overlay_choice)
    return {
        'data': [trace1],
        'layout':
            go.Layout(
                title='percentage of ' + overlay_choice + ' over time',
                barmode='stack',
                xaxis=dict(
                    title='Quarter',
                    titlefont=dict(
                        size=18,
                        color='Black'
                    ),
                    showticklabels=True,
                ),
                yaxis=dict(
                    title='Percentage of ' + overlay_choice,
                    titlefont=dict(
                        size=18,
                        color='Black'
                    ),
                    showticklabels=True,
                )
            )
    }


@app.callback(
    dash.dependencies.Output('Pi-Chart-Maori', 'children'),
    [dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('Diseas-value', 'children'),
     dash.dependencies.Input('map-display', 'hoverData')
     ])
def ClaenDataMaori(year_slider, DiseasDataJason, hoverData):
    # print "Pi chart maori non maori running\n"
    DiseasData = pd.read_json(DiseasDataJason, orient='split')
    DiseasData.set_index('Quarter_Start_Date', inplace=True)
    # lep_dfFilter = gpd.read_file(lep_dfFilterJason)
    tmp = map_layout.copy()
    month = int(datetime.fromtimestamp(year_slider).strftime('%m'))
    year = datetime.fromtimestamp(year_slider).strftime('%Y')
    if month == 9 or month == 11 or month == 10:
        month = str(10)
    elif month == 12 or month == 2 or month == 1:
        month = "0" + str(1)
    elif month == 3 or month == 5 or month == 4:
        month = "0" + str(4)
    elif month == 06 or month == 8 or month == 7:
        month = "0" + str(7)
    year_slider = year + "-" + (month) + "-01"

    # dataset = lep_dfFilter
    # print hoverData
    TotalName = hoverData['points'][0]['text']
    Name = TotalName[TotalName.find(": ") + 2:TotalName.find("<br /> ")]
    DiseasDataSorted = DiseasData.sort_index()
    dataMaori = DiseasDataSorted.loc[year_slider, Name + 'Maori']
    dataM = {'Maori': [dataMaori]}
    df = pd.DataFrame(dataM)
    return df.to_json(date_format='iso', orient='split')


# this is used for PI chart updating
@app.callback(
    dash.dependencies.Output('PieCahrt-Maori', 'figure'),
    [dash.dependencies.Input('map-display', 'hoverData'),
     dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('Pi-Chart-Maori', 'children')
     ])
def update_graph(hoverData, year_slider, PiChartData):
    PiChartData = pd.read_json(PiChartData, orient='split')
    dataMaori = PiChartData.iloc[0, 0]

    labels = ['Maori', 'Non-Maori']
    Totaldata = [dataMaori, 100 - dataMaori]
    # print DiseasDataSorted.index.values.tolist()
    trace1 = go.Pie(labels=labels, values=Totaldata)
    return {
        'data': [trace1],
        'layout':
            go.Layout(
                title='Percentage Maori vs Non maori',
                barmode='stack')
    }


# this is used for PI chart updating
@app.callback(
    dash.dependencies.Output('PieCahrt-Male', 'figure'),
    [dash.dependencies.Input('map-display', 'hoverData'),
     dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('Diseas-value', 'children')

     ])
def update_graph(hoverData, year_slider, DiseasDataJason):
    DiseasData = pd.read_json(DiseasDataJason, orient='split')
    DiseasData.set_index('Quarter_Start_Date', inplace=True)
    # lep_dfFilter = gpd.read_file(lep_dfFilterJason)
    month = int(datetime.fromtimestamp(year_slider).strftime('%m'))
    year = datetime.fromtimestamp(year_slider).strftime('%Y')
    if month == 9 or month == 11 or month == 10:
        month = str(10)
    elif month == 12 or month == 2 or month == 1:
        month = "0" + str(1)
    elif month == 3 or month == 5 or month == 4:
        month = "0" + str(4)
    elif month == 06 or month == 8 or month == 7:
        month = "0" + str(7)
    year_slider = year + "-" + (month) + "-01"

    #  print "Pi chart male -female running\n"
    tmp = map_layout.copy()

    # dataset = lep_dfFilter

    # print hoverData
    TotalName = hoverData['points'][0]['text']
    Name = TotalName[TotalName.find(": ") + 2:TotalName.find("<br /> ")]
    # print Name
    # DiseasData = ImportDataFrameFROMCSV(overlay_choice)
    DiseasDataSorted = DiseasData.sort_index()
    dataMaori = DiseasDataSorted.loc[year_slider, Name + 'Male']
    labels = ['Male', 'FeMale']
    Totaldata = [dataMaori, 100 - dataMaori]
    #  print DiseasDataSorted.index.values.tolist()
    trace1 = go.Pie(labels=labels, values=Totaldata)
    return {
        'data': [trace1],
        'layout':
            go.Layout(
                title='Percentage Male vs FeMale',
                barmode='stack')
    }


if __name__ == '__main__':
    app.run_server(debug=False, port=8051)