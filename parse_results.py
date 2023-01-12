import pandas as pd
import json
from itertools import combinations

with open('Somerset_county_data.json', 'r') as f:
    data = json.load(f)

amenities_to_ignore = [
        'grave_yard',
        'post_box',
        'bench',
        'parking',
        'recycling',
        'telephone',
        'bicycle_parking',
        'waste_basket',
        'shelter',
        'grit_bin',
        'telephone',
        'hunting_stand',
        'fuel',
        'toilets'
        ]

base_dict = {
        'pub': 0,
        'school': 0,
        'cafe': 0,
        'church': 0,
        'village_hall': 0,
        'post_office': 0,
        'other': 0 
        }

other_amenities = {}

def extract_amenities(name, x, base_dict=base_dict):
    my_base_dict = base_dict.copy()
    for entry in x:
        amenity_type = entry['amenity']
        if amenity_type == 'pub':
            my_base_dict['pub'] += 1
        elif amenity_type in ['community_centre', 'townhall']:
            my_base_dict['village_hall'] += 1 
        elif amenity_type == 'place_of_worship':
            my_base_dict['church'] += 1 
        elif amenity_type == 'cafe':
            my_base_dict['cafe'] += 1 
        elif amenity_type == 'school':
            my_base_dict['school'] += 1 
        elif amenity_type == 'post_office':
            my_base_dict['post_office'] += 1 
        elif amenity_type in amenities_to_ignore:
            continue
        else:
            my_base_dict['other'] += 1 
            try:
                other_amenities[name].append(amenity_type)
            except:
                other_amenities[name] = [amenity_type]
    return my_base_dict

output = []
for entry in data:
    name = entry['code']
    population = entry['population']
    amenities = extract_amenities(name, entry['amenities'])
    output.append(
            {
                'name': name,
                'population': population,
                'amenities': amenities
                
                }

            )


all_options = [b for a in range(1, len(base_dict)) for b in combinations(base_dict.keys(), a)]

for entry in sorted(output, key=lambda x: x['population']):
    values = [a for a, b in entry['amenities'].items() if b>0]
    ones_to_eliminate = [b for a in range(1,len(values)+1) for b in combinations(values, a)]
    to_eliminate = []
    for ah in ones_to_eliminate:
        if ah in all_options:
            to_eliminate.append(ah)
    if to_eliminate:
        name = entry['name']
        population = entry['population']
        print("{0} (population: {1})".format(name, population))
        print("Smallest place to have:")
        for c in to_eliminate:
            print(c)
        all_options = [x for x in all_options if x not in to_eliminate]
