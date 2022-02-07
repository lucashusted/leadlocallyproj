from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px
import numpy as np
import geopandas as gpd
#from jupyter_dash import JupyterDash
import dash
from dash import dash_table
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import html
# some fake data for now, fill with real stuff later.
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})
df.loc[:,'shit'] = np.log(df.unemp)

state_names = pd.read_csv('state_names.txt',sep='\t',names=['state_name','state_abbrev','state_fips'],dtype=str)
state_names = state_names.apply(lambda x: x.str.strip()) # get rid of trailing spaces

counties = gpd.read_file('cb_2018_us_county_5m')
df = counties.merge(df,left_on='GEOID',right_on='fips')

df = df.merge(state_names,left_on='STATEFP',right_on='state_fips',how='left')
# get all the ones that matched
states = df.state_name.sort_values().dropna().unique()

# making the state dropdown dictionaries
statedropdown = (
    [{'label':'United States','value':'US'}] +
    [{'label': ii, 'value': jj} for ii,jj in df.groupby('state_name').state_abbrev.first().iteritems()]
    )

# get the centers of each state in the dataframe that way we can navigate accordingly from dropdown
states = df.dissolve('state_abbrev')
statecenters = states.centroid.apply(lambda x: {"lat": x.y, "lon": x.x}).to_dict()


# determining zoom dynamically
sizerank = states.area.rank().to_frame('sizerank')
sizerank.loc[:,'zoom'] = np.where(sizerank.sizerank>51,3,
                            np.where(sizerank.sizerank>45,4,
                                np.where(sizerank.sizerank>20,5,
                                    np.where(sizerank.sizerank>1,6,10))))
sizerank = sizerank.zoom.to_dict()

data_url = 'https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv'
df_fake = pd.read_csv(data_url)


df_table = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')


#app = JupyterDash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY]) #CYBORG

selector_col = html.Div(
    [
        html.H4(children='High Impact Local Projects and Voter Information'),
        html.Br(),
        html.P('Select specific states, voter measures, or '\
               'geographic unit of measure using the drop-down menus.'
        ),
        html.Label('Location'),
        dcc.Dropdown(
            id='location',
            options=statedropdown,
            value='US'
        ),
        html.Br(),
        html.Label('Geographic Unit'),
        dcc.Dropdown(
            id='unit',
            options=[{'value': i, 'label': i.title()} for i in ['county','congressional district']],
            value='county'
        ),
        html.Br(),
        html.Label('Voter Measure'),
        dcc.Dropdown(
            id='measure',
            options=[{'value': x, 'label': x.title()} for x in ['unemp','shit']],
            value='unemp', # the default value?
        ),
    ], style={'margin-left':'20px','margin-top':'20px'}
)

map_col = html.Div(
    dcc.Graph(id="choropleth"),
    style={'margin-top':'20px','margin-right':'20px','margin-bottom':'30px'}
)

table_col = html.Div(
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df_table.columns],
        data=df_table.to_dict('records')
    ),
    style={'margin-left':'100px','margin-right':'100px'}
)



app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(selector_col,width=3),
                dbc.Col(map_col,width=9)
            ], justify='center',align='center'
        ),
        dbc.Row(
            [
                dbc.Col(table_col, width=12)
            ], justify='center', align='center'
        )
    ]
)


@app.callback(
    Output("choropleth", "figure"),
    Input("measure", "value"),
    Input("location","value")
    )

def display_choropleth(measure,location):
    if location == 'US':
        plotdf = states # df
        zoom = 3
        center = {"lat": 37.0902, "lon": -95.7129}
    else:
        plotdf = df.loc[df.state_abbrev.eq(location),:]
        zoom = sizerank[location]
        center = statecenters[location]

    fig = px.choropleth_mapbox(plotdf, geojson=plotdf.geometry,
                           locations=plotdf.index, color=measure,
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           mapbox_style="carto-positron",
                           zoom=zoom, center = center,
                           opacity=0.5,
                           labels={'unemp':'Unemployment Rate'},
                           custom_data=[plotdf['GEOID'],
                                        plotdf[measure]]
                          )
    hovertemp = '%{customdata[0]}<br>'
    hovertemp += '<i>Value:</i> %{customdata[1]}<br>'
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(hovertemplate=hovertemp)

    fig.add_scattermapbox(
        lat = ['38.91427','38.91538','38.91458',
                 '38.92239','38.93222','38.90842',
                 '38.91931','38.93260','38.91368',
                 '38.88516','38.921894','38.93206',
                 '38.91275'
              ],
        lon = ['-77.02827','-77.02013','-77.03155',
                 '-77.04227','-77.02854','-77.02419',
                 '-77.02518','-77.03304','-77.04509',
                 '-76.99656','-77.042438','-77.02821',
                 '-77.01239'
              ],
        mode = 'markers+text',
        text = ["The coffee bar","Bistro Bohem","Black Cat",
                 "Snap","Columbia Heights Coffee","Azi's Cafe",
                 "Blind Dog Cafe","Le Caprice","Filter",
                 "Peregrine","Tryst","The Coupe",
                 "Big Bear Cafe"
               ],
        marker_size=12,
        marker_color='rgb(235, 0, 100)'
    )

    return fig



#
# @app.callback(
#     Output('selections', 'value'),
#     Input('choropleth', 'clickData')
#     )
# def update_figure(clickData):
#     if clickData is not None:
#         location = clickData['points'][0]['location']
#
#         if location not in selections:
#             selections.add(location)
#         else:
#             selections.remove(location)
#     return

app.run_server(debug=True,use_reloader=False)
#app.run_server(mode='inline')
