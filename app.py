# =============================================================================
# Imports
# =============================================================================
#from urllib.request import urlopen
#import os; os.chdir('/Users/whiskey/Desktop/johnproj')
#import json
import os
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

first_time = False # this reloads some of the raw data files. should be turned off for deployment

## variable to use for heatmap for the project scatterplot
projrank = 'Greenhouse Gases (CO2e)'
projscl = 'Greens' # just use the default matplotlib colormap of Reds for scale

# just the name of the presidential margin variable
marname = 'presmargin'

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

def roundorfine(x,rnum=2):
    if type(x)==str:
        return x
    return round(x,rnum)

def irregrank(x):
    ''' Redo the rank so .5 is 0 when have pos/neg numbers for Democratic vote margin '''
    y = pd.Series([np.nan]*len(x),index=x.index)
    y.loc[x.le(0)] = x.loc[x.le(0)].rank(ascending=False,pct=True).divide(-2)
    y.loc[x.gt(0)] = x.loc[x.gt(0)].rank(ascending=True,pct=True).divide(2)
    return y.add(.5)


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
proj_cols = {
    'Project Name':'Project Name',
    'placename':'City',
    'Operating Status':'Status',
    'Classification':'Class',
    'Industry Sector':'Sector',
    'Greenhouse Gases (CO2e)':'Greenhouse Gases',
    'Carbon Monoxide (CO)':'Carbon Monoxide',
    'Nitrogen Oxides (NOx)':'Nirogen Oxides'
}


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
    marname:'2020 Presidential Margin',
    'avg_partisan_score':'Partisan Score',
    #'avg_yale_score':'Yale Score',
    'avg_climate_score':'Climate Score',
    'avg_biden_support_score':'Biden Support Score',
    'civis_registered_count':'Registered',
    'civis_unregistered_count':'Unregistered',
    'civis_registered_ratio':'Fraction Registered'
}

# =============================================================================
# Bringing in Data on Counties
# =============================================================================
state_names = pd.read_csv(os.path.join('data','state_names.txt'),sep='\t',
                          names=['state_name','state_abbrev','state_fips'],dtype=str)
state_names = state_names.apply(lambda x: x.str.strip()) # get rid of trailing spaces

counties = gpd.read_file(os.path.join('data','cb_2018_us_county_5m'))
counties = counties.merge(state_names,
                          right_on='state_fips',
                          left_on='STATEFP',
                          how='left')

## Presidential Election Data from John
presdat = pd.read_csv(os.path.join('data','Pres_Election_Data_2020_county.csv'),
                     usecols=[2,13,14,67],
                     thousands=',',
                     names=['total','biden','trump','fips'],
                     skiprows=1).dropna()

presdat.loc[:,'state'] = np.where(presdat.fips.astype(int).astype(str).str.len().gt(2),
                                 False,
                                 True)
presdat.fips = np.where(presdat.state,
                        presdat.fips.astype(int).astype(str).str.zfill(2),
                        presdat.fips.astype(int).astype(str).str.zfill(5)
                        )

presdat.loc[:,'demmarge'] = presdat.biden.divide(presdat.total).add(-presdat.trump.divide(presdat.total))
presdat.loc[:,marname] = presdat.demmarge.multiply(100).round(1).apply(lambda x:
    'D '+str(x)[0:4]+'%' if x>=0 else 'R '+str(x)[1:5]+'%'
    )

# critical that this is called [same as above]_rank for later code
# a ranking from 0-1 with .5 being equal shares for each person, and more votes for biden == more blue
# doing this separately for states and counties
presdat.loc[presdat.state,'%s_rank' %marname] = irregrank(presdat.loc[presdat.state,'demmarge'])
presdat.loc[~presdat.state,'%s_rank' %marname] = irregrank(presdat.loc[~presdat.state,'demmarge'])

# TO CHANGE BUT FOR NOW DF IS WHERE ALL THE SCORES AND CENSUS DATA SHOULD BE BY COUNTY
if first_time:
    df = pd.read_excel(os.path.join('data','Final Aggregations (County_District_City Levels).xlsx'),
                       sheet_name='County')
    df.to_csv(os.path.join('data','final_aggregations.csv'),index=False)
else:
    df = pd.read_csv(os.path.join('data','final_aggregations.csv'))

df.county_geoid = df.county_geoid.astype(str).str.zfill(5) # getting 5 digit fips thing
df.loc[:,'civis_registered_ratio'] = df.civis_registered_count.divide(
    df.civis_registered_count+df.civis_unregistered_count
)

