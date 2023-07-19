import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import pymc3 as pm

lookup_df = pd.read_csv('oa_to_parishes.csv')

counties = [
        'Cumbria',
        'East Sussex',
        'Somerset',
        'Warwickshire',
        'Worcestershire',
        'Cambridgeshire',
        'North Yorkshire',
        'Gloucestershire',
        'Oxfordshire',
        'Leicestershire',
        'Lincolnshire',
        'Suffolk',
        'Devon',
        'Derbyshire',
        'Nottinghamshire',
        'West Sussex',
        'Staffordshire',
        'Norfolk',
        'Surrey',
        'Hertfordshire',
        'Tyne and Wear',
        'Lancashire',
        'Hampshire'
]


def num_things(ams, thing):
    return len([t for t in ams if t['amenity'] == thing])


results_dict = {}
overall_dict = {}

for county in counties:
    with open("all_data_final_{0}.json".format(county), 'r') as f:
        data = json.loads(f.read())
    parsed_data = {}
    for entry in data:
        parish_name = lookup_df[lookup_df.OA21CD == entry['code']].PAR22NM.values[0]
        try:
            parsed_data[parish_name]['population'] += entry['population']
            for am in entry['amenities']:
                parsed_data[parish_name]['amenities'].append(am)
        except:
            parsed_data[parish_name] = {
                    'population': entry['population'],
                    'amenities': [am for am in entry['amenities']]
                    }
    for parish, vals in parsed_data.items():
        num_pubs = num_things(vals['amenities'], 'pub')
        num_schools = num_things(vals['amenities'], 'school')
        num_church = num_things(vals['amenities'], 'place_of_worship')
        num_cafe = num_things(vals['amenities'], 'cafe')
        num_amenities = len(vals['amenities'])
        try:
            results_dict[county]['population'].append(vals['population'])
            results_dict[county]['pubs'].append(num_pubs)
            results_dict[county]['schools'].append(num_schools)
            results_dict[county]['church'].append(num_church)
            results_dict[county]['cafe'].append(num_cafe)
            results_dict[county]['num_amenities'].append(num_amenities)
        except:
            results_dict[county] = {
                'population': [vals['population']],
                'pubs': [num_pubs],
                'schools': [num_schools],
                'church': [num_church],
                'cafe': [num_cafe],
                'num_amenities': [num_amenities]
                }
        try:
            overall_dict['population'].append(vals['population'])
            overall_dict['pubs'].append(num_pubs)
            overall_dict['schools'].append(num_schools)
            overall_dict['church'].append(num_church)
            overall_dict['cafe'].append(num_cafe)
            overall_dict['num_amenities'].append(num_amenities)
        except:
            overall_dict = {
                'population': [vals['population']],
                'pubs': [num_pubs],
                'schools': [num_schools],
                'church': [num_church],
                'cafe': [num_cafe],
                'num_amenities': [num_amenities]
                }


df = pd.DataFrame(overall_dict)
df.loc[:, 'population_grouped'] = df.population.apply(
        lambda x: 100*np.round(x/100) if x < 1000 else 500*np.round(x/500) if x < 5000 else np.round(x/5000)*5000
        )

good = df.groupby('population_grouped').agg('mean').reset_index()
better_good = good[good.population_grouped <= 2000]

ls = [':', '-', '--', '-.']
things = ['pubs', 'schools', 'church', 'cafe']
fig, ax = plt.subplots(figsize=(20,12))
i = 0
for thing in things:
    plt.plot(better_good.population_grouped, better_good[thing], label=thing, ls=ls[i%len(ls)])
    i += 1

plt.xlabel('Population', fontsize=18)
plt.xticks(fontsize=16)
plt.ylabel('Average number per parish', fontsize=18)
plt.yticks(fontsize=16)
plt.title('Average number of facilities per parish', fontsize=20)
plt.legend(fontsize=16)
plt.tight_layout()
plt.savefig('facilities_per_parish.png')
plt.show()


masked = df[['pubs', 'schools', 'church', 'cafe']].apply(lambda x: x > 0)
masked.loc[:, 'population_grouped'] = df.population_grouped
good = masked.groupby('population_grouped').agg('mean').reset_index()
better_good = good[good.population_grouped <= 2000]

ls = [':', '-', '--', '-.']
things = ['pubs', 'schools', 'church', 'cafe']
fig, ax = plt.subplots(figsize=(20,12))
i = 0
for thing in things:
    plt.plot(better_good.population_grouped, better_good[thing], label=thing, ls=ls[i%len(ls)])
    i += 1

plt.xlabel('Population of a parish', fontsize=18)
plt.xticks(fontsize=16)
plt.ylabel('Probability of facility', fontsize=18)
plt.yticks(fontsize=16)
plt.title('Probability of a facility given a parish size', fontsize=20)
plt.legend(fontsize=16)
plt.tight_layout()
plt.savefig('probability_facilities_per_parish.png')
plt.show()
