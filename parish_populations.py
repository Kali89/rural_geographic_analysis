import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns

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
        'Oxfordshire'
]

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
            results_dict[county].append(vals['population'])
        except:
            results_dict[county] = [vals['population']]

ls = ['solid', 'dotted', 'dashed', 'dashdot']
fig, ax = plt.subplots(figsize=(20,12))
i = 0
for key, val in results_dict.items():
    sns.kdeplot(val, label=key, ls=ls[i%len(ls)], log_scale=True, clip=[0,50000])
    i+=1
plt.xlabel('Population', fontsize=18)
plt.xticks(fontsize=16)
plt.ylabel('Density', fontsize=18)
plt.yticks(fontsize=16)
plt.title('Population density of parishes')
plt.legend(fontsize=16)
plt.tight_layout()
plt.savefig("density_plot_combined.png")
plt.show()

