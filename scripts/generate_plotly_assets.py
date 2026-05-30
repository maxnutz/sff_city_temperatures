from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import plotly.graph_objects as go

DOCS_DIR = Path(__file__).resolve().parent.parent / 'docs'
PLOTS_DIR = DOCS_DIR / 'plots'


def write_plot(path: Path, figure: go.Figure) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(path, include_plotlyjs='cdn', full_html=True)


def main() -> None:
    start = datetime(2026, 1, 1)
    times = [start + timedelta(hours=i * 6) for i in range(20)]

    series_values = {
        'north': [3, 4, 5, 6, 7, 8, 8, 7, 6, 6, 7, 9, 10, 11, 10, 9, 8, 7, 6, 5],
        'south': [5, 6, 7, 8, 9, 10, 10, 9, 8, 8, 9, 11, 12, 13, 12, 11, 10, 9, 8, 7],
        'east': [2, 3, 4, 5, 6, 7, 7, 6, 5, 5, 6, 8, 9, 10, 9, 8, 7, 6, 5, 4],
        'west': [4, 5, 6, 7, 8, 9, 9, 8, 7, 7, 8, 10, 11, 12, 11, 10, 9, 8, 7, 6],
    }

    for site, values in series_values.items():
        figure = go.Figure()
        figure.add_trace(go.Scatter(x=times, y=values, mode='lines+markers', name=site.title()))
        figure.update_layout(title=f'{site.title()} temperature series', margin=dict(l=20, r=20, t=50, b=20))
        write_plot(PLOTS_DIR / f'{site}.html', figure)

    combined = go.Figure()
    for site, values in series_values.items():
        combined.add_trace(go.Scatter(x=times, y=values, mode='lines', name=site.title()))
    combined.update_layout(title='Combined temperature series', margin=dict(l=20, r=20, t=50, b=20))
    write_plot(PLOTS_DIR / 'combined.html', combined)

    city_map = go.Figure(
        go.Scattergeo(
            lon=[16.357, 16.373, 16.386, 16.401],
            lat=[48.184, 48.200, 48.207, 48.214],
            text=['North sensor', 'South sensor', 'East sensor', 'West sensor'],
            mode='markers+text',
            marker=dict(size=[12, 12, 12, 12], color=[6, 8, 5, 7], colorscale='Viridis', showscale=True),
            textposition='top center',
            name='Sensors',
        )
    )
    city_map.update_layout(
        title='Sensor map (Vienna area)',
        geo=dict(scope='europe', center=dict(lat=48.208, lon=16.373), projection_scale=45),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    write_plot(PLOTS_DIR / 'map.html', city_map)


if __name__ == '__main__':
    main()
