from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
import pandas as pd

import plotly.graph_objects as go

SENSOR_LOCATIONS: dict[str, dict[str, float]] = {
    "Baum": {"lat": 48.1853771, "lon": 16.3530750},
    "Cafe": {"lat": 48.185508, "lon": 16.353281},
    "Telefonzelle": {"lat": 48.185685, "lon": 16.353648},
    "Bankomat": {"lat": 48.185590, "lon": 16.353828},
}


class Sensor:
    def __init__(self, name: str):
        self.name = name
        self.df = self._load_temperature_csv()
        self.df_max = self._evaluate_maximum_per_day()

    def _load_temperature_csv(self) -> pd.DataFrame:
        inputfile = pd.read_excel(
            "Temperaturzeitreihen/alle_Zeitreihen.xlsx",
            sheet_name=self.name,
            decimal=",",
        )
        inputfile.set_index("Zeit", inplace=True)
        inputfile.index = pd.to_datetime(inputfile.index, errors="coerce")
        inputfile = inputfile[inputfile.index.notna()].sort_index()

        return inputfile[[self.name]]

    def _evaluate_maximum_per_day(self) -> pd.DataFrame:
        """
        evaluates the maximum value per day from timeseries.
        Returns a timeseries with index days and one value per day
        in column 'maximum_temperature'
        """
        if self.df.empty:
            return pd.DataFrame(columns=["maximum_temperature"])

        daily_max = self.df[self.name].resample("D").max().dropna()
        return daily_max.to_frame(name="maximum_temperature")

    def plot_time_series(self):
        """
        Creates a plotly figure for the timeseries of the sensor.
        Plots one line per day from 00h to 24h
        x Axis of the plots shows the time in hours from 00 to 24.
        """
        figure = go.Figure()

        if self.df.empty:
            output_path = Path("docs/plots") / f"{self.name.lower()}_time_series.html"
            _write_plot(figure, output_path)
            return figure

        sensor_column = self.df.columns[0]
        daily_maximums = self.df[sensor_column].resample("D").max().dropna()

        max_day = daily_maximums.idxmax() if not daily_maximums.empty else None
        min_day = daily_maximums.idxmin() if not daily_maximums.empty else None

        for day, day_frame in self.df.groupby(self.df.index.normalize()):
            day_start = pd.Timestamp(day)
            hours = (day_frame.index - day_start).total_seconds() / 3600
            day_label = day_start.date().isoformat()

            line_color = "rgba(140, 140, 140, 0.6)"
            if max_day is not None and day == max_day.normalize():
                line_color = "red"
                day_label = f"{day_label} (max)"
            elif min_day is not None and day == min_day.normalize():
                line_color = "blue"
                day_label = f"{day_label} (min)"

            figure.add_trace(
                go.Scatter(
                    x=hours,
                    y=day_frame[sensor_column],
                    mode="lines",
                    name=day_label,
                    line=dict(color=line_color, width=2),
                )
            )

        figure.update_layout(
            title=f"{self.name} time series",
            xaxis_title="Time of day (hours)",
            yaxis_title="Temperature (°C)",
            xaxis=dict(range=[0, 24]),
            hovermode="x unified",
        )

        output_path = Path("docs/plots") / f"{self.name.lower()}_time_series.html"
        _write_plot(figure, output_path)
        return figure


def plot_sensor_time_series(
    csv_path: str | Path,
    sensor_name: str,
    output_html_path: str | Path | None = None,
) -> go.Figure:
    timestamps, temperatures = _load_temperature_csv(csv_path)
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=timestamps, y=temperatures, mode='lines', name=sensor_name))
    figure.update_layout(title=f'{sensor_name} time series', xaxis_title='Time', yaxis_title='Temperature (°C)')
    _write_plot(figure, output_html_path)
    return figure


