# Upgrading the Heat Proxy to Real Microclimate Data

`scripts/02_generate_heat_grid.py` ships with a density-based
`temperature_proxy` (28°C baseline + up to 6.5°C from building density) so
the pipeline runs end-to-end without external imagery. For a research-grade
version, replace that column with one of the following.

## Option A — Land Surface Temperature (satellite)

- **Sentinel-3 SLSTR** (1km, daily revisit) or **Landsat 8/9 TIRS** (100m,
  16-day revisit) via [Copernicus Browser](https://browser.dataspace.copernicus.eu/)
  or [USGS EarthExplorer](https://earthexplorer.usgs.gov/).
- Pick a clear-sky day from a recent heatwave (late June 2026).
- Convert thermal band DN → brightness temperature → LST (mono-window or
  split-window algorithm depending on sensor).
- Resample/zonal-mean the LST raster onto the same 200m grid used in
  `02_generate_heat_grid.py`, replacing `temperature_proxy`.

## Option B — Mean Radiant Temperature simulation (street-level)

- [SOLWEIG](https://umep-docs.readthedocs.io/) (part of the UMEP QGIS
  plugin) simulates MRT at street level using a digital surface model built
  from your building heights plus land cover.
- Best run on a single neighborhood (e.g. San Salvario or Barriera di
  Milano) rather than the whole city — it's computationally heavier than a
  density proxy and gives a much more physically grounded "urban canyon"
  signal.
- Output a raster or point grid of MRT, then join it to the same grid
  schema (`grid_id`, `geometry`, `temperature_proxy`) so it drops into the
  existing Kepler.gl layer config.

Either option keeps the rest of the pipeline (buildings, pedestrian
network, demographics) unchanged — only `torino_heat_grid.geojson`'s source
changes.
