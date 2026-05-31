from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from backend.temperature_backend import (
    evaluate_heat_stress,
    plot_sensor_max_temperature_map,
    plot_sensor_time_series,
    plot_sensors_for_days,
    plot_weather_station_time_series,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
DUMMY_INPUT = REPO_ROOT / 'data' / 'dummy_input'


class TemperatureBackendTests(unittest.TestCase):
    def test_weather_station_plot_and_evaluation(self) -> None:
        weather_csv = DUMMY_INPUT / 'weather_station.csv'
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'weather.html'
            figure = plot_weather_station_time_series(weather_csv, output_path)

            self.assertEqual(len(figure.data), 1)
            self.assertTrue(output_path.exists())

        stress = evaluate_heat_stress(weather_csv)
        self.assertEqual(len(stress), 10)
        self.assertIn('2026-01-01', stress)
        self.assertIn('2026-01-10', stress)

    def test_sensor_plot_functions(self) -> None:
        sensor_files = {
            'north': DUMMY_INPUT / 'sensor_north.csv',
            'south': DUMMY_INPUT / 'sensor_south.csv',
            'east': DUMMY_INPUT / 'sensor_east.csv',
            'west': DUMMY_INPUT / 'sensor_west.csv',
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            sensor_output = Path(tmp_dir) / 'north.html'
            single_fig = plot_sensor_time_series(sensor_files['north'], 'north', sensor_output)
            self.assertEqual(len(single_fig.data), 1)
            self.assertTrue(sensor_output.exists())

            multi_output = Path(tmp_dir) / 'selected_days.html'
            multi_fig = plot_sensors_for_days(sensor_files, ['2026-01-01', '2026-01-03'], multi_output)
            self.assertEqual(len(multi_fig.data), 4)
            self.assertTrue(multi_output.exists())

            map_output = Path(tmp_dir) / 'map.html'
            map_fig = plot_sensor_max_temperature_map(sensor_files, '2026-01-02', map_output)
            self.assertEqual(len(map_fig.data), 1)
            self.assertEqual(len(map_fig.data[0]['lat']), 4)
            self.assertTrue(map_output.exists())


if __name__ == '__main__':
    unittest.main()
