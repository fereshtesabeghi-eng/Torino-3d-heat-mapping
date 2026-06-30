"""
01_fetch_osm_geometry.py

Pulls Torino's 3D building geometry and pedestrian network from OpenStreetMap
using OSMnx, cleans the attributes Kepler.gl needs, and exports two GeoJSONs:

    data/processed/torino_buildings_3d.geojson
    data/processed/torino_pedestrian_network.geojson

Requirements: osmnx>=2.0, geopandas, pandas
"""

import os
import osmnx as ox
import geopandas as gpd
import pandas as pd

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PLACE_NAME = "Turin, Italy"


def fetch_pedestrian_network(place_name: str) -> gpd.GeoDataFrame:
    print("↳ Downloading pedestrian network...")
    walk_graph = ox.graph_from_place(place_name, network_type="walk")
    # osmnx 2.0 returns a single GeoDataFrame when nodes=False
    pedestrian_edges = ox.graph_to_gdfs(walk_graph, nodes=False, edges=True)
    return pedestrian_edges[["geometry", "name", "highway"]].copy()


def calculate_height(row: pd.Series) -> float:
    """Resolve a usable building height in meters from OSM tags."""
    if "height" in row and pd.notna(row["height"]):
        try:
            return float(str(row["height"]).replace("m", "").strip())
        except ValueError:
            pass

    if "building:levels" in row and pd.notna(row["building:levels"]):
        try:
            return float(row["building:levels"]) * 3.2
        except ValueError:
            pass

    return 15.0  # baseline default for missing data


def fetch_buildings_3d(place_name: str) -> gpd.GeoDataFrame:
    print("↳ Downloading building footprints...")
    building_tags = {"building": True}
    buildings = ox.features_from_place(place_name, tags=building_tags)
    buildings = buildings.reset_index()

    print("↳ Cleaning building height attributes...")
    buildings["calculated_height"] = buildings.apply(calculate_height, axis=1)

    buildings_cleaned = buildings[
        buildings["geometry"].type.isin(["Polygon", "MultiPolygon"])
    ].copy()

    return buildings_cleaned[["geometry", "calculated_height", "building"]]


def main():
    print(f"🔄 Fetching data for {PLACE_NAME}... this might take a minute.")

    pedestrian_cleaned = fetch_pedestrian_network(PLACE_NAME)
    buildings_final = fetch_buildings_3d(PLACE_NAME)

    print("💾 Saving files to disk...")
    pedestrian_path = os.path.join(OUTPUT_DIR, "torino_pedestrian_network.geojson")
    buildings_path = os.path.join(OUTPUT_DIR, "torino_buildings_3d.geojson")

    pedestrian_cleaned.to_file(pedestrian_path, driver="GeoJSON")
    buildings_final.to_file(buildings_path, driver="GeoJSON")

    print("✅ Success! Your files are ready for Kepler.gl:")
    print(f"   - {pedestrian_path}")
    print(f"   - {buildings_path}")


if __name__ == "__main__":
    main()
