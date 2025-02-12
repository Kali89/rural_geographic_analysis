import pandas as pd
import numpy as np
import subprocess

print("Adding UPRN to house price sales")

## https://ubdc.ac.uk/data-services/data-catalogue/housing-data/price-paid-data-to-uprn-lookup/
transaction_to_uprn_lookup = pd.read_csv('../data/my_updated_ppdid_uprn.csv')

output_file = '../data/pp-complete-with-uprn.csv'
chunksize=100000
columns = ['id', 'price', 'date', 'postcode', 'property_type', 'old_new', 'duration', 'paon', 'saon', 'street', 'locality', 'town', 'district', 'county', 'ppd_category', 'record_status']
i = 0

## Add header row
with open(output_file, 'w') as f:
    f.write(','.join(columns + ['uprn']) + '\n')

## https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads
for chunk in pd.read_csv('../data/pp-complete.csv.1', chunksize=chunksize, header=0, names=columns):
        df = chunk
        df['date'] = pd.to_datetime(df.date).apply(lambda x: x.date())
        merged = df.merge(transaction_to_uprn_lookup, how='inner', left_on='id', right_on='transactionid').drop(columns='transactionid')
        merged.to_csv(output_file, mode="a", header=False, index=False)
        if i % 20 == 0:
            print("Done chunk {0}".format(i))
        i += 1

## Now we have price paid with the UPRN (for whichever ones we've found)
## Next we filter the UPRN to lat/lon lookup to only include UPRNs that have
## sold and we have matched

#print("Creating a list of UPRNs to get Geographic information about")
#
#command = """awk -F ',' '{print $(NF-2)}' ../data/pp-complete-with-uprn.csv | tail -n +2
#| sort | uniq > ../data/uprns_of_interest.txt"""
#
#process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
#process.wait()
#print(process.returncode)

print("Filtering the list of UPRN to geo lookups")

to_filter_with = pd.read_csv(
    '../data/uprns_of_interest.csv',
    index_col=None,
    header=0,
    names=['uprn']
)


output_file = '../data/filtered_osopenuprn.csv'
chunksize=100000
input_columns = ['uprn', 'x_coord', 'y_coord', 'lat', 'lon']
i = 0
with open(output_file, 'w') as f:
    f.write(','.join(input_columns) + '\n')

## https://osdatahub.os.uk/downloads/open/OpenUPRN
for chunk in pd.read_csv('../data/osopenuprn_202310.csv', chunksize=chunksize, header=0, names=input_columns):
        df = chunk
        merged = to_filter_with.merge(df, how='inner', on='uprn')
        merged.to_csv(output_file, mode="a", index=False, header=False)
        if i % 20 == 0:
            print("Done chunk {0}".format(i))
        i += 1

del transaction_to_uprn_lookup
del to_filter_with

print("Adding geo information to the house sales")

kept_lookup = pd.read_csv('../data/filtered_osopenuprn.csv', index_col=None)

output_file = '../data/pp-complete-with-location.csv'
chunksize=100000
input_columns = ['uprn', 'x_coord', 'y_coord', 'lat', 'lon']
columns = ['id', 'price', 'date', 'postcode', 'property_type', 'old_new', 'duration', 'paon', 'saon', 'street', 'locality', 'town', 'district', 'county', 'ppd_category', 'record_status', 'uprn']
i = 0
with open(output_file, 'w') as f:
    f.write(','.join(columns + ['x_coord', 'y_coord', 'lat', 'lon']) + '\n')
for chunk in pd.read_csv('../data/pp-complete-with-uprn.csv', chunksize=chunksize, header=0, names=columns):
        df = chunk
        merged = df.merge(kept_lookup, how='inner', on='uprn')
        merged.to_csv(output_file, mode="a", index=False, header=False)
        if i % 20 == 0:
            print("Done chunk {0}".format(i))
        i += 1
