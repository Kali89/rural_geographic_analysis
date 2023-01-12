import geopandas as gdp
import overpy
import pandas as pd
from shapely.geometry import Point
import time
import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)

df = gdp.read_file("OA_2021_EW_BFE_V7.shp")
other_df = df.to_crs('EPSG:4326')
lsoa_df = pd.read_csv('joined_population_data.csv')
to_keep = lsoa_df[
        [
            'Area', 
            'lsoa21cd',
            '2021',
            'lad22nm',
            'RGN21NM'
            
        ]]
to_keep.columns = ['LSOANM', 'LSOA21NM', 'Population', 'LADNM', 'RGNNM']

lookup_df = pd.read_csv('oa_to_lsoa_lookup.csv')
merged_location = other_df.merge(lookup_df, how='inner', left_on='OA21CD', right_on='oa21cd')

to_keep.loc[:, 'code'] = to_keep.name.apply(lambda x: x.split(':')[0].strip())
to_keep.loc[:, 'name'] = to_keep.name.apply(lambda x: x.split(':')[1].strip())

api = overpy.Overpass(max_retry_count=5, retry_timeout=30)

data_structure = []
i = 0
for index, row_a in to_keep.iterrows():
    name_main = row_a['name']
    print("Querying for {0}".format(name_main))
    code_main = row_a['code']
    population_main = row_a['total']
    geo = other_df[other_df.PARNCP21CD == code_main].geometry
    if geo.shape[0] == 0:
        geo = other_df[other_df.PARNCP21NM == name_main].geometry
    if geo.shape[0] == 0:
        print("Can't find shapefile for {0}".format(name_main))
        continue
    bounds = geo.bounds.values[0]
    bbox = (bounds[1], bounds[0], bounds[3], bounds[2])
    query = """
    (node["amenity"]{0};
    way["amenity"]{0};
    relation["amenity"]{0};
    );
    out body;
    >;
    out skel qt;
    """.format(bbox)

    results = api.query(query.strip())

    data_points = []

    for row in results.nodes:
        lat = row.lat
        lon = row.lon
        point = Point(lon, lat)
        if geo.values[0].contains(point):
            if 'amenity' in row.tags:
                amenity = row.tags.get('amenity', 'N/A')
                name = row.tags.get('name', 'N/A')
                other_tags = row.tags
                data_type = 'node'

                data_point = {
                        'name': name,
                        'amenity': amenity,
                        'data_type': data_type,
                        'lat': lat,
                        'lon': lon,
                        'other_tags': other_tags
                        }
                data_points.append(data_point)

    for row in results.relations:
        if 'amenity' in row.tags:
            lat = row.members[0].resolve().nodes[0].lat
            lon = row.members[0].resolve().nodes[0].lon
            point = Point(lon, lat)
            if geo.values[0].contains(point):
                amenity = row.tags.get('amenity', 'N/A')
                name = row.tags.get('name', 'N/A')

                other_tags = row.tags
                data_type = 'relation'

                data_point = {
                        'name': name,
                        'amenity': amenity,
                        'data_type': data_type,
                        'lat': lat,
                        'lon': lon,
                        'other_tags': other_tags
                        }
                data_points.append(data_point)

    for row in results.ways:
        if 'amenity' in row.tags:
            lat = row.nodes[0].lat
            lon = row.nodes[0].lon
            point = Point(lon, lat)
            if geo.values[0].contains(point):
                amenity = row.tags.get('amenity', 'N/A')
                name = row.tags.get('name', 'N/A')
                other_tags = row.tags
                data_type = 'way'

                data_point = {
                        'name': name,
                        'amenity': amenity,
                        'data_type': data_type,
                        'lat': lat,
                        'lon': lon,
                        'other_tags': other_tags
                        }
                data_points.append(data_point)

        
    data_structure.append({
            'name': name_main,
            'code': code_main,
            'population': population_main,
            'amenities': data_points}
            )

    print("Added {0} as number {1}".format(name_main, i))
    time.sleep(5)
    json_string = json.dumps(data_structure, cls=DecimalEncoder)
    with open('north_yorkshire_data_more.json', 'w') as f:
        f.write(json_string)
    i += 1

json_string = json.dumps(data_structure, cls=DecimalEncoder)
with open('north_yorkshire_data.json', 'w') as f:
    f.write(json_string)
