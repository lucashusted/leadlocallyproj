# =============================================================================
# Imports
# =============================================================================
#from urllib.request import urlopen
#import os; os.chdir('/Users/whiskey/Desktop/johnproj')
#import json
import pandas as pd
import plotly.express as px
import numpy as np
import geopandas as gpd
import plotly.graph_objects as go
#from jupyter_dash import JupyterDash
import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

## variable to use for heatmap for the project scatterplot
projrank = 'CO2e tpy'
projscl = 'Reds' # just use the default matplotlib colormap of Reds for scale

# a helper function to fix the labeling of potentially missing CO2 variables
def fixlab(x,roundnum=None):
    if roundnum:
        return "{:,}".format(round(x,roundnum)) if not pd.isna(x) else 'NA'
    return "{:,}".format(round(x)) if not pd.isna(x) else 'NA'

def fixpct(x):
    if pd.isna(x):
        return 'NA'
    if x<.0005:
        return '<0.1%'
    else:
        return str(round(100*x,1)) + '%'

# for the map rendering, here's the choices
partisan_scores = {
    'Partisan Score':'avg_partisan_score',
    'Yale Score':'avg_yale_score',
    'Climate Score':'avg_climate_score',
    'Biden Support Score':'avg_biden_support_score',
    'Local Voter Score':'avg_local_voter_score',
    'Pres. General Turnout':'avg_p_turnout_score',
    'Midterm General Turnout':'avg_m_turnout_score',
    'Offyear General Turnout':'avg_offyear_m_turnout_score',
    'Pres. Primary Turnout':'avg_pp_turnout_score',
    'Non-Pres Primary Turnout':'avg_nonpp_turnout_score'
}

# Project_Name has to be first and placename is defined in the code below
proj_cols = ['Project_Name','placename','Operational Status','Classification',
            'Sector','CO2e tpy','CO tpy','NOx tpy']

race_dict = {
    'African_Americans':'African American',
    'Asians':'Asian',
    'Caucasians':'White',
    'Hispanics':'Hispanic',
    'Native_Americans':'Native American',
    'Other_and_Uncoded_Race':'Other'
}
age_dict = {
    '18_34':'18-34',
    '35_64':'35-64',
    '65':'65+',
}

# getting the fixed multi-index columns combining race and age
agerace_dict = dict(
    zip(
        ['Registered_{}_{}'.format(ii,jj) for ii in race_dict.keys() for jj in age_dict.keys()],
        [tuple([ii,jj]) for ii in race_dict.values() for jj in age_dict.values()]
    )
)

sum_table_cols = {
    'avg_partisan_score':'Partisan Score',
    'avg_yale_score':'Yale Score',
    'avg_climate_score':'Climate Score',
    'avg_biden_support_score':'Biden Support Score',
    'civis_registered_count':'Registered',
    'civis_unregistered_count':'Unregistered',
    'civis_registered_ratio':'Fraction Registered'
}

# =============================================================================
# Bringing in Data on Counties
# =============================================================================
state_names = pd.read_csv('data/state_names.txt',sep='\t',
                          names=['state_name','state_abbrev','state_fips'],dtype=str)
state_names = state_names.apply(lambda x: x.str.strip()) # get rid of trailing spaces

counties = gpd.read_file('data/cb_2018_us_county_5m')
counties = counties.merge(state_names,
                          right_on='state_fips',
                          left_on='STATEFP',
                          how='left')

# TO CHANGE BUT FOR NOW DF IS WHERE ALL THE SCORES AND CENSUS DATA SHOULD BE BY COUNTY
df = pd.read_excel('data/Final Aggregations (County_District_City Levels).xlsx',
                   sheet_name='County')
df.county_geoid = df.county_geoid.astype(str).str.zfill(5) # getting 5 digit fips thing
df.loc[:,'civis_registered_ratio'] = df.civis_registered_count.divide(
    df.civis_registered_count+df.civis_unregistered_count
)



races = df.set_index('county_geoid').loc[:,['Registered_{}_Total'.format(ii) for ii in race_dict.keys()]]
races.loc[:,'pop_total'] = races.sum(axis=1)

