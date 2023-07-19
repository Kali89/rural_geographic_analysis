import pandas as pd

parishes = pd.read_csv('oa_parishes.csv')
parishes.loc[:, 'code'] = parishes.Area.apply(lambda x: x.split(':')[1])

output_to_LAD_lookup = pd.read_csv('modified_output_area_to_LAD_lookup.csv', sep=',')
LAD_to_county_lookup = pd.read_csv('Local_Authority_District_to_County_(April_2021)_Lookup_in_England.csv')
LAD_to_region_lookup = pd.read_csv('Local_Authority_District_to_Region_(April_2021)_Lookup_in_England.csv')

merged_lookup = output_to_LAD_lookup.merge(
        LAD_to_region_lookup,
        how='inner',
        left_on='lad22cd',
        right_on='LAD21CD'
    ).merge(
            LAD_to_county_lookup,
            how='inner',
            left_on='lad22cd',
            right_on='LAD21CD'
            )

merged_lookup = merged_lookup[
        [
            'oa21cd',
            'lad22nm',
            'lad22cd',
            'CTY21CD',
            'CTY21NM',
            'RGN21CD',
            'RGN21NM'
            ]
        ].drop_duplicates()

del output_to_LAD_lookup
del LAD_to_county_lookup
del LAD_to_region_lookup

merged = parishes.merge(
        merged_lookup,
        how='left',
        left_on='code',
        right_on='oa21cd'
)

merged.to_csv('joined_population_data.csv', index=None)

