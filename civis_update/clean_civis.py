# =============================================================================
# Setup and Pulling in Variables to Gather
# =============================================================================
import pandas as pd
import requests
import numpy as np
#import json

# may need to get a new one, they are free: https://api.census.gov/data/key_signup.html
key = 'dd656273275c1cd093eff324a1bbb16b338a001c'


def check_age(x):
    if x[1]<18:
        return 'child'
    elif x[0]>=65:
        return '65+'
    elif x[1]<35:
        return '18-34'
    else:
        return '35-64'

def get_age_range(x):
    if x=='Under 5 years':
        return (0,5)
    if x=='85 years and over':
        return (85,100)
    elif 'to' in x:
        y = x.split(' to ')
        y2 = y[1].split(' ')
        return (int(y[0]),int(y2[0]))
    elif 'and' in x:
        y = x.split(' and ')
        y2 = y[1].split(' ')
        return (int(y[0]),int(y2[0]))
    else:
        y = x.split(' ')
        return (int(y[0]),int(y[0]))
    
race_dict = {
    'B01001': 'Total',
    'B01001A':'White Alone',
    'B01001B':'Black or African American Alone',
    'B01001C':'American Indian and Alaska Native Alone',
    'B01001D':'Asian Alone',
    'B01001E':'Native Hawaiian and Other Pacific Islander Alone',
    'B01001F':'Some Other Race Alone',
    'B01001G':'Two or More Races',
    'B01001H':'White Alone, Not Hispanic or Latino',
    'B01001I':'Hispanic or Latino'
    }
        

acsvars = pd.read_csv('acs_variables.csv')
acsvars = acsvars.dropna(subset=['Label'])

# do gender
acsvars = acsvars.loc[acsvars.Label.str.split('!!').apply(len).ge(4),:]
acsvars.loc[:,'gender'] = acsvars.Label.str.split('!!').apply(lambda x: x[2]).values
acsvars.loc[:,'male'] = acsvars.gender.eq('Male:')

# get min and max ages and then age output
acsvars.loc[:,'agerange'] = acsvars.Label.str.split('!!').apply(lambda x: x[-1]).values
acsvars.loc[:,'agerange'] = acsvars.agerange.apply(get_age_range)
acsvars.loc[:,'age'] = acsvars.agerange.apply(check_age)

# race
acsvars.loc[:,'race'] = acsvars.Name.apply(lambda x: race_dict[x.split('_')[0]])

# subset it fully
acsvars = acsvars.loc[acsvars.age.ne('child'),['Name','male','age','race']]


# =============================================================================
# Doing the API pull (limited to 50 variables at a time)
# =============================================================================
vars_to_pull = acsvars.Name.to_list()
results = {}
x = 0
while x<=len(acsvars):
    url = 'https://api.census.gov/data/2019/acs/acs5?get=NAME,'\
        '{}&for=county:*&in=state:*&key={}'.format(
    ','.join(vars_to_pull[x:x+40]),key
    )
    pull = requests.get(url)
    results[x] = pd.DataFrame(pull.json()[1:],columns=pull.json()[0])
    x+=40


for ii,jj in results.items():
    jj.loc[:,'geoid'] = jj.state+jj.county
    temp = jj.set_index(['geoid']).drop(columns=['NAME','state','county'])
    if ii==0:
        final = temp
    else:
        final = final.join(temp)

final.columns.name = 'Name'
final = final.sort_index().stack().to_frame('population')
final = final.join(acsvars.set_index('Name'))

final.population = final.population.astype(int)

final.race = final.race.replace({'Native Hawaiian and Other Pacific Islander Alone':'Other Alone',
                                 'Some Other Race Alone':'Other Alone'})

final = final.groupby(['geoid','age','race']).population.sum()

# make race the columns
final = final.unstack()

namedict = results[0].set_index('geoid').NAME.to_dict()


#%% Redistributing hispanic and multiple race people


# the base matrix is all the individual races alone
alones = [x for x in final.columns if 'Alone' in x and 'Hispanic' not in x]
nonwhite = [x for x in alones if 'White' not in x]
# get their fraction in the population
race_frac = final.loc[:,alones].divide(final.loc[:,alones].sum(axis=1),axis=0)
nonwhite_frac = final.loc[:,nonwhite].divide(final.loc[:,nonwhite].sum(axis=1),axis=0).fillna(0)

