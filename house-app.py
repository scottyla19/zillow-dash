# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import numpy as np
import plotly.graph_objs as go


app = dash.Dash()
#df= pd.read_csv('http://files.zillowstatic.com/research/public/Zip/Zip_MedianValuePerSqft_AllHomes.csv')

df= pd.read_csv('Zip_MedianValuePerSqft_AllHomes.csv', dtype={'RegionName':str})
dtype_dic= {'ZIP': str,
            'LAT' : np.float64,
            'LNG': np.float64}
zipLatLong = pd.read_csv("ZipLatLong.csv", dtype = dtype_dic)
zipLatLong.rename(columns={'ZIP': 'RegionName'}, inplace=True)
df = pd.merge(df, zipLatLong, on='RegionName', how='left')
lastCol = df.columns[-3]
states = df.State.unique()
states = sorted(states)


colors = ["rgb(0,116,217)","rgb(255,65,54)","rgb(133,20,75)","rgb(255,133,27)","lightgrey"]
mapGroup = df.groupby(['Metro', 'State','RegionName', 'LNG', 'LAT'], as_index = False)[lastCol].mean()
mapGroup.round({lastCol: 2})
mapGroup['text'] = mapGroup['Metro'] + " - " + mapGroup['RegionName'].astype(str) + ' - $' + mapGroup[lastCol].astype(str)
scl = [ [0,"rgb(34, 0, 102)"],[0.35,"rgb(17, 51, 204)"],[0.5,"rgb(51, 221, 0)"],\
    [0.6,"rgb(255, 218, 33)"],[0.7,"rgb(255, 102, 34)"],[1,"rgb(209, 0, 0)"] ]

data = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = mapGroup['LNG'],
        lat = mapGroup['LAT'],
        text = mapGroup['text'],
        mode = 'markers',
        sizemode = 'area',
        marker = dict(
            size =15,
            opacity = 0.5,
            reversescale = False,
            autocolorscale = False,
            symbol = 'circle',
            colorscale = scl,
            cmin = 0,
            color = mapGroup[lastCol],
            cmax = mapGroup[lastCol].quantile(.9),
            colorbar=dict(
                title="Median Price Per Sq. Foot as of " + lastCol
            )
        ))]

layout = dict(
        title = 'Median Price Per Square Foot by Zip Code',
        colorbar = True,
        # autosize=False,
        width=1500,
        # height=500,
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showland = True,
            showcoastlines = True,
            showLakes = True,
            coastlinewidth = 2,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(217, 217, 217)",
            countrycolor = "rgb(217, 217, 217)",
            countrywidth = 2,
            subunitwidth = 2
        ),
    )

fig = dict( data=data, layout=layout )
# scale = 500
#
#
# mapData = go.Scattergeo(
#         locationmode = 'USA-states',
#         lon = mapGroup['LNG'],
#         lat = mapGroup['LAT'],
#         text = mapGroup['Metro'],
#         marker = dict(
#             size = mapGroup[lastCol]/scale,
#             # color = colors[i],
#             line = dict(width=0.5, color='rgb(40,40,40)'),
#             sizemode = 'area'
#         )
#     )
#
# mapLayout = go.Layout(
#     title = '2014 US city populations<br>(Click legend to toggle traces)',
#     showlegend = True,
#     geo = dict(
#         scope='usa',
#         projection=dict( type='albers usa' ),
#         showland = True,
#         landcolor = 'rgb(217, 217, 217)',
#         subunitwidth=1,
#         countrywidth=1,
#         subunitcolor="rgb(255, 255, 255)",
#         countrycolor="rgb(255, 255, 255)"
#     )
#
# )

app.layout = html.Div(children=[
    html.H1(children='Zillow Housing Analysis'),

    dcc.Dropdown(
        id='state-choice',
        options=[{'label': i, 'value': i} for i in states],
        placeholder='Choose your state',
        multi=True
    ),
    dcc.Dropdown(
        id='metro-choice',
        placeholder='Choose your metro area',
        multi=True
    ),
    dcc.Dropdown(
        id='zip-choice',
        placeholder='Choose your zipcode',
        multi=True
    ),
    dcc.Checklist(
        id='showTable',
        options=[
            {'label': 'Show Table', 'value': 'Show'},
        ],
        values=['No']
    ),
    html.Div(id='dt-container', children=[
        dt.DataTable(
            rows=[{}],
            id='datatable',
            filterable=True,
            sortable=True
        )
    ]),

    dcc.Graph(id='map',figure=fig),
    dcc.Graph(id='graph'),
    html.Div(id='timeSeries-container', children=[
        dcc.Graph(id='timeSeries')
    ])

])

# update table on change of all dropdowns
@app.callback(
    Output('datatable', 'rows'),
    [Input('state-choice', 'value'),
    Input('metro-choice', 'value'),
    Input('zip-choice', 'value')])
def state_cb(state, metro, zipcode):
    if zipcode:
        currDF = df[(df['State'].isin(state)) & (df['Metro'].isin(metro)) & (df['RegionName'].isin(zipcode))]
        return currDF.to_dict('records')
    elif metro:
        currDF = df[(df['State'].isin(state)) & (df['Metro'].isin(metro))]
        return currDF.to_dict('records')
    else:
        currDF = df[df['State'].isin(state)]
        return currDF.to_dict('records')