df = df.merge(presdat.loc[~presdat.state,:],left_on='county_geoid',right_on='fips',how='left')

## getting the county race data
races = df.set_index('county_geoid').loc[:,['Registered_{}_Total'.format(ii) for ii in race_dict.keys()]]
races.loc[:,'pop_total'] = races.sum(axis=1)

counties = counties.merge(df.loc[:,['county_geoid','pop2012',marname,'%s_rank' %marname]+
                                 list(partisan_scores.values())],
                          left_on='GEOID',
                          right_on='county_geoid',
                          how='inner') # inner

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
                                     columns=['Reg. Race/Age'])
for ii in agerace.columns:
    default_agerace_table.loc[:,ii] = np.nan*len(default_agerace_table)


### Again but for the summary table that is always on display
sumtab = df.set_index('county_geoid').loc[:,sum_table_cols.keys()]
sumtab.columns = sum_table_cols.values()
for ii in sumtab.columns:
    if 'Fraction' in ii:
        sumtab.loc[:,ii] = sumtab.loc[:,ii].apply(fixpct)
    elif 'Margin' in ii:
        pass
    elif ii in ['Registered','Unregistered']:
        sumtab.loc[:,ii] = sumtab.loc[:,ii].apply(lambda x: fixlab(x))
    else:
        sumtab.loc[:,ii] = sumtab.loc[:,ii].apply(lambda x: fixlab(x,2))


default_sum_table = pd.DataFrame(zip(sumtab.columns,[np.nan]*(len(sumtab.columns))),
                                  columns=['Characteristics','Values'])


# =============================================================================
# Making States from Counties and Adding Rank
# =============================================================================

# run the first time:
if first_time:
    states = counties.copy()
    states.loc[:,'statepop'] = states.groupby('state_abbrev').pop2012.transform(sum)

    for ii in partisan_scores.values():
        states.loc[:,ii] = states.loc[:,ii]*(states.pop2012/states.statepop)

    states = states.dissolve('state_abbrev',aggfunc='sum')
    states.to_file(os.path.join('data','states_shapefile.geojson'),driver='GeoJSON')
else:
    states = gpd.read_file(os.path.join('data','states_shapefile.geojson'))
    states = states.set_index('state_abbrev')


states.loc[:,'placename'] = states.index.map(
    state_names.set_index('state_abbrev').state_name.to_dict()
    ) # get the state names for graphing later

for ii in partisan_scores.values():
    counties.loc[:,'{}_rank'.format(ii)] = counties.loc[:,ii].rank(pct=True)
    states.loc[:,'{}_rank'.format(ii)] = states.loc[:,ii].rank(pct=True)

states = states.assign(clicktype='state')

# merging in the presidential data into the states
states = states.join(
    presdat.loc[presdat.state,:].assign(
        state_abbrev=presdat.fips.map(state_names.set_index('state_fips').state_abbrev.to_dict())
    ).set_index('state_abbrev').filter(regex='pres')
)

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
projects = pd.read_csv(os.path.join('data','projects.csv'))
projects = projects.assign(clicktype='project')
projects.loc[:,'placename'] = projects.City.str.title()+', '+projects.State

# OLD WAY when using the old projects.csv file because there were non-unique projects
# projects = projects.sort_values(['Project Name',projrank],ascending=[True, False])
# projects.loc[:,'projcount'] = projects.assign(_cons = 1).groupby('Project_Name')._cons.cumsum().values
# projects.loc[:,'Project_Name'] = (
#     np.where(projects.groupby('Project_Name').projcount.transform('count')==1,
#              projects.Project_Name,
#              projects.Project_Name + ' (' + projects.projcount.astype(str) + ')'
#              )
# )

projects = projects.set_index('Project ID').sort_values('Project Name')

# making the dictionary with all the projects
projdict = projects['Project Name'].to_dict()

