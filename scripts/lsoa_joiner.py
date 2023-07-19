import pandas as pd

parishes = pd.read_csv('lsoa_parishes.csv')
output_to_LAD_lookup = pd.read_csv('modified_output_area_to_LAD_lookup.csv', sep=',')
LAD_to_county_lookup = pd.read_csv('Local_Authority_District_to_County_(April_2021)_Lookup_in_England.csv')
LAD_to_region_lookup = pd.read_csv('Local_Authority_District_to_Region_(April_2021)_Lookup_in_England.csv')

merged_lookup = output_to_LAD_lookup.merge(
        LAD_to_region_lookup,
        how='inner',
        left_on='lad22cd',
        right_on='LAD21CD'
    )

merged_lookup = merged_lookup[
        [
            'lsoa21cd',
            'lad22nm',
            'lad22cd',
            'RGN21CD',
            'RGN21NM'
            ]
        ].drop_duplicates()

output_to_LAD_lookup[['oa21cd', 'lsoa21cd']].drop_duplicates().to_csv('oa_to_lsoa_lookup.csv', index=None)
del output_to_LAD_lookup
del LAD_to_county_lookup
del LAD_to_region_lookup

merged = parishes.merge(
        merged_lookup,
        how='left',
        left_on='mnemonic',
        right_on='lsoa21cd'
)

merged.to_csv('joined_population_data.csv', index=None)

