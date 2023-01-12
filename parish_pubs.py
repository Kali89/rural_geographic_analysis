import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import pymc3 as pm

lookup_df = pd.read_csv('oa_to_parishes.csv')

counties = [
#        'Cumbria',
#        'East Sussex',
#        'Somerset',
#        'Warwickshire',
#        'Worcestershire',
#        'Cambridgeshire',
#        'North Yorkshire',
#        'Gloucestershire',
        'Oxfordshire'
]

def num_pubs(ams):
    return len([t for t in ams if t['amenity'] == 'pub'])

results_dict = {}

for county in counties:
    with open("all_data_final_{0}.json".format(county), 'r') as f:
        data = json.loads(f.read())
    parsed_data = {}
    for entry in data:
        parish_name = lookup_df[lookup_df.OA21CD == entry['code']].PAR22NM.values[0]
        if 'unparished' in parish_name:
            continue
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
        try:
            results_dict[county]['population'].append(vals['population'])
            results_dict[county]['pubs'].append(num_pubs(vals['amenities']))
        except:
            results_dict[county] = {
                    'population': [vals['population']],
                    'pubs': [num_pubs(vals['amenities'])]
                    }

keya = list(results_dict.keys())[0]
populations = []
pubs = []
for i, j in sorted(zip(results_dict[keya]['population'], results_dict[keya]['pubs']), key=lambda x: x[0]):
    populations.append(i) 
    pubs.append(j) 

model = pm.Model()
with model:
    lambda_1 = pm.Beta('lambda_1', alpha=2, beta=2)
    lambda_2 = pm.Beta('lambda_2', alpha=2, beta=2)
    tau = pm.DiscreteUniform("tau", lower=np.min(populations), upper=np.max(populations))

with model:
    idx = np.arange(len(populations))
    lambda_ = pm.math.switch(tau > idx, lambda_1, lambda_2)

with model:
    observation = pm.Binomial('y_obs', p=lambda_, n=populations, observed=pubs)
    step = pm.Metropolis()
    trace = pm.sample(10000, step=step)

