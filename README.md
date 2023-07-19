# An analysis of the rural parishes of England

This repository contains the code for downloading OpenStreetMap data (using the publicly accessible API) and joining it with various geographic data (provided by the UK Government, via Nomis and Geoportal.statistics.gov).

It also contains an analysis of that data.

It also contains a presentation of a few of these things for IC2S 2023.

You could argue it contains too many things. If you're lost, let me try to help point you in the right direction...

## Key Files

`scripts/local_data_downloader.py`: Used to download data from OpenStreetMap. It requires you to set up your own OpenStreetMap server. Points to note include the fact that we begin with a list of every output area in England and the shapefile of those output areas. We then request the bounding box of those shapefiles from OpenStreetMap and extract the amenities. For each amenity, we then check that it lies within an output area (allowing for non-square output areas!). If it is, we append it to a dictionary that ultimately gets written to a JSON file. We write a lot (after each data point) and the file is written in such a way that it can be stopped and restarted and won't request duplicate data.

`scripts/data_downloader.py`: As above, except it doesn't require setting up your own server. Howerver, there is a five second delay built it (for politeness). To run completely will take over 10 days.

`analysis_notebooks/HousePriceStats.ipynb` includes a bunch of figures and procedures, and at some point tries to work out the impact of a pub on house sale prices (but not hugely successfully).

`analysis_notebooks/PowerLaws.ipynb` primarily tries to understand whether traditional urbans scaling laws work for rural environments. And mainly concludes that they don't.

`analysis_notebooks/PlottingDiffKernel.ipynb` is all about making big beautiful maps of the UK.

`analysis_notebooks/HousePriceStats.ipynb` generates summary statistics on UK house prices based on the entire house sale history file.

## A cool picture

![Correlation matrix of various features of interest](results/correlation_matrix.png?raw=true "Correlation Matrix of features of interest")

## Notes

I've excluded the large data files that were taken from the Government services listed above. If it's not clear which ones they are and you'd like to re-run the analysis, let me know.

If there's anything in here that you think is especially interesting, let me know! Or if you've got any questions.

## Files to Download

- Population from the 2021 Census: https://www.nomisweb.co.uk/sources/census_2021_bulk (https://www.nomisweb.co.uk/output/census/2021/census2021-ts001.zip)
- Best fit lookup from the 2021 OAs to Parishes, Counties, Regions and Countries (https://geoportal.statistics.gov.uk/datasets/ons::oas-2021-to-civil-parish-and-non-civil-parished-areas-to-ltla-to-utla-to-region-to-country-may-2022-lookup-in-england-and-wales-1/about)
- Urban rural lookup of 2011 OAs (https://geoportal.statistics.gov.uk/datasets/rural-urban-classification-2011-of-output-areas-in-england-and-wales-1/about)
- Lookup between 2011 OAs and 2021 OAs (https://geoportal.statistics.gov.uk/datasets/ons::oa-2011-to-oa-2021-to-local-authority-district-2022-for-england-and-wales-lookup-version-2/about)
- English indices of multiple deprivation (at 2011 LSOA level) (https://geoportal.statistics.gov.uk/datasets/ons::index-of-multiple-deprivation-dec-2019-lookup-in-england/about)
- An OA to LSOA lookup for 2011 (https://geoportal.statistics.gov.uk/datasets/ons::output-area-to-lower-layer-super-output-area-to-middle-layer-super-output-area-to-local-authority-district-december-2011-lookup-in-england-and-wales-1/about)
- Boundary file for all the Output Areas in the UK (https://geoportal.statistics.gov.uk/datasets/ons::output-areas-dec-2021-boundaries-full-clipped-ew-bfc/about)
