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


def _write_plot(figure: go.Figure, output_html_path: str | Path | None) -> None:
    if output_html_path is None:
        return

    output_path = Path(output_html_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(output_path, include_plotlyjs="cdn", full_html=True)


def _load_temperature_csv(csv_path: str | Path) -> tuple[pd.Series, pd.Series]:
    inputfile = pd.read_csv(csv_path)
    inputfile["timestamp"] = pd.to_datetime(inputfile["timestamp"], errors="coerce")
    inputfile = inputfile[inputfile["timestamp"].notna()].sort_values("timestamp")
    return inputfile["timestamp"], inputfile["temperature"]


def plot_sensor_max_temperature_map(
    all_locations: list[Sensor],
    output_html_path: str | Path | None = Path("docs/plots/map.html"),
    sensor_locations: dict[str, dict[str, float]] = SENSOR_LOCATIONS,
) -> go.Figure:

    df = pd.DataFrame(sensor_locations).T

    sensor_colors = {
        "Baum": "#636EFA",
        "Cafe": "#EF553B",
        "Telefonzelle": "#00CC96",
        "Bankomat": "#AB63FA",
    }

    df["color"] = df.index.to_series().map(sensor_colors)

    fig = go.Figure(
        go.Scattermapbox(
            lon=df["lon"],
            lat=df["lat"],
            mode="markers+text",
            text=df.index,
            textposition="top right",
            textfont=dict(size=12, color="black"),
            marker=dict(size=16, color=df["color"]),
        )
    )

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            zoom=18,  # adjust depending on your area
            center=dict(
                lat=df["lat"].mean(),
                lon=df["lon"].mean(),
            ),
        ),
        title="Sensor locations",
        margin=dict(l=0, r=0, t=40, b=0),
    )

    _write_plot(fig, output_html_path)
    return fig


def plot_one_day_for_all_locations(
    all_locations: list[Sensor], days: list[pd.datetime] = [], day_name: str = None
) -> go.Figure:
    """
    all_locations: list[Sensor]: list of the objects of class Sensor.
        self.df is the timeseries to be used.
        self.name is the name to be used.
        days: _optional_ list of days to plot. If empty, all days in the timeseries will be plotted.
        day_name: _optional_ name to be included in the title of the plot and the outputfile.
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

    # prepare allowed days set if days parameter is provided
    allowed_days_set = None
    days_labels: list[str] = []
    if days:
        # normalize input days to pandas Timestamp (date precision)
        normalized = [pd.to_datetime(d).normalize() for d in days]
        allowed_days_set = set(normalized)
        days_labels = [d.date().isoformat() for d in normalized]

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
            # if days provided, only include those dates
            if (
                allowed_days_set is not None
                and day_start.normalize() not in allowed_days_set
            ):
                continue

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
        title="Zeitreihen an " + day_name if day_name else "Zeitreihe aller Messpunkte",
        xaxis_title="Tageszeit",
        yaxis_title="Temperatur (°C)",
        xaxis=dict(range=[0, 24]),
        hovermode="x unified",
        legend=dict(groupclick="togglegroup"),
    )

    # build output filename: include evaluated days if provided
    if days_labels:
        # sort and deduplicate labels for filename
        unique_sorted = sorted(dict.fromkeys(days_labels))
        days_part = "_".join(unique_sorted)
        output_filename = f"combined_{day_name.replace(' ', '_')}.html"
    else:
        output_filename = "combined.html"

    output_path = Path("docs/plots") / output_filename
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

    # create the sensor-location map
    plot_sensor_max_temperature_map(all_sensors)

    # create one plot per location
    for sensor in all_sensors:
        sensor.plot_time_series()

    # create one plot with all locations
    plot_one_day_for_all_locations(all_sensors)

    # Tagesplots
    days_to_plot = {
        "Tagen unter 25 Grad": [
            "2026-05-19",
            "2026-05-20",
            "2026-05-21",
            "2026-05-22",
            "2026-06-01",
        ],
        "Sommertagen (TX > 25 Grad)": [
            "2026-05-23",
            "2026-05-28",
            "2026-05-29",
            "2026-05-30",
            "2026-05-31",
            "2026-06-02",
        ],
        "Hitzetag (TX > 30 Grad)": [
            "2026-05-24",
            "2026-05-25",
            "2026-05-26",
            "2026-05-27",
        ],
    }
    for day_name, days in days_to_plot.items():
        plot_one_day_for_all_locations(all_sensors, days=days, day_name=day_name)


if __name__ == "__main__":
    main()
