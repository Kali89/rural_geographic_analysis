# An analysis of the rural parishes of England

This repository contains the code for downloading OpenStreetMap data (using the publicly accessible API) and joining it with various geographic data (provided by the UK Government, via Nomis and Geoportal.statistics.gov).

It also contains an analysis of that data.

## Key Files

`data_downloader.py` contains the code used to download data from OpenStreetMap. Points to note include the fact that we begin with a list of every output area in England and the shapefile of those output areas. We then request the bounding box of those shapefiles from OpenStreetMap and extract the amenities. For each amenity, we then check that it lies within an output area (allowing for non-square output areas!). If it is, we append it to a dictionary that ultimately gets written to a JSON file. We write a lot (after each data point) and the file is written in such a way that it can be stopped and restarted and won't request duplicate data. Additionally, there is a five second delay built it (for politeness). To run completely will take over 10 days.

`joiner.py` is responsible for the creation of `joined_population_data.csv`. This is just a simple join between output areas and parishes.

`UrbanRuralProduction.py` is where the bulk of the analysis takes place. In here we plot descriptive statistics, build models and make inferences.

## Notes

I've excluded the large data files that were taken from the Government services listed above. If it's not clear which ones they are and you'd like to re-run the analysis, let me know.

If there's anything in here that you think is especially interesting, let me know! Or if you've got any questions.