counties = counties.merge(df.loc[:,['county_geoid','pop2012']+
                                 list(partisan_scores.values())],
                          left_on='GEOID',
                          right_on='county_geoid',
                          how='inner')

counties.loc[:,'placename'] = counties.NAME+', '+counties.state_abbrev
counties = counties.assign(clicktype='county')

# get the county dictionary and sort the values
countydict = counties.sort_values(['state_abbrev','placename']).set_index('GEOID').placename.to_dict()

# =============================================================================
# Getting the Age + Race DataFrame for Display and the summary stats table
# =============================================================================
agerace = df.set_index('county_geoid').loc[:,agerace_dict.keys()]
agerace.columns = pd.MultiIndex.from_tuples(
    [agerace_dict[ii] for ii in agerace.columns],
    names=['race','age']
)

agerace = agerace.rename(columns=agerace_dict).stack().stack()
total_all = agerace.groupby('county_geoid').sum()
agerace = agerace.unstack('race')
agerace.loc[:,'Total'] = agerace.sum(axis=1,skipna=True)
agerace = agerace.stack().unstack('age')
agerace.loc[:,'Total'] = agerace.sum(axis=1,skipna=True)

# making the default table for display
default_agerace_table = pd.DataFrame(list(agerace.index.get_level_values('race').unique()),
                                     columns=['Race/Age'])
for ii in agerace.columns:
    default_agerace_table.loc[:,ii] = np.nan*len(default_agerace_table)


### Again but for the summary table that is always on display
sumtab = df.set_index('county_geoid').loc[:,sum_table_cols.keys()]
sumtab.columns = sum_table_cols.values()
for ii in sumtab.columns:
    if 'Fraction' in ii:
        sumtab.loc[:,ii] = sumtab.loc[:,ii].apply(fixpct)
    elif ii in ['Registered','Unregistered']:
        sumtab.loc[:,ii] = sumtab.loc[:,ii].apply(lambda x: fixlab(x))
    else:
        sumtab.loc[:,ii] = sumtab.loc[:,ii].apply(lambda x: fixlab(x,2))


default_sum_table = pd.DataFrame(zip(sumtab.columns,[np.nan]*(len(sumtab.columns))),
                                  columns=['Characteristics','Values'])


# =============================================================================
# Making States from Counties and Adding Rank
# =============================================================================
#state_list = counties.state_name.sort_values().dropna().unique()

states = counties.copy()
states.loc[:,'statepop'] = states.groupby('state_abbrev').pop2012.transform(sum)

for ii in partisan_scores.values():
    states.loc[:,ii] = states.loc[:,ii]*(states.pop2012/states.statepop)

states = states.dissolve('state_abbrev',aggfunc='sum')
states.loc[:,'placename'] = states.index.map(
    state_names.set_index('state_abbrev').state_name.to_dict()
    ) # get the state names for graphing later

for ii in partisan_scores.values():
    counties.loc[:,'{}_rank'.format(ii)] = counties.loc[:,ii].rank(pct=True)
    states.loc[:,'{}_rank'.format(ii)] = states.loc[:,ii].rank(pct=True)

states = states.assign(clicktype='state')

statedict = states.placename.to_dict()

# get all the ones that matched

# =============================================================================
# Brining in the Cities
# =============================================================================
# cities = gpd.read_file('us_principal_cities')


# cities = gpd.read_file('cb_2018_us_ua10_500k')
# cities.loc[:,'NAME'] = cities.NAME10.str.split(', ').apply(lambda x: x[0]).str.upper()
# cities.loc[:,'STATE'] = (cities.NAME10.str.split(', ')
#                          .apply(lambda x: x[1]).str.upper()
#                          .apply(lambda x: x.split('--')[0])
#                          )

# =============================================================================
# Getting the Projects and Labels Ready for the Scatterplot
# =============================================================================
projects = pd.read_csv('data/projects.csv')
projects = projects.assign(clicktype='project')
projects.loc[:,'placename'] = projects.City.str.title()+', '+projects.State

