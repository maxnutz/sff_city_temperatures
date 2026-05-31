from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.temperature_backend import (  # noqa: E402
    plot_sensor_max_temperature_map,
    plot_sensor_time_series,
    plot_sensors_for_days,
    plot_weather_station_time_series,
)

DOCS_DIR = REPO_ROOT / 'docs'
PLOTS_DIR = DOCS_DIR / 'plots'
DUMMY_INPUT_DIR = REPO_ROOT / 'data' / 'dummy_input'


def main() -> None:
    sensor_files = {
        'north': DUMMY_INPUT_DIR / 'sensor_north.csv',
        'south': DUMMY_INPUT_DIR / 'sensor_south.csv',
        'east': DUMMY_INPUT_DIR / 'sensor_east.csv',
        'west': DUMMY_INPUT_DIR / 'sensor_west.csv',
    }

    for sensor_name, sensor_file in sensor_files.items():
        plot_sensor_time_series(sensor_file, sensor_name.title(), PLOTS_DIR / f'{sensor_name}.html')

    plot_sensors_for_days(sensor_files, ['2026-01-01', '2026-01-02'], PLOTS_DIR / 'combined.html')
    plot_sensor_max_temperature_map(sensor_files, '2026-01-02', PLOTS_DIR / 'map.html')

    weather_file = DUMMY_INPUT_DIR / 'weather_station.csv'
    plot_weather_station_time_series(weather_file, PLOTS_DIR / 'weather_station.html')


if __name__ == '__main__':
    main()