# making the labels for use later
projlabs = []
for ii,jj in projects.iterrows():
    lab = (
        '<b>{}</b><br><i>{}</i><br>Status: {}<br>Classification: {}<br>'\
        'Sector: {}<br>CO2e TPY: {}<br>CO TPY: {}<br>NOx TPY: {}'.format(
            jj['Project Name'],
            jj['placename'],
            jj['Operating Status'].title(),
            jj['Classification'].title(),
            jj['Industry Sector'].title(),
            fixlab(jj['Greenhouse Gases (CO2e)']),
            fixlab(jj['Carbon Monoxide (CO)']),
            fixlab(jj['Nitrogen Oxides (NOx)'])
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



default_proj_table = pd.DataFrame(zip(list(proj_cols.values())[1:],[np.nan]*(len(proj_cols)-1)),
                                  columns=['Characteristics','Values'])

### Projects table for the table at the end
keepprojcols = {
    'Project Name':'Name',
    'City':'City',
    'County or Parish':'County',
    'State':'State',
    'Classification':'Class',
    'Industry Sector':'Sector',
    'Project Type':'Type',
    'Operating Status':'Status',
    'Greenhouse Gases (CO2e)':'CO2e',
    'Particulate Matter (PM2.5)':'PM2.5',
    'Nitrogen Oxides (NOx)':'NOx',
    'Volatile Organic Compounds (VOC)':'VOC',
    'Sulfur Dioxide (SO2)':'SO2',
    'Carbon Monoxide (CO)':'CO',
    'Hazardous Air Pollutants (HAPs)':'HAPs'
}
prettyproj = (projects
    .loc[:,keepprojcols.keys(),]
    .sort_values(projrank,ascending=False)
    .rename(columns=keepprojcols)
)

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

if first_time:
    statecenters = states.centroid.apply(lambda x: {"lat": x.y, "lon": x.x}).to_dict()
else:
    # this is better to hardcode for speed, otherwise you can generate it from above.
    statecenters = {
        'AK': {'lat': 64.19864536710269, 'lon': -152.21161373123448},
        'AL': {'lat': 32.788821784191406, 'lon': -86.82877413163206},
        'AR': {'lat': 34.899871241215195, 'lon': -92.43906311821542},
        'AZ': {'lat': 34.293211150058774, 'lon': -111.66463907125058},
        'CA': {'lat': 37.24595553055764, 'lon': -119.6105602159633},
        'CO': {'lat': 38.998545515111005, 'lon': -105.54781469615011},
        'CT': {'lat': 41.62015672684962, 'lon': -72.72640117314178},
        'DE': {'lat': 38.99204548882909, 'lon': -75.50028373711518},
        'FL': {'lat': 28.62041492098466, 'lon': -82.4976752864272},
        'GA': {'lat': 32.649094738788925, 'lon': -83.44596500320112},
        'HI': {'lat': 20.253115080067484, 'lon': -156.35292733138635},
        'IA': {'lat': 42.07462719278254, 'lon': -93.50006506707614},
        'ID': {'lat': 44.38909223490469, 'lon': -114.65935747329844},
        'IL': {'lat': 40.06500169852606, 'lon': -89.19842354739647},
        'IN': {'lat': 39.908136731062775, 'lon': -86.27562549855642},
        'KS': {'lat': 38.48469938007203, 'lon': -98.38021614182924},
        'KY': {'lat': 37.52665629171558, 'lon': -85.29056855164151},
        'LA': {'lat': 31.048494726639834, 'lon': -91.97325322252993},
        'MA': {'lat': 42.25228990949808, 'lon': -71.79509897430427},
        'MD': {'lat': 39.03126992444781, 'lon': -76.76631772288249},
        'ME': {'lat': 45.35981779141607, 'lon': -69.2228910889948},
        'MI': {'lat': 44.352476289297314, 'lon': -85.4359147179878},
        'MN': {'lat': 46.316596102870975, 'lon': -94.30876357721999},
        'MO': {'lat': 38.36765846221201, 'lon': -92.47742457510007},
        'MS': {'lat': 32.74881844210886, 'lon': -89.66427750479697},
        'MT': {'lat': 47.033485201447306, 'lon': -109.64511961499808},
        'NC': {'lat': 35.53968516211722, 'lon': -79.3564149890917},
        'ND': {'lat': 47.4463027225088, 'lon': -100.46931085379893},
        'NE': {'lat': 41.52714971186757, 'lon': -99.81084819475505},
        'NH': {'lat': 43.68574513468267, 'lon': -71.57766142933251},
        'NJ': {'lat': 40.18412844815561, 'lon': -74.6609056712226},
        'NM': {'lat': 34.421363236533026, 'lon': -106.10837614027254},
        'NV': {'lat': 39.35643474393468, 'lon': -116.65538515310705},
        'NY': {'lat': 42.940175281697854, 'lon': -75.5026176732071},
        'OH': {'lat': 40.29355614307442, 'lon': -82.79018130968092},
        'OK': {'lat': 35.58354797116435, 'lon': -97.50843879290386},
        'OR': {'lat': 43.936662110767834, 'lon': -120.55516902274762},
        'PA': {'lat': 40.87388911264181, 'lon': -77.79960395647934},
        'RI': {'lat': 41.67579888419362, 'lon': -71.55273840814883},
        'SC': {'lat': 33.907636549324906, 'lon': -80.89581622723576},
        'SD': {'lat': 44.43613089653848, 'lon': -100.23044797642653},
        'TN': {'lat': 35.84297953256935, 'lon': -86.34335390283998},
        'TX': {'lat': 31.482595722807783, 'lon': -99.34939812991959},
        'UT': {'lat': 39.32378886224561, 'lon': -111.67820486515588},
        'VA': {'lat': 37.51527475300566, 'lon': -78.80826455850163},
        'VT': {'lat': 44.075198510023924, 'lon': -72.66271933121298},
        'WA': {'lat': 47.38228437070144, 'lon': -120.45086015401435},
        'WI': {'lat': 44.639490186969255, 'lon': -90.01147527784497},
        'WV': {'lat': 38.642527095365274, 'lon': -80.61383728857619},
        'WY': {'lat': 42.99964887765216, 'lon': -107.55147723016859}
    }


if first_time:
    # determining zoom dynamically (HARD CODED AFTER FIRST RUN)
    sizerank = states.area.rank().to_frame('sizerank')
    sizerank.loc[:,'zoom'] = np.where(sizerank.sizerank>51,3,
                                np.where(sizerank.sizerank>45,4,
                                    np.where(sizerank.sizerank>20,5,
                                        np.where(sizerank.sizerank>1,6,10))))
    sizerank = sizerank.zoom.to_dict()
else:
    sizerank = {'AK':4,'AL':5,'AR':5,'AZ':5,'CA':4,'CO':5,'CT':6,'DE':6,'FL':5,'GA':5,'HI':6,
    'IA':5,'ID':5,'IL':5,'IN':6,'KS':5,'KY':6,'LA':6,'MA':6,'MD':6,'ME':6,'MI':5,'MN':5,'MO':5,
    'MS':6,'MT':4,'NC':5,'ND':5,'NE':5,'NH':6,'NJ':6,'NM':4,'NV':5,'NY':5,'OH':6,'OK':5,'OR':5,
    'PA':6,'RI':10,'SC':6,'SD':5,'TN':6,'TX':4,'UT':5,'VA':6,'VT':6,'WA':5,'WI':5,
    'WV':6,'WY':5}

# The App Layout Elements
# =============================================================================
#app = JupyterDash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY]) #CYBORG FLATLY
server = app.server

selector_col = html.Div(
    [
        html.H4(children='High Impact Local Projects and Voter Information'),
        html.P('''
            The map shades partisanship rank measures. Click or select a state to see a
            county breakdown. Darker shaded dots represent local fossil fuel projects with more CO2e.
            Browse specific counties or projects by clicking map or selecting from dropdowns.
            A full list of projects is below.
            '''
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
            options=(
                [{'value': marname, 'label': 'Democratic 2020 Presidential Margin'}]
                +[{'value': jj, 'label': ii} for ii,jj in partisan_scores.items()]
            ),
            value=marname, # the default value?
            clearable=False
        ),
    ],
    style={'margin-left':'20px','margin-top':'0px'}
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
        },
        # style_header={
        #     'backgroundColor': 'rgb(210, 210, 210)',
        #     'color': 'black',
        #     'fontWeight': 'bold'
        # }
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'height': 'auto',
        },
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
        },
        # style_header={
        #     'backgroundColor': 'rgb(210, 210, 210)',
        #     'color': 'black',
        #     'fontWeight': 'bold'
        # }
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'height': 'auto',
        },
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
        },
        # style_header={
        #     'backgroundColor': 'rgb(210, 210, 210)',
        #     'color': 'black',
        #     'fontWeight': 'bold'
        # }
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'height': 'auto',
        },
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