# No repeated projects names, so give unique names to multiple projects with same name
projects = projects.sort_values(['Project_Name',projrank],ascending=[True, False])
projects.loc[:,'projcount'] = projects.assign(_cons = 1).groupby('Project_Name')._cons.cumsum().values
projects.loc[:,'Project_Name'] = (
    np.where(projects.groupby('Project_Name').projcount.transform('count')==1,
             projects.Project_Name,
             projects.Project_Name + ' (' + projects.projcount.astype(str) + ')'
             )
)

# making the dictionary with all the projects
projdict = projects.Project_Name.to_dict()

# making the labels for use later
projlabs = []
for ii,jj in projects.iterrows():
    lab = (
        '<b>{}</b><br><i>{}</i><br>Status: {}<br>Classification: {}<br>'\
        'Sector: {}<br>CO2e TPY: {}<br>CO TPY: {}<br>NOx TPY: {}'.format(
            jj['Project_Name'],
            jj['placename'],
            jj['Operational Status'].title(),
            jj['Classification'].title(),
            jj['Sector'].title(),
            fixlab(jj['CO2e tpy']),
            fixlab(jj['CO tpy']),
            fixlab(jj['NOx tpy'])
        )
    )
    projlabs.append(lab)

# this ranks the projects by CO tpy quintile, fills missing with 0
projcolors = ((projects[projrank].rank(pct=True)//.2+1)
              .fillna(0)
              .astype(int)
              .divide(5)
              ).to_list()

# this just ranks it normally
#projcolors = projects[projrank].rank(pct=True).fillna(0).to_list()
# full custom with ranks
# projscl = [[0,'grey'],[.2,'red'],[.4,'blue'],[.6,'brown'],[.8,'orange'],[1,'pink']]

default_proj_table = pd.DataFrame(zip(proj_cols[1:],[np.nan]*(len(proj_cols)-1)),
                                  columns=['Characteristics','Values'])

# =============================================================================
# Features of the selectors
# =============================================================================

# making the state dropdown dictionaries
statedropdown = (
    [{'label':'United States','value':'US'}] +
    [{'label': ii, 'value': jj} for ii,jj in
         counties.groupby('state_name').state_abbrev.first().iteritems()]
    )

# get the centers of each state in the dataframe that way we can navigate accordingly from dropdown

statecenters = states.centroid.apply(lambda x: {"lat": x.y, "lon": x.x}).to_dict()

# determining zoom dynamically
sizerank = states.area.rank().to_frame('sizerank')
sizerank.loc[:,'zoom'] = np.where(sizerank.sizerank>51,3,
                            np.where(sizerank.sizerank>45,4,
                                np.where(sizerank.sizerank>20,5,
                                    np.where(sizerank.sizerank>1,6,10))))
sizerank = sizerank.zoom.to_dict()


# =============================================================================
# The App Layout Elements
# =============================================================================
#app = JupyterDash(__name__)
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.FLATLY]) #CYBORG
server = app.server

selector_col = html.Div(
    [
        html.H4(children='High Impact Local Projects and Voter Information'),
        html.Br(),
        html.P('Graphs show relative rank by geographic unit of relevant score. '\
               'Select specific states to see breakdown by county.'
        ),
        html.Label('Location'),
        dcc.Dropdown(
            id='location',
            options=statedropdown,
            value='US',
            clearable=False
        ),
        html.Br(),
        # html.Label('Geographic Unit'),
        # dcc.Dropdown(
        #     id='unit',
        #     options=[{'value': i, 'label': i.title()} for i in ['county','congressional district']],
        #     value='county'
        # ),
        # html.Br(),
        html.Label('Voter Measure'),
        dcc.Dropdown(
            id='measure',
            options=[{'value': jj, 'label': ii} for ii,jj in partisan_scores.items()],
            value='avg_partisan_score', # the default value?
            clearable=False
        ),
    ],
    style={'margin-left':'20px','margin-top':'20px'}
)

