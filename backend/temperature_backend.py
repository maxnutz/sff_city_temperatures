from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

import plotly.graph_objects as go

SENSOR_LOCATIONS: dict[str, dict[str, float]] = {
    'north': {'lat': 48.214, 'lon': 16.357},
    'south': {'lat': 48.184, 'lon': 16.373},
    'east': {'lat': 48.207, 'lon': 16.386},
    'west': {'lat': 48.200, 'lon': 16.401},
}


def _load_temperature_csv(csv_path: str | Path) -> tuple[list[datetime], list[float]]:
    timestamps: list[datetime] = []
    temperatures: list[float] = []

    with Path(csv_path).open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or 'timestamp' not in reader.fieldnames or 'temperature' not in reader.fieldnames:
            raise ValueError('CSV must contain timestamp and temperature columns.')

        for row in reader:
            timestamps.append(datetime.fromisoformat(row['timestamp']))
            temperatures.append(float(row['temperature']))

    return timestamps, temperatures


def _write_plot(figure: go.Figure, output_html_path: str | Path | None) -> None:
    if output_html_path is None:
        return

    output_path = Path(output_html_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(output_path, include_plotlyjs='cdn', full_html=True)


def plot_weather_station_time_series(csv_path: str | Path, output_html_path: str | Path | None = None) -> go.Figure:
    timestamps, temperatures = _load_temperature_csv(csv_path)
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=timestamps, y=temperatures, mode='lines', name='Weather station'))
    figure.update_layout(title='Weather station time series', xaxis_title='Time', yaxis_title='Temperature (°C)')
    _write_plot(figure, output_html_path)
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


def plot_sensors_for_days(
    sensor_files: dict[str, str | Path],
    included_days: Iterable[str],
    output_html_path: str | Path | None = None,
) -> go.Figure:
    included_day_set = set(included_days)
    figure = go.Figure()

    for sensor_name, csv_path in sensor_files.items():
        timestamps, temperatures = _load_temperature_csv(csv_path)
        filtered_pairs = [
            (timestamp, temperature)
            for timestamp, temperature in zip(timestamps, temperatures)
            if timestamp.date().isoformat() in included_day_set
        ]

        filtered_timestamps = [timestamp for timestamp, _ in filtered_pairs]
        filtered_temperatures = [temperature for _, temperature in filtered_pairs]

        figure.add_trace(go.Scatter(x=filtered_timestamps, y=filtered_temperatures, mode='lines', name=sensor_name))

    figure.update_layout(title='Temperature sensors for selected days', xaxis_title='Time', yaxis_title='Temperature (°C)')
    _write_plot(figure, output_html_path)
    return figure


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


def evaluate_heat_stress(csv_path: str | Path) -> dict[str, float]:
    timestamps, temperatures = _load_temperature_csv(csv_path)
    daily_maximums: defaultdict[str, float] = defaultdict(lambda: float('-inf'))

    for timestamp, temperature in zip(timestamps, temperatures):
        day = timestamp.date().isoformat()
        if temperature > daily_maximums[day]:
            daily_maximums[day] = temperature

    return dict(daily_maximums)
