"""
03_integrate_demographics.py

Joins ISTAT census-section demographic data (population, elderly share,
housing density) onto the same 200m grid used for the heat proxy, so the
final Kepler.gl scene can answer: do the most vulnerable residents live in
the most severe heat traps?

Expected input:
    data/raw/istat_census_sections.geojson
        - an ISTAT "sezioni di censimento" polygon layer for Torino,
          downloaded from https://www.istat.it/it/archivio/104317
          (Base territoriale e variabili censuarie), containing at least:
            P1            total population
            P14           population aged 65+
            (or your local equivalents — adjust COLUMN_MAP below)

Output:
    data/processed/torino_demographics_grid.geojson
        grid cells carrying population_count, elderly_share, housing_density

Requirements: geopandas, pandas
"""

import os
import geopandas as gpd
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

ISTAT_PATH = os.path.join(RAW_DIR, "istat_census_sections.geojson")
HEAT_GRID_PATH = os.path.join(PROCESSED_DIR, "torino_heat_grid.geojson")
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "torino_demographics_grid.geojson")

METRIC_CRS = "EPSG:32632"
GEOGRAPHIC_CRS = "EPSG:4326"

# Map ISTAT's raw column codes to readable names used downstream.
# Update these to match the actual columns in your ISTAT extract.
COLUMN_MAP = {
    "P1": "population_count",
    "P14": "population_65plus",
}


def load_istat(path: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    gdf = gdf.rename(columns=COLUMN_MAP)
    keep_cols = ["geometry", "population_count", "population_65plus"]
    return gdf[[c for c in keep_cols if c in gdf.columns]]


def main():
    if not os.path.exists(ISTAT_PATH):
        raise FileNotFoundError(
            f"Missing {ISTAT_PATH}.\n"
            "Download ISTAT census-section boundaries + variables for Torino "
            "and place them at data/raw/istat_census_sections.geojson "
            "(see docs/demographic_data_sources.md)."
        )

    print("📖 Loading ISTAT demographic data and the heat grid...")
    istat = load_istat(ISTAT_PATH)
    heat_grid = gpd.read_file(HEAT_GRID_PATH)

    istat_metric = istat.to_crs(METRIC_CRS)
    grid_metric = heat_grid.to_crs(METRIC_CRS)
    grid_metric["grid_id"] = range(len(grid_metric))

    print("🔬 Apportioning population onto the heat grid by area overlap...")
    istat_metric["section_area"] = istat_metric.geometry.area
    joined = gpd.overlay(istat_metric, grid_metric, how="intersection")
    joined["overlap_area"] = joined.geometry.area
    joined["area_fraction"] = joined["overlap_area"] / joined["section_area"]

    for col in ["population_count", "population_65plus"]:
        if col in joined.columns:
            joined[col] = joined[col] * joined["area_fraction"]

    agg = joined.groupby("grid_id")[
        [c for c in ["population_count", "population_65plus"] if c in joined.columns]
    ].sum()

    grid_metric = grid_metric.merge(agg, on="grid_id", how="left").fillna(0)

    if "population_count" in grid_metric.columns and "population_65plus" in grid_metric.columns:
        grid_metric["elderly_share"] = (
            grid_metric["population_65plus"] / grid_metric["population_count"].replace(0, pd.NA)
        ).fillna(0)

    print("💾 Converting back to WGS84 and saving...")
    grid_final = grid_metric.to_crs(GEOGRAPHIC_CRS)
    grid_final.to_file(OUTPUT_PATH, driver="GeoJSON")

    print(f"✅ Success! Created: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
