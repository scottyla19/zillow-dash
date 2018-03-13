# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import plotly.graph_objs as go


app = dash.Dash()
#df= pd.read_csv('http://files.zillowstatic.com/research/public/Zip/Zip_MedianValuePerSqft_AllHomes.csv')

df= pd.read_csv('Zip_MedianValuePerSqft_AllHomes.csv')

states = df.State.unique()
states = sorted(states)

app.layout = html.Div(children=[
    html.H1(children='Zillow Housing Analysis'),

    dcc.Dropdown(
        id='state-choice',
        options=[{'label': i, 'value': i} for i in states],
        placeholder='Choose your state'
    ),
    dcc.Dropdown(
        id='metro-choice',
        # options=[{'label': i, 'value': i} for i in states],
        placeholder='Choose your metro area'
    ),
    dcc.Dropdown(
        id='zip-choice',
        # options=[{'label': i, 'value': i} for i in states],
        placeholder='Choose your zipcode'
    ),
    dt.DataTable(
        rows=[{}],
        id='datatable',
        # rows=df.to_dict('records'),
        filterable=True,
        sortable=True
    ),
    dcc.Graph(id='graph')
])

# update table on change of all dropdowns
@app.callback(
    Output('datatable', 'rows'),
    [Input('state-choice', 'value'),
    Input('metro-choice', 'value'),
    Input('zip-choice', 'value')])
def state_cb(state, metro, zipcode):
    if zipcode:
        currDF = df[df['RegionName']== zipcode]
        return currDF.to_dict('records')
    elif metro:
        currDF = df[df['Metro']== metro]
        return currDF.to_dict('records')
    else:
        currDF = df[df['State']== state]
        return currDF.to_dict('records')

# update metro dropdown on state dropdown choice
@app.callback(
    Output('metro-choice', 'options'),
    [dash.dependencies.Input('state-choice', 'value')])
def metro_cb(dropdown_value):
    currDF = df[df['State'] == dropdown_value]
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
    currDF = df[(df['State'] == state) & (df['Metro'] == metro)]
    currDF.dropna(subset=["Metro"], inplace=True)
    zips = currDF.RegionName.unique()
    zips = sorted(zips)
    return [{'label': z, 'value': z} for z in zips]


# Create Graph
@app.callback(
    Output('graph', 'figure'),
    [Input('state-choice', 'value'),
    Input('metro-choice', 'value'),
    Input('zip-choice', 'value')])
def update_figure(state, metro, zip):
    currDF = df[df['State']== state]
    dfGroup = currDF.groupby('Metro', as_index = False)['2018-01'].mean()
    print(dfGroup)
    return {
        'data': [go.Bar(
            x=dfGroup['Metro'],
            y=dfGroup['2018-01'],

        )]
    }

if __name__ == '__main__':
    app.run_server(debug=True)