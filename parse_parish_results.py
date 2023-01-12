import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures

lookup_df = pd.read_csv('oa_to_parishes.csv')

counties = [
        'Cumbria',
        'East Sussex',
        'Somerset',
        'Warwickshire',
        'Worcestershire',
        'Cambridgeshire',
        'North Yorkshire',
        'Gloucestershire'
]

pubs_dict = {}

def num_pubs(ams):
    return len([t for t in ams if t['amenity'] == 'pub'])


prediction_dict = {}

for county in counties:
    pub_list = []
    pop_list = []
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
    for key, value in sorted(parsed_data.items(), key = lambda x: x[1]['population']):
        population = value['population']
        pubs = num_pubs(value['amenities'])
        pub_list.append(pubs)
        pop_list.append(population)
        try:
            pubs_dict[county]['pubs'].append(pubs)
            pubs_dict[county]['population'].append(population)
        except:
            pubs_dict[county] = {
                    'pubs': [pubs],
                    'population': [population]
                    }

    train_x = np.array(np.log(pop_list)).reshape(-1,1))
    test_x = np.log(np.arange(1,2000)).reshape(-1,1)
    lr = LogisticRegression()
    lr.fit(train_x, np.array(pub_list).reshape(-1,1))
    predictions = lr.predict_proba(test_x)[:,1]
    prediction_dict[county] = predictions
    print("Finished {0}".format(county))


fig, ax = plt.subplots(figsize=(20,12))
for key, val in prediction_dict.items():
    plt.plot(np.log(np.arange(1,2000)), val, label=key)

plt.xlabel('Population', fontsize=18)
plt.xticks(fontsize=16)
plt.ylabel('Probabilty of having more than 1 pub', fontsize=18)
plt.yticks(fontsize=16)
plt.title('Probability of a parish being multi-pub', fontsize=20)
plt.legend(fontsize=18)
plt.tight_layout()
plt.savefig('prob_parish_multipub_log.png')
