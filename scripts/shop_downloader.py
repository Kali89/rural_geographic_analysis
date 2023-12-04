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
oa_df = pd.read_csv('joined_population_data.csv')
to_keep = oa_df[
        [
            'Area', 
            'code',
            '2021',
            'lad22nm',
            'CTY21NM',
            'RGN21NM'
            
        ]].drop_duplicates()

to_keep.columns = ['Area', 'Code', 'Population', 'LADNM', 'CTYNM', 'RGNNM']

merged = to_keep.merge(other_df, how='inner', left_on='Code', right_on='OA21CD')
merged.loc[:, 'population_density'] = merged.Population / merged.SHAPE_Area

county_order_list = merged.groupby(['CTYNM']).size().sort_values().index.values

api = overpy.Overpass(max_retry_count=5, retry_timeout=30)

for county in county_order_list:
    frame = merged[merged.CTYNM == county]
    try:
        with open('{0}_county_data.json'.format(county), 'r') as f:
            already_loaded = json.load(f)
        all_names = []
        for entry in already_loaded:
            already_name = entry['code']
            all_names.append(already_name)
        data_structure = already_loaded
    except:
        data_structure = []
        all_names = []
    sizey = frame.shape[0]
    i = 0
    for index, row_a in frame.iterrows():
        start_time = time.time()
        code_main = row_a['Code']
        lad_main = row_a['LADNM']
        cty_main = row_a['CTYNM']
        rgn_main = row_a['RGNNM']
        if code_main in all_names:
            print("Already have {0} as number {1} out of {2} - continuing".format(code_main, i, sizey))
            i += 1
            continue
        print("Querying for {0}".format(code_main))
        population_main = row_a['Population']
        geo = row_a['geometry']
        bounds = geo.bounds
        bbox = (bounds[1], bounds[0], bounds[3], bounds[2])
        query = """
        (node["shop"]{0};
        way["shop"]{0};
        relation["shop"]{0};
        );
        out body;
        >;
        out skel qt;
        """.format(bbox)

        results = api.query(query.strip())

        data_points = []

        for row in results.nodes:
            try:
                lat = row.lat
                lon = row.lon
                point = Point(lon, lat)
                if geo.contains(point):
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
            except:
                print("Error on node {0} - continuing".format(code_main))

        for row in results.relations:
            try:
                if 'amenity' in row.tags:
                    lat = row.members[0].resolve().nodes[0].lat
                    lon = row.members[0].resolve().nodes[0].lon
                    point = Point(lon, lat)
                    if geo.contains(point):
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
            except:
                print("Error on relation {0} - continuing".format(code_main))

        for row in results.ways:
            try:
                if 'amenity' in row.tags:
                    lat = row.nodes[0].lat
                    lon = row.nodes[0].lon
                    point = Point(lon, lat)
                    if geo.contains(point):
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
            except:
                print("Error on way {0} - continuing".format(code_main))

        data_structure.append({
                'county': county,
                'code': code_main,
                'lad': lad_main,
                'county': cty_main,
                'rgn_main': rgn_main,
                'population': population_main,
                'amenities': data_points}
                )

        print("Added {0} as number {1} on county {2} (out of {3})".format(code_main, i, county, sizey))
        time.sleep(5)
        json_string = json.dumps(data_structure, cls=DecimalEncoder)
        with open('{0}_county_data.json'.format(county), 'w') as f:
            f.write(json_string)
        i += 1
        end_time = time.time()
        print("Time taken: {0}".format(end_time - start_time))
    print("Finished county {0}".format(county))
    json_string = json.dumps(data_structure, cls=DecimalEncoder)
    with open('all_data_final_{0}.json'.format(county), 'w') as f:
        f.write(json_string)