# update metro dropdown on state dropdown choice
@app.callback(
    Output('metro-choice', 'options'),
    [Input('state-choice', 'value')])
def metro_cb(state):
    currDF = df[df['State'].isin(state)]
    currDF.dropna(subset=["Metro"], inplace=True)
    metros = currDF.Metro.unique()
    metros = sorted(metros)
    return [{'label': m, 'value': m} for m in metros]

# Update zipcode dropdown choices on metro change
@app.callback(
    Output('zip-choice', 'options'),
    [Input('state-choice', 'value'),
    Input('metro-choice', 'value')])
def zip_cb(state, metro):
    currDF = df[(df['State'].isin(state)) & (df['Metro'].isin(metro))]
    currDF.dropna(subset=["Metro"], inplace=True)
    zips = currDF.RegionName.unique()
    zips = sorted(zips)
    return [{'label': z, 'value': z} for z in zips]

# show or hide datatable
@app.callback(
    Output('dt-container', 'style'),
    [Input('showTable','values')])
def state_cb(doShowTable):
    if "Show" in doShowTable:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# show or hide timeSeries
@app.callback(
    Output('timeSeries-container', 'style'),
    [Input('zip-choice','value')])
def state_cb(zipChoice):
    if zipChoice:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Create Graph
@app.callback(
    Output('graph', 'figure'),
    [Input('state-choice', 'value'),
    Input('metro-choice', 'value'),
    Input('zip-choice', 'value')])
def update_figure(state, metro, zipcode):
    if metro:
        # currDF = df[(df['State'].isin(state)) & (df['Metro'].isin(metro))]
        # currDF.set_index('RegionName', inplace=True)
        # currDF.drop(currDF.columns[0:6], axis=1, inplace=True)
        # tCurrDF = currDF.transpose()
        # myData = []
        # for c in tCurrDF.columns:
        #     trace0 = go.Box(
        #         y=tCurrDF[c],
        #         name = str(c)
        #     )
        #     myData.append(trace0)
        currDF = df[(df['Metro'].isin(metro)) & (df['State'].isin(state))]

        dfGroup = currDF.groupby(['RegionName', 'Metro', 'City'], as_index = False)[lastCol].mean()
        dfGroup.set_index('RegionName', inplace=True)

        metros = ', '.join(metro)
        myData = []
        for m in metro:
            currGroup = dfGroup[dfGroup['Metro'] == m]
            trace0 = go.Bar(
                x=currGroup.index.values,
                y=currGroup[lastCol],
                name = m,
                text = currGroup['City']
            )
            myData.append(trace0)

        layout = go.Layout(
            xaxis=dict(
                title='Zip Codes',
                type = 'category'
            ),
            yaxis=dict(
                title='Price Per Sq. Foot'
            ),
            title = "Price Per Sq. Foot by Zip Code for " + metros,
            barmode='group'
        )
        return {
            'data':myData,
            'layout':layout
        }


    if state:
        currDF = df[df['State'].isin(state)]

        dfGroup = currDF.groupby(['Metro', 'State'], as_index = False)[lastCol].mean()
        states = ', '.join(state)
        myData = []
        for s in state:
            currGroup = dfGroup[dfGroup['State'] == s]
            trace0 = go.Bar(
                x=currGroup['Metro'],
                y=currGroup[lastCol],
                name = s
            )
            myData.append(trace0)

        layout = go.Layout(
            xaxis=dict(
                title='Metro Area',
                type = 'category'
            ),
            yaxis=dict(
                title='Price Per Sq. Foot'
            ),
            title = "Price Per Sq. Foot by Metropolitan Area for " + states,
            barmode= "group"

        )
        return {
            'data':myData,
            'layout':layout
        }


    dfGroup = df.groupby('State', as_index = False)[lastCol].mean()
    layout = go.Layout(
        xaxis=dict(
            title='State',
            type = 'category'
        ),
        yaxis=dict(
            title='Price Per Sq. Foot'
        ),
        title = "Price Per Sq. Foot by State"

    )
    return {
        'data': [go.Bar(
            x=dfGroup['State'],
            y=dfGroup[lastCol],

        )],
        'layout':layout
    }
@app.callback(
    Output('timeSeries', 'figure'),
    [Input('zip-choice', 'value')])
def update_timeSeries(zipcode):
    currDF = df[(df['RegionName'].isin(zipcode)) ]
    currDF.set_index('RegionName', inplace=True)
    currDF.drop(currDF.columns[0:6], axis=1, inplace=True)
    currDF.drop(currDF.columns[-2:], axis=1, inplace=True)
    tCurrDF = currDF.transpose()

    zips = ', '.join(str(x) for x in zipcode)
    myData = []
    for c in tCurrDF.columns:
        trace0 = go.Scatter(
            x=tCurrDF.index.values,
            y=tCurrDF[c],
            name = str(c)
        )
        myData.append(trace0)
    layout = go.Layout(
        xaxis=dict(
            title='Year-Month',
            type = 'category'
        ),
        yaxis=dict(
            title='Price Per Sq. Foot'
        ),
        title = "Price Per Sq. Foot for " + zips

    )
    return {
        'data':myData,
        'layout':layout
    }


if __name__ == '__main__':
    app.run_server(debug=True)
