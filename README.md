# sff_city_temperatures

Evaluation of temperature Data on Siebenbrunnenplatz, Vienna.

## Initial frontend framework

This repository includes a minimal Python/HTML frontend scaffold for the temperature dashboard and a GitHub Pages deployment setup.

## GitHub Pages

The public GitHub Pages site is available at:

- https://maxnutz.github.io/sff_city_temperatures/

The pages build generates interactive Plotly charts as standalone HTML files inside `docs/plots/`.
The home page links to one static page per dashboard element:

- `docs/four-timeseries.html`
- `docs/combined-timeseries.html`
- `docs/static-information.html`
- `docs/map-scatter.html`

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

folder `backend` holds the python code for data evaluation

### Code Structure:
- main Class `Sensor`: 
  - init: Sensors are differentiated by their name. All names are in the dict `SENSOR_LOCATIONS`
  - :param: df: holds the 5-minute data series of the sensor
  - :param: df_max: holds the maximum temperature per day of the sensor
  - :method: plot_time_series: Plots one line per day from 00h to 24h of self.df-Timeseries of this sensor. &rarr; output in `docs/plots/{bankomat,baum,cafe,telefonzelle}_time_series.html` to be integrated on the "Four Temperature Time Series" - site
- function `plot_sensor_max_temperature_map`: _does not work yet_ &rarr; output will be `docs/plots/map.html`
- function `plot_one_day_for_all_locations`: Creates a figure over one day including the daily lines for all locations &rarr; output is `docs/plots/combined.html`

- function `plot_weather_station_time_series` _does not work yet_ 

## Run Flask scaffold locally

Activate the environment and start the app:

```bash
conda activate webpage
python app.py
```

> [!NOTE]
> The app does not run the evluations, if they are not available yet. Therefore, run the python-code by hand! 

Open `http://localhost:8000/` to view the initial four-panel layout.
