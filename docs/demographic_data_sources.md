# ISTAT Demographic Data

`scripts/03_integrate_demographics.py` expects an ISTAT census-section
("sezioni di censimento") polygon layer for Torino.

## Where to get it

- ISTAT's **Base territoriale e variabili censuarie** (2021 census):
  https://www.istat.it/it/archivio/104317
- Download the shapefile/geopackage for **Piemonte / Torino**, plus the
  matching census variable tables (population, age brackets, housing).
- Variables of interest for this project:
  - `P1` — total resident population
  - `P14` (or the nearest equivalent in your extract) — population aged 65+
  - housing density / number of occupied dwellings, if you want a housing
    pressure layer as well as an age-vulnerability layer

## Preparing the file

1. Join the census variable table to the section boundaries (by section ID)
   in QGIS or GeoPandas if they don't already come pre-joined.
2. Reproject/export to GeoJSON.
3. Save as `data/raw/istat_census_sections.geojson`.
4. If ISTAT's column codes differ from `P1`/`P14` in your specific extract,
   update `COLUMN_MAP` at the top of `03_integrate_demographics.py`.

## What the script does

It apportions each census section's population onto the 200m analysis grid
by area-weighted overlap (a simple areal interpolation — fine for a course
project; for higher accuracy you could dasymetrically weight by building
footprint area instead of raw polygon overlap).
