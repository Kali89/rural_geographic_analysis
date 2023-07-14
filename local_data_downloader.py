import geopandas as gdp
import overpy
import pandas as pd
from shapely.geometry import Point
import json
from decimal import Decimal
import concurrent.futures
import numpy as np


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


df = gdp.read_file("geo_data/OA_2021_EW_BFC_V7.shp")
other_df = df.to_crs('EPSG:4326')
oa_region_lookup = pd.read_csv(
        'data/OAs_(2021)_to_Civil_Parish_and_Non-Civil_Parished_Areas_to_LTLA_to_UTLA_to_Region_to_Country_(May_2022)_Lookup_in_England_and_Wales.csv'
        )
to_keep = oa_region_lookup[[
    'OA21CD',
    'RGN22NM'
    ]].drop_duplicates()

merged = to_keep.merge(
        other_df,
        how='inner',
        on='OA21CD'
        )

drop_wales = merged[merged.RGN22NM != 'Wales']

region_order_list = drop_wales.groupby(['RGN22NM']).size().sort_values().index.values

def thread_function(region):
    print("Starting with {0}".format(region))
    api = overpy.Overpass(max_retry_count=5, retry_timeout=10, url="http://3.10.223.96/api/interpreter")
    frame = drop_wales[drop_wales.RGN22NM == region]
    try:
        with open('output_data/{0}_region_data_updated.json'.format(region), 'r') as f:
            already_loaded = json.load(f)
        with open('output_data/{0}_region_errors_updated.json'.format(region), 'r') as g:
            error_data = json.load(g)
        all_names = []
        error_codes = []
        for entry in already_loaded:
            already_name = entry['OA21CD']
            all_names.append(already_name)
        for entry in error_data:
            error_codes.append(entry)
        data_structure = already_loaded
    except:
        data_structure = []
        all_names = []
        error_codes = []
    sizey = frame.shape[0]
    i = 0
    for index, row_a in frame.iterrows():
        code_main = row_a['OA21CD']
        if code_main in all_names:
            i += 1
            continue
        geo = row_a['geometry']
        bounds = geo.bounds
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
                error_codes.append(code_main)
                print(
                        "Error on node {0} for region {1}".format(
                            code_main,
                            region
                            )
                        )

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
                error_codes.append(code_main)
                print(
                        "Error on relation {0} for region {1}".format(
                            code_main,
                            region
                            )
                        )

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
                print(
                        "Error on relation {0} for region {1}".format(
                            code_main,
                            region
                            )
                        )
                error_codes.append(code_main)

        data_structure.append({
                'OA21CD': code_main,
                'RGN22NM': region,
                'amenities': data_points}
                )
        if i % 50 == 0:
            print(
                    "Added {0} out of {1} for region {2} ({3:.2f}% done!)".format(
                        i,
                        sizey,
                        region,
                        100*i/sizey
                        )
                    )
        if i % np.round(sizey/80) == 0:
            json_string = json.dumps(data_structure, cls=DecimalEncoder)
            error_string = json.dumps(error_codes, cls=DecimalEncoder)
            with open('output_data/{0}_region_data_updated.json'.format(region), 'w') as f:
                f.write(json_string)
            with open('output_data/{0}_region_errors_updated.json'.format(region), 'w') as g:
                g.write(error_string)

            print(
                    "Added {0} out of {1} for region {2} ({3:.2f}% done!)".format(
                        i,
                        sizey,
                        region,
                        100*i/sizey
                        )
                    )
        i += 1
    print("Finished region {0}".format(region))
    json_string = json.dumps(data_structure, cls=DecimalEncoder)
    error_string = json.dumps(error_codes, cls=DecimalEncoder)
    with open('output_data/all_data_final_updated_{0}.json'.format(region), 'w') as f:
        f.write(json_string)
    with open('output_data/all_data_final_updated_errors_{0}.json'.format(region), 'w') as g:
        g.write(error_string)
    return {
            'region_name': region,
            'num_successes': len(data_structure),
            'num_errors': len(error_codes)
            }


with concurrent.futures.ThreadPoolExecutor() as executor:
    regions = {
            executor.submit(thread_function, region): region for region in new_region_list
            }
    for future in concurrent.futures.as_completed(regions):
        data = future.result()
        print("Finished region {0}: {1} successes and {2} failures".format(
            data['region_name'], data['num_successes'], data['num_errors']
            ))