map_col = html.Div(
    dcc.Graph(id="choropleth"),
    style={'margin-top':'20px','margin-right':'20px','margin-bottom':'20px'}
)

table_proj = html.Div(
    dash_table.DataTable(
        id='proj-table',
        columns=[{"name": i, "id": i} for i in default_proj_table.columns],
        data=default_proj_table.to_dict('records'),
        style_cell={
            'height': 'auto',
            # all three widths are needed
            'maxWidth': '170px', # 'minWidth': '170px', 'width': '170px',
            'whiteSpace': 'normal'
        }
    ),
    # add the margin on the table, so no need on the selectors
    style={'margin-left':'20px','margin-right':'20px','margin-top':'10px'}
)

table_sumtab = html.Div(
    dash_table.DataTable(
        id='sumtab-table',
        columns=[{"name": i, "id": i} for i in default_sum_table.columns],
        data=default_sum_table.to_dict('records'),
        style_cell={
            'height': 'auto',
            # all three widths are needed
            'maxWidth': '170px', #'width': '100px', 'minWidth': '100px',
            'whiteSpace': 'normal'
        }
    ),
    # add the margin on the table, so no need on the selectors
    style={'margin-left':'20px','margin-right':'5px','margin-top':'10px'}
)

table_agerace = html.Div(
    dash_table.DataTable(
        id='agerace-table',
        columns=[{"name": i, "id": i} for i in default_agerace_table.columns],
        data=default_agerace_table.to_dict('records'),
        style_cell={
            'height': 'auto',
            # all three widths are needed
            'maxWidth': '170px', #'width': '100px', 'minWidth': '100px',
            'whiteSpace': 'normal'
        }
    ),
    # add the margin on the table, so no need on the selectors
    style={'margin-left':'5px','margin-right':'50px','margin-top':'10px'}
)

proj_selector = html.Div(
    dcc.Dropdown(
        id='project-select',
        options=[{'value': ii, 'label': jj} for ii,jj in projdict.items()],
        placeholder='Find a project',
    ),
    style={'margin-left':'20px','margin-right':'20px'}
)

place_selector = html.Div(
    dcc.Dropdown(
        id='place-select',
        options=[{'value': ii, 'label': jj} for ii,jj in countydict.items()],
        placeholder='Find a county'
    ),
    style={'margin-left':'20px',} #'margin-right':'50px'}
)

radio_freq = dcc.RadioItems(
    id='freq-type',
    options=[{'value':'count','label':'Count'},
             {'value':'percent','label':'Percent'}],
    value='count',
    labelStyle={'display': 'inline-block','margin-left':'4px','margin-right':'7px'},
)

# =============================================================================
# The App Layout Itself
# =============================================================================

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
                dbc.Col(proj_selector,width=4),
                dbc.Col(place_selector,width={"size": 6, "offset": 0}),
                dbc.Col(radio_freq,width={'size':2,'offset':0})
            ],align='start'
        ),
        dbc.Row(
            [
                dbc.Col(table_proj, width=4),
                dbc.Col(table_sumtab,width=3),
                dbc.Col(table_agerace, width=5)
            ], align='start' # justify='center'
        ),
    ]
)