def _write_plot(figure: go.Figure, output_html_path: str | Path | None) -> None:
    if output_html_path is None:
        return

    output_path = Path(output_html_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(output_path, include_plotlyjs="cdn", full_html=True)


def plot_sensor_max_temperature_map(
    sensor_files: dict[str, str | Path],
    day: str,
    output_html_path: str | Path | None = None,
    sensor_locations: dict[str, dict[str, float]] | None = None,
) -> go.Figure:
    locations = sensor_locations or SENSOR_LOCATIONS

    sensor_names: list[str] = []
    lats: list[float] = []
    lons: list[float] = []
    max_temperatures: list[float] = []

    for sensor_name, csv_path in sensor_files.items():
        timestamps, temperatures = _load_temperature_csv(csv_path)
        daily_values = [
            temperature
            for timestamp, temperature in zip(timestamps, temperatures)
            if timestamp.date().isoformat() == day
        ]
        if not daily_values or sensor_name not in locations:
            continue

        sensor_names.append(sensor_name)
        lats.append(locations[sensor_name]['lat'])
        lons.append(locations[sensor_name]['lon'])
        max_temperatures.append(max(daily_values))

    figure = go.Figure(
        go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers+text',
            text=sensor_names,
            textposition='top center',
            marker=dict(size=14, color=max_temperatures, colorscale='Viridis', showscale=True),
            name='Max sensor temperature',
        )
    )
    figure.update_layout(
        title=f'Maximum sensor temperatures on {day}',
        mapbox=dict(style='open-street-map', center=dict(lat=48.205, lon=16.38), zoom=11),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    _write_plot(figure, output_html_path)
    return figure


def plot_one_day_for_all_locations(all_locations: list[Sensor]) -> go.Figure:
    """
    all_locations: list[Sensor]: list of the objects of class Sensor.
        self.df is the timeseries to be used.
        self.name is the name to be used.

        Creates a figure over one day including the daily lines for all locations
    """
    figure = go.Figure()

    sensor_colors: dict[str, str] = {
        "Baum": "#636EFA",
        "Cafe": "#EF553B",
        "Telefonzelle": "#00CC96",
        "Bankomat": "#AB63FA",
    }
    line_styles = ["solid"]  # , "dash", "dot", "dashdot", "longdash", "longdashdot"]

    for sensor in all_locations:
        if sensor.df.empty:
            continue

        sensor_column = sensor.df.columns[0]
        color = sensor_colors.get(sensor.name, "#666666")
        sensor_traces_added = False

        for day_index, (day, day_frame) in enumerate(
            sensor.df.groupby(sensor.df.index.normalize())
        ):
            day_start = pd.Timestamp(day)
            hours = (day_frame.index - day_start).total_seconds() / 3600
            day_label = day_start.date().isoformat()
            line_dash = line_styles[day_index % len(line_styles)]
            opacity = 0.45 + (
                0.5 * (day_index % len(line_styles)) / max(1, len(line_styles) - 1)
            )
            rgba_color = (
                f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, "
                f"{int(color[5:7], 16)}, {opacity:.2f})"
            )

            figure.add_trace(
                go.Scatter(
                    x=hours,
                    y=day_frame[sensor_column],
                    mode="lines",
                    name=f"{sensor.name} {day_label}",
                    legendgroup=sensor.name,
                    showlegend=not sensor_traces_added,
                    line=dict(color=rgba_color, width=2, dash=line_dash),
                    hovertemplate=(
                        f"{sensor.name}<br>Day: {day_label}<br>"
                        "Hour: %{x:.2f}<br>Temperature: %{y:.2f} °C<extra></extra>"
                    ),
                )
            )
            sensor_traces_added = True

    figure.update_layout(
        title="Combined time series for all locations",
        xaxis_title="Time of day (hours)",
        yaxis_title="Temperature (°C)",
        xaxis=dict(range=[0, 24]),
        hovermode="x unified",
        legend=dict(groupclick="togglegroup"),
    )

    output_path = Path("docs/plots") / "combined.html"
    _write_plot(figure, output_path)
    return figure


def plot_weather_station_time_series(
    csv_path: str | Path, output_html_path: str | Path | None = None
) -> go.Figure:
    timestamps, temperatures = _load_temperature_csv(csv_path)
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(x=timestamps, y=temperatures, mode="lines", name="Weather station")
    )
    figure.update_layout(
        title="Weather station time series",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
    )
    _write_plot(figure, output_html_path)
    return figure


def main():
    all_sensors: list[Sensor] = [Sensor(name) for name in SENSOR_LOCATIONS.keys()]

    # create one plot per location
    # for sensor in all_sensors:
    #    sensor.plot_time_series()

    # create one plot with all locations
    plot_one_day_for_all_locations(all_sensors)


if __name__ == "__main__":
    main()