# make a new base matrix with the counts, where two or more races are split amongst population
two_race = race_frac.multiply(final.loc[:,'Two or More Races'],axis=0).round().astype(int)
counts = final.loc[:,alones]+two_race

# we have the white/hispanic people, pull them out:
counts.loc[:,'White Alone'] = (
    counts.loc[:,'White Alone']-(
        final.loc[:,'White Alone']-final.loc[:,'White Alone, Not Hispanic or Latino']
        )
    )

# get the remaining hispanic population and subtract them out
nonwhite_hisp = (final.loc[:,'Hispanic or Latino'] - (
    final.loc[:,'White Alone']-final.loc[:,'White Alone, Not Hispanic or Latino']
    )
)

hispother = nonwhite_frac.multiply(nonwhite_hisp,axis=0).round().astype(int)

counts.loc[:,hispother.columns] = (
    counts.loc[:,hispother.columns]-(hispother//2) # only remove half of the racial group
    )

counts.loc[:,'hispanic'] = final.loc[:,'Hispanic or Latino']


counts = counts.rename(columns={'American Indian and Alaska Native Alone':'Native American',
                                'Asian Alone':'Asian',
                                'Black or African American Alone':'Black',
                                'Other Alone':'Other',
                                'White Alone':'White',
                                'hispanic':'Hispanic'})

# make sure there is at least one person in each category, makes min value 1
counts = counts.clip(1)


#%% Merging in the registration data from Civis and seeing if it checks out

state_to_fips = pd.read_csv('state_names.txt',delimiter='\t',names=['state','abbrev','code'])
state_to_fips.abbrev = state_to_fips.abbrev.str.strip()

civis = pd.read_csv('civis_registered.csv')
civis.loc[:,'state'] = civis.state_abbrev.map(state_to_fips.set_index('abbrev').code.to_dict())
civis = civis.dropna(subset=['state','fips'])
civis = civis.rename(columns={'age_group':'age'})

# making a matching combined fips code
civis.loc[:,'geoid'] = (
    civis.state.astype(int).astype(str).str.zfill(2)+
    civis.fips.astype(int).astype(str).str.zfill(3)
    )

civis.loc[:,'race'] = np.where(
    civis.race.eq('African-American'),'Black',
    np.where(civis.race.eq('Native American'),'Native American',
    np.where(civis.race.eq('Uncoded'),'Other',
    np.where(civis.race.eq('Other'),'Other',
    np.where(civis.race.eq('Hispanic'),'Hispanic',
    np.where(civis.race.eq('Caucasian'),'White',
    np.where(civis.race.eq('Asian'),'Asian',
    'Bad')))))))

# getting rid of missing columns (though this isn't relevant anymore), and ensuring we have a full panel (with 0)
civis = civis.loc[civis.age.ne('Bad') & civis.race.ne('Bad'),:]
civis = civis.groupby(['geoid','age','race']).registered.sum().unstack().unstack()
civis = civis.fillna(0).stack().stack().astype(int).unstack()


#%% Combining it all

df = counts.stack().to_frame('population').join(civis.stack().rename('registered'))
df = df.dropna().astype(int)

df.loc[:,'reg_frac'] = df.registered.divide(df.population)

county_reg = df.groupby('geoid').sum()
county_reg.reg_frac = county_reg.registered.divide(county_reg.population)


#%% Export to CSV

df.to_csv('civis_registration_totals.csv')


#%% Briefly Clean Up the Scores File To Get a GEOID

df = pd.read_csv('civis_scores.csv')
df.loc[:,'state'] = df.state_abbrev.map(state_to_fips.set_index('abbrev').code.to_dict())
df = df.dropna(subset=['state','fips']).copy()

df.loc[:,'geoid'] = (
    df.state.astype(int).astype(str).str.zfill(2)+
    df.fips.astype(int).astype(str).str.zfill(3)
    )

df = df.set_index('geoid').filter(regex='score')

df.to_csv('civis_scores_cleaned.csv')