import pandas as pd
import numpy as np

## https://ubdc.ac.uk/data-services/data-catalogue/housing-data/price-paid-data-to-uprn-lookup/
transaction_to_uprn_lookup = pd.read_csv('../data/ppdid_uprn_usrn.csv')
columns = ['id', 'price', 'date', 'postcode', 'property_type', 'old_new', 'duration', 'paon', 'saon', 'street', 'locality', 'town', 'district', 'county', 'ppd_category', 'record_status']

grouped_version = pd.read_csv(
    '../data/pp-complete.csv.1',
    header=0,
    names=columns
)

handy = grouped_version.merge(
    transaction_to_uprn_lookup[['uprn', 'transactionid', 'parentuprn', 'usrn']],
    how='inner',
    left_on='id',
    right_on='transactionid'
)

lookup = handy[['postcode', 'paon', 'saon', 'uprn']].drop_duplicates()

great = grouped_version.merge(
    lookup,
    how='inner',
    on=['postcode', 'paon', 'saon']
)

great.to_csv('../data/pp-complete-with-uprn.csv')
