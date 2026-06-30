# Composing the 3D Scene in Kepler.gl

This is the manual styling pass once you have the three GeoJSONs from the
`scripts/` pipeline:

- `torino_buildings_3d.geojson`
- `torino_pedestrian_network.geojson`
- `torino_heat_grid.geojson`
- (optional) `torino_demographics_grid.geojson`

## 1. Load the canvas

1. Go to [kepler.gl/demo](https://kepler.gl/demo).
2. Drag and drop the GeoJSON files into the browser window at the same time.

## 2. Layer 1 — Heat proxy (the base)

- Expand `torino_heat_grid`.
- Color by `temperature_proxy`.
- Use a diverging palette (deep blue → bright red/orange).
- Set layer opacity to ~0.4–0.5 so it reads as a glow painted on the ground
  rather than a solid mask.

## 3. Layer 2 — 3D buildings (the structure)

- Expand `torino_buildings_3d`.
- Click the 3D map icon (top right) to enable tilt.
- Toggle **Height** on, set the height field to `calculated_height`.
- Set fill color to a uniform dark gray/charcoal for contrast against the
  heat layer below — this is what makes the "urban canyons" visually pop.
- Right-click + drag to tilt the camera and look down the street canyons.

## 4. Layer 3 — Pedestrian network (the human element)

- Expand `torino_pedestrian_network`.
- Color: stark white or neon cyan.
- Reduce stroke width so it reads as delicate webbing threaded between the
  buildings — this is where people actually walk through the heat traps.

## 5. Optional Layer — Demographics

- Add `torino_demographics_grid` as a **Hexbin** or **Grid** layer.
- Aggregate by `population_count` or `elderly_share`.
- This is the layer that lets you actually answer the project's core
  question: are the most vulnerable residents walking through the worst
  heat traps?

## 6. Save your work

Kepler's exported `kepler_gl.html` and a saved `kepler_config.json` can each
be 50MB+ once your full-city datasets are embedded. They are intentionally
**not** committed to this repo (see `.gitignore`). To share them:

- Use [Git LFS](https://git-lfs.github.com/) if you want them versioned, or
- Export just the JSON **config** (Kepler → Share → Export Map → Config
  Only) and store the data files separately, or
- Host the exported HTML on GitHub Pages / Netlify and link it from the
  README instead of committing the file.
