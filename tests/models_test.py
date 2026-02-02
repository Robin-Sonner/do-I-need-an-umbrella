import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from dinau import (
    CurrentWeather,
    CurrentWeatherLite,
    DailyWeatherLite,
    Location,
    WeatherClient,
    WeatherForecastDailyLite,
)


class MockVariable:
    """Mock variable from API response"""

    def __init__(self, value):
        self._value = value

    def Value(self):
        return self._value

    def ValuesAsNumpy(self):
        if isinstance(self._value, (list, np.ndarray)):
            return np.array(self._value)
        return np.array([self._value])


class TestUmbrellaNeeded(unittest.TestCase):
    """Test the umbrella_needed functionality"""

    def create_hourly_dataframe(self, temperatures, precipitations, hours=None):
        """Helper method to create hourly data"""
        if hours is None:
            hours = list(range(24))

        dates = [
            datetime.now().replace(hour=h, minute=0, second=0, microsecond=0)
            for h in hours
        ]

        return pd.DataFrame(
            {
                "date": pd.to_datetime(dates),
                "temperature": temperatures,
                "apparent_temperature": [t - 2 for t in temperatures],
                "humidity": [70] * len(temperatures),
                "wind_speed": [10] * len(temperatures),
                "weather_code": [3] * len(temperatures),
                "precipitation": precipitations,
            }
        )

    def test_umbrella_needed_no_rain(self):
        """Test that umbrella is not needed when there's no rain"""
        hourly_df = self.create_hourly_dataframe(
            temperatures=[15] * 24, precipitations=[0] * 24
        )

        daily_weather = DailyWeatherLite(
            timestamp=datetime.now().timestamp(),
            temperature_min=10.0,
            temperature_max=20.0,
            precipitation_probability=0.0,
            hourly_data=hourly_df,
        )

        self.assertFalse(daily_weather.umbrella_needed())

    def test_umbrella_needed_heavy_rain(self):
        """Test that umbrella is needed with heavy rain"""
        hourly_df = self.create_hourly_dataframe(
            temperatures=[15] * 24, precipitations=[5.0] * 24  # Heavy rain all day
        )

        daily_weather = DailyWeatherLite(
            timestamp=datetime.now().timestamp(),
            temperature_min=10.0,
            temperature_max=20.0,
            precipitation_probability=90.0,
            hourly_data=hourly_df,
        )

        self.assertTrue(daily_weather.umbrella_needed())

    def test_umbrella_needed_morning_rain(self):
        """Test umbrella needed calculation with morning rain (higher weight)"""
        precipitations = [0] * 24
        precipitations[7] = 3.0  # Rain at 7 AM (morning, high weight)

        hourly_df = self.create_hourly_dataframe(
            temperatures=[15] * 24, precipitations=precipitations
        )

        daily_weather = DailyWeatherLite(
            timestamp=datetime.now().timestamp(),
            temperature_min=10.0,
            temperature_max=20.0,
            precipitation_probability=70.0,
            hourly_data=hourly_df,
        )

        # Should need umbrella due to morning rain with high probability
        self.assertTrue(daily_weather.umbrella_needed())

    def test_umbrella_needed_night_rain(self):
        """Test that night rain has lower weight"""
        precipitations = [0] * 24
        precipitations[23] = 2.0  # Rain at 11 PM (night, lower weight)

        hourly_df = self.create_hourly_dataframe(
            temperatures=[15] * 24, precipitations=precipitations
        )

        daily_weather = DailyWeatherLite(
            timestamp=datetime.now().timestamp(),
            temperature_min=10.0,
            temperature_max=20.0,
            precipitation_probability=40.0,  # Lower probability
            hourly_data=hourly_df,
        )

        # Should not need umbrella due to night rain with lower weight
        # Night factor: 0.75, probability factor: 0.4 * 2 = 0.8, temp factor: 1.0
        # Points: 2.0 * 0.8 * 1.0 * 0.75 = 1.2 < 3.0
        self.assertFalse(daily_weather.umbrella_needed())

    def test_umbrella_needed_cold_rain(self):
        """Test that cold rain has a higher weight"""
        # Moderate cold rain at noon
        precipitations = [0] * 24
        precipitations[12] = 2.0
        temperatures = [5] * 24

        hourly_df = self.create_hourly_dataframe(
            temperatures=temperatures, precipitations=precipitations
        )
        daily_weather = DailyWeatherLite(
            timestamp=datetime.now().timestamp(),
            temperature_min=5.0,
            temperature_max=5.0,
            precipitation_probability=80.0,
            hourly_data=hourly_df,
        )
        self.assertTrue(daily_weather.umbrella_needed())

    def test_umbrella_forecast_multiple_days(self):
        """Test umbrella_needed for multiple days in forecast"""
        # Create 3 days of data
        dates = []
        temperatures = []
        precipitations = []

        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Day 1: No rain
        for h in range(24):
            dates.append(base_date + timedelta(hours=h))
            temperatures.append(15)
            precipitations.append(0)

        # Day 2: Heavy rain
        for h in range(24):
            dates.append(base_date + timedelta(days=1, hours=h))
            temperatures.append(15)
            precipitations.append(5.0)

        # Day 3: Very light rain at night only
        for h in range(24):
            dates.append(base_date + timedelta(days=2, hours=h))
            temperatures.append(15)
            # Only rain at night (low weight) and very light
            if h == 23:
                precipitations.append(0.3)
            else:
                precipitations.append(0)

        hourly_df = pd.DataFrame(
            {
                "date": pd.to_datetime(dates),
                "temperature": temperatures,
                "apparent_temperature": [t - 2 for t in temperatures],
                "humidity": [70] * len(temperatures),
                "wind_speed": [10] * len(temperatures),
                "weather_code": [3] * len(temperatures),
                "precipitation": precipitations,
            }
        )

        daily_df = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    [
                        base_date,
                        base_date + timedelta(days=1),
                        base_date + timedelta(days=2),
                    ]
                ),
                "temperature_min": [10.0, 10.0, 10.0],
                "temperature_max": [20.0, 20.0, 20.0],
                "precipitation_probability": [
                    0.0,
                    90.0,
                    20.0,
                ],  # Low probability for day 3
            }
        )

        forecast = WeatherForecastDailyLite(
            timestamp=datetime.now().timestamp(),
            daily_data=daily_df,
            hourly_data=hourly_df,
        )

        results = forecast.umbrella_needed()

        self.assertEqual(len(results), 3)
        self.assertFalse(results[0])  # Day 1: no rain
        self.assertTrue(results[1])  # Day 2: heavy rain
        self.assertFalse(results[2])  # Day 3: very light rain at night, low probability


if __name__ == "__main__":
    unittest.main()
