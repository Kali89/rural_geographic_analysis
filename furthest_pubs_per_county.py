import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist
from math import sin, cos, sqrt, atan2, radians

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

def get_distance(point1, point2):
    R = 6370
    lat1 = radians(point1[0])  #insert value
    lon1 = radians(point1[1])
    lat2 = radians(point2[0])
    lon2 = radians(point2[1])

    dlon = lon2 - lon1
    dlat = lat2- lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance


close_dict = {}

for county in counties:
    pub_list = []
    with open("all_data_final_{0}.json".format(county), 'r') as f:
        data = json.loads(f.read())
    for entry in data:
        ams = entry['amenities']
        for a in ams:
            if a['amenity'] == 'pub':
                lat = float(a['lat'])
                lon = float(a['lon'])
                pub_list.append({
                    'code': entry['code'],
                    'lat': lat,
                    'lon': lon,
                    'name': a['name']
                    })
    all_pubs = pd.DataFrame(pub_list)
    all_points = all_pubs[['lat', 'lon']].values
    dm = cdist(all_points, all_points, get_distance)
    df = pd.DataFrame(dm, index=all_pubs.name, columns=all_pubs.name)
    closest_pub_pairs = []
    for name, frame in df.iterrows():
        other_name = frame.sort_values().index[1]
        val = frame.sort_values()[1]
        closest_pub_pairs.append({
            'pub': name,
            'neighbour': other_name,
            'distance': val
            })
    neighbour_frame = pd.DataFrame(closest_pub_pairs)
    close_dict[county] = neighbour_frame

for county, frame in close_dict.items():
    most_isolated_pub = frame.sort_values(by='distance', ascending=False).head(1)
    print("{0}: {1}: {2:.2f}km".format(county, most_isolated_pub.pub.values[0], most_isolated_pub.distance.values[0]))