full_projtable = html.Div(
    [
        html.Hr(),
        html.H4(children='Browse The Full Project List'),
        html.P('''
            The full list of projects from above is found in this table, sorted by CO2e (descending).
            Columns can be sorted (ascending/descending/cleared) and filtered. Filters can be applied either exactly
            (eg. typing TX pulls in all projects in Texas) or with operators like > or < to denote
            values greater than or less than a value (eg. >MD gives all states alphabetically greater than
            or equal to Maryland while >100 gives all values in a column greater than or equal to 100.)
            Columns or rows can be removed entirely, and the final displayed table can be exported to an Excel file.
            '''
            ),
        # dash_table.DataTable(
        #     id='fullproj-table',
        #     columns=[
        #         {"name": i, "id": i} for i in prettyproj.columns
        #     ],
        #     page_action='none',
        #     style_table={'height': '1000px', 'overflowY': 'auto'},
        #     sort_action='custom',
        #     sort_mode='multi',
        #     sort_by=[],
        #     style_data={
        #         'whiteSpace': 'normal',
        #         'height': 'auto',
        #         'color': 'black',
        #         'backgroundColor': 'white'
        #     },
        #     style_cell={
        #         'height': 'auto',
        #         # all three widths are needed
        #         'maxWidth': '200px', 'width': '80px', 'minWidth': '30px',
        #         'whiteSpace': 'normal'
        #     },
        #     fixed_rows={'headers': True},
        #     style_data_conditional=[
        #         {
        #             'if': {'row_index': 'odd'},
        #             'backgroundColor': 'rgb(220, 220, 220)',
        #         }
        #     ],
        #     style_header={
        #         'backgroundColor': 'rgb(210, 210, 210)',
        #         'color': 'black',
        #         'fontWeight': 'bold'
        #     }
        # ),
        dash_table.DataTable(
            id='fullproj-table',
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True} for i in prettyproj.columns
            ],
            data=prettyproj.to_dict('records'),
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable=False,
            row_selectable=False,
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            export_format='xlsx',
            export_headers='display',
            page_action='none', # native
            style_table={'height': '1000px', 'overflowY': 'auto'},
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'maxWidth': '120px', 'minWidth':'60px',
                'whiteSpace': 'normal',
                'fontSize': '11'
            },
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            },
            style_data={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white',
                'height': 'auto',
            },
            fixed_rows={'headers': True},
            style_cell_conditional=[
                # we can do special formatting for certain cells
                {
                    'if': {'column_id': 'Name'},
                    'textAlign': 'left',
                    'maxWidth':'300px'
                }
            ],
        ),
        html.Br(),
        html.Hr(),
        html.Br()
    ], style={'margin-left':'20px','margin-right':'20px','margin-top':'10px'}
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
        dbc.Row(
            [
                dbc.Col(full_projtable,width=12)
            ], align='center',justify='center'
        )
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
                               template='plotly_dark',
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
                                            plotdf[measure].apply(roundorfine)]
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                      plot_bgcolor='rgba(0, 0, 0, 0)',
                      paper_bgcolor='rgba(0, 0, 0, 0)')
    fig.update_traces(
        hovertemplate='<b>%{customdata[1]}</b><br><i>Value:</i> %{customdata[2]}<br>'
        )
    fig.add_scattermapbox(
        lat = projects.Latitude.to_list(),
        lon = projects.Longitude.to_list(),
        mode = 'markers+text',
        text = projlabs,
        marker = go.scattermapbox.Marker(
            size = 9,
            color = projcolors,  # This is used to match the color scale
            colorscale = projscl
        ),
        hoverinfo='text',
        customdata=projects['Project Name'],
        hoverlabel=go.scattermapbox.Hoverlabel(font={'size':14}) # the size of the text
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
    data = (projects.loc[:,proj_cols.keys()].set_index('Project Name')
                    .loc[projdict[name]]
                    .to_frame()
                    .reset_index()
            )
    data.iloc[:,0] = data.iloc[:,0].map(proj_cols)
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
                       .rename(columns={'race':'Reg. Race/Age'})
                )
    else:
        data = (agerace.loc[name]
                       .divide(total_all.loc[name]) # the total groupby from above
                       .applymap(fixpct)
                       .reset_index()
                       .rename(columns={'race':'Reg. Race/Age'})
                )
    # getting the summary stats for the other table
    sumdata = sumtab.loc[name].to_frame().reset_index()
    sumdata.columns = default_sum_table.columns

    return data.to_dict('records'),sumdata.to_dict('records')


# =============================================================================
# Update the projects table based on filters
# =============================================================================

# @app.callback(
#     Output('fullproj-table', "data"),
#     Input('fullproj-table', "sort_by"))
# def update_majortable(sort_by):
#     # sorting on values
#     if len(sort_by):
#         dispproj = prettyproj.sort_values(
#             [col['column_id'] for col in sort_by],
#             ascending=[
#                 col['direction'] == 'asc'
#                 for col in sort_by
#             ],
#             inplace=False
#         )
#     else:
#         # No sort is applied
#         dispproj = prettyproj.sort_values(keepprojcols[projrank],ascending=False)
#
#     return dispproj.to_dict('records')


@app.callback(
    Output('fullproj-table', 'style_data_conditional'),
    Input('fullproj-table', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]




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