# =============================================================================
# The function the makes the map
# =============================================================================
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
        plotdf = counties.loc[counties.state_abbrev.eq(location),:]
        zoom = sizerank[location]
        center = statecenters[location]

    fig = px.choropleth_mapbox(plotdf,
                               geojson=plotdf.geometry,
                               locations=plotdf.index,
                               color='{}_rank'.format(measure),
                               color_continuous_scale='rdbu', #"Viridis",
                               range_color=(0, 1),
                               mapbox_style="carto-positron",
                               zoom=zoom,
                               center = center,
                               opacity=0.5,
                               labels = {'{}_rank'.format(measure):'Rank (Pct.)'},
                               custom_data=[plotdf['clicktype'],
                                            plotdf['placename'],
                                            plotdf[measure].round(2)]
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(
        hovertemplate='<b>%{customdata[1]}</b><br><i>Value:</i> %{customdata[2]}<br>'
        )
    fig.add_scattermapbox(
        lat = projects.lat.to_list(),
        lon = projects.lon.to_list(),
        mode = 'markers+text',
        text = projlabs,
        marker = go.scattermapbox.Marker(
            size = 10,
            color = projcolors,  # This is used to match the color scale
            colorscale = projscl
        ),
        hoverinfo='text',
        customdata=projects['Project_Name'],
        hoverlabel=go.scattermapbox.Hoverlabel(font={'size':15}) # the size of the text
    )

    return fig

# =============================================================================
# Update the project selector from the clickData
# =============================================================================
@app.callback(
    Output('project-select', 'value'),
    Output('place-select', 'value'),
    Input('choropleth', 'clickData'),
    State('project-select', 'value'),
    State('place-select', 'value'),
    )
def update_project_select(clickData,project,place):
    if not clickData:
        return project,place
    # otherwise, if a click has happened:
    customdata = clickData['points'][0]['customdata']
    if type(customdata)==str:
        # convert the customdata id to a value
        id = list(projdict.keys())[list(projdict.values()).index(customdata)]
        return id,place
    elif customdata[0]=='state':
        return project,place
    else: # elif customdata[1]=='county'
        id = list(countydict.keys())[list(countydict.values()).index(customdata[1])]
        return project,id

# =============================================================================
# Update the map to zoom on a state if the state is clicked
# =============================================================================
@app.callback(
    Output("location","value"),
    Input('choropleth', 'clickData'),
    State("location","value")
    )
def update_project_select(clickData,value):
    if not clickData:
        return dash.no_update
    # otherwise, if a click has happened:
    customdata = clickData['points'][0]['customdata']
    if type(customdata)==str:
        # convert the customdata id to a value
        return dash.no_update
    elif customdata[0]=='state':
        return list(statedict.keys())[list(statedict.values()).index(customdata[1])]
    else: # elif customdata[1]=='county'
        return dash.no_update


# =============================================================================
# Update the project table based on the clickdata
# =============================================================================
@app.callback(
    Output('proj-table','data'),
    Input('project-select', 'value'),
    )
def update_proj_table(name):
    if not name:
        return default_proj_table.to_dict('records')
    data = (projects.loc[:,proj_cols].set_index('Project_Name')
                    .loc[projdict[name]]
                    .to_frame()
                    .reset_index()
            )
    data.columns = ['Characteristics','Values']
    return data.to_dict('records')


# =============================================================================
# Update the county table based on the clickdata
# =============================================================================
@app.callback(
    Output('agerace-table','data'),
    Output('sumtab-table','data'),
    Input('place-select', 'value'),
    Input('freq-type','value'),
    )
def update_agerace_table(name,freqtype):
    if not name:
        return default_agerace_table.to_dict('records'),default_sum_table.to_dict('records')
    if freqtype=='count':
        data = (agerace.loc[name]
                       .applymap(fixlab)
                       .reset_index()
                       .rename(columns={'race':'Race/Age'})
                )
    else:
        data = (agerace.loc[name]
                       .divide(total_all.loc[name]) # the total groupby from above
                       .applymap(fixpct)
                       .reset_index()
                       .rename(columns={'race':'Race/Age'})
                )
    # getting the summary stats for the other table
    sumdata = sumtab.loc[name].to_frame().reset_index()
    sumdata.columns = default_sum_table.columns

    return data.to_dict('records'),sumdata.to_dict('records')




# =============================================================================
# Testing
# =============================================================================
# @app.callback(
#     Output('table-title', 'children'),
#     Input('choropleth', 'clickData')
#     )
# def display_table(clickData):
#     if not clickData:
#         return 'Make a Selection to Display Data'
#     else:
#         return '{}'.format(clickData)

# def update_figure(clickData):
#     if clickData is not None:
#         location = clickData['points'][0]['location']
#
#         if location not in selections:
#             selections.add(location)
#         else:
#             selections.remove(location)
#     return

if __name__ == '__main__':
    app.run_server()
#app.run_server(debug=False,use_reloader=False)
#app.run_server(mode='inline')
