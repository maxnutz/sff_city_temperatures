# sff_city_temperatures

Evaluation of temperature Data on Siebenbrunnenplatz, Vienna.

## Initial frontend framework

This repository includes a minimal Python/HTML frontend scaffold for the temperature dashboard and a GitHub Pages deployment setup.

## GitHub Pages

The public GitHub Pages site is available at:

- https://maxnutz.github.io/sff_city_temperatures/

The pages build generates interactive Plotly charts as standalone HTML files inside `docs/plots/`.

## Setup (Conda — recommended)

Create and activate the `webpage` Conda environment (recommended):

```bash
conda env create -f environment.yml
conda activate webpage
```

If you prefer a pip-only setup, you can still use:

```bash
python -m pip install -r requirements.txt
```

## Backend scaffold

The Python backend scaffold is in `backend/temperature_backend.py` and includes:

- weather-station time series plotting
- single-sensor time series plotting
- multi-sensor selected-day time series plotting
- sensor max-temperature map plotting on OpenStreetMap
- dummy heat-stress evaluation (daily weather-station maxima)

Dummy CSV input data is committed under `data/dummy_input/`:

- `weather_station.csv` (hourly data for 10 days)
- `sensor_north.csv`, `sensor_south.csv`, `sensor_east.csv`, `sensor_west.csv` (5-minute data for 10 days)

## Generate Plotly assets locally

Activate the environment and run the generator:

```bash
conda activate webpage
python scripts/generate_plotly_assets.py
```

Then open `/tmp/workspace/maxnutz/sff_city_temperatures/docs/index.html` in a browser.

## Run backend tests

```bash
python -m unittest discover -s tests -q
```

## Run Flask scaffold locally

Activate the environment and start the app:

```bash
conda activate webpage
python app.py
```

Open `http://localhost:8000/` to view the initial four-panel layout.
