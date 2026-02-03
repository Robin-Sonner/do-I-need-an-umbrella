import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import numpy as np

from dinau import CurrentWeather, CurrentWeatherLite, Location, WeatherClient


class MockResponse:
    """Mock API response object"""

    def __init__(self, current_data=None, hourly_data=None, daily_data=None):
        self._current_data = current_data
        self._hourly_data = hourly_data
        self._daily_data = daily_data
        self._utc_offset = 0

    def Current(self):
        return self._current_data

    def Hourly(self):
        return self._hourly_data

    def Daily(self):
        return self._daily_data

    def UtcOffsetSeconds(self):
        return self._utc_offset


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


class MockDataObject:
    """Mock data object (Current/Hourly/Daily)"""

    def __init__(self, variables, time_data=None):
        self._variables = variables
        self._time_data = time_data or {}

    def Variables(self, index):
        return MockVariable(self._variables[index])

    def Time(self):
        return self._time_data.get("time", int(datetime.now().timestamp()))

    def TimeEnd(self):
        return self._time_data.get(
            "time_end", int((datetime.now() + timedelta(days=1)).timestamp())
        )

    def Interval(self):
        return self._time_data.get("interval", 3600)


class TestWeatherClientIntegration(unittest.TestCase):
    """Integration tests for WeatherClient"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("dinau.location.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": [{"latitude": 49.45, "longitude": 11.08}]
            }
            mock_get.return_value = mock_response
            self.location = Location("Nuremberg")

    def test_get_current_weather_lite(self):
        """Test getting current weather in lite mode"""
        mock_meteo = Mock()

        current_data = MockDataObject(
            [
                15.5,  # temperature
                14.2,  # apparent_temperature
                65.0,  # humidity
                12.5,  # wind_speed
                3,  # weather_code
                0.5,  # precipitation
            ]
        )

        mock_response = MockResponse(current_data=current_data)
        mock_meteo.weather_api.return_value = [mock_response]

        client = WeatherClient(
            self.location, rounding_precision=2, meteo=lambda session: mock_meteo
        )
        weather = client.get_weather_current(lite=True)

        self.assertIsInstance(weather, CurrentWeatherLite)
        self.assertEqual(weather.temperature, 15.5)
        self.assertEqual(weather.weather_code, 3)

    def test_get_current_weather_full(self):
        """Test getting current weather in full mode"""
        mock_meteo = Mock()

        current_data = MockDataObject(
            [
                15.5,  # temperature
                14.2,  # apparent_temperature
                65.0,  # humidity
                12.5,  # wind_speed
                180.0,  # wind_direction
                18.5,  # wind_gust
                3,  # weather_code
                0.5,  # precipitation
                0.0,  # snowfall
                0.5,  # rain
                0.0,  # showers
                75.0,  # cloud_cover
                1013.0,  # pressure_sea_level
                1010.0,  # pressure_surface_level
            ]
        )

        mock_response = MockResponse(current_data=current_data)
        mock_meteo.weather_api.return_value = [mock_response]

        client = WeatherClient(
            self.location, rounding_precision=2, meteo=lambda session: mock_meteo
        )
        weather = client.get_weather_current(lite=False)

        self.assertIsInstance(weather, CurrentWeather)
        self.assertEqual(weather.temperature, 15.5)
        self.assertEqual(weather.wind_gust, 18.5)
        self.assertEqual(weather.cloud_cover, 75.0)


class TestWeatherClientRounding(unittest.TestCase):
    """Test rounding functionality"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("dinau.location.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": [{"latitude": 49.45, "longitude": 11.08}]
            }
            mock_get.return_value = mock_response
            self.location = Location("Nuremberg")

    def test_rounding_applied_current_weather(self):
        """Test that rounding is applied correctly to current weather"""
        mock_meteo = Mock()

        # Create mock data with values that need rounding
        current_data = MockDataObject(
            [
                12.3456,  # temperature
                11.7891,  # apparent_temperature
                67.8912,  # humidity
                15.4567,  # wind_speed
                3,  # weather_code
                2.3456,  # precipitation
            ]
        )

        mock_response = MockResponse(current_data=current_data)
        mock_meteo.weather_api.return_value = [mock_response]

        client = WeatherClient(
            self.location, rounding_precision=2, meteo=lambda session: mock_meteo
        )
        weather = client.get_weather_current(lite=True)

        self.assertEqual(weather.temperature, 12.35)
        self.assertEqual(weather.apparent_temperature, 11.79)
        self.assertEqual(weather.humidity, 67.89)
        self.assertEqual(weather.wind_speed, 15.46)
        self.assertEqual(weather.precipitation, 2.35)

    def test_no_rounding_when_none(self):
        """Test that rounding is not applied when precision is None"""
        mock_meteo = Mock()

        current_data = MockDataObject(
            [
                12.3456,  # temperature
                11.7891,  # apparent_temperature
                67.8912,  # humidity
                15.4567,  # wind_speed
                3,  # weather_code
                2.3456,  # precipitation
            ]
        )

        mock_response = MockResponse(current_data=current_data)
        mock_meteo.weather_api.return_value = [mock_response]

        client = WeatherClient(
            self.location, rounding_precision=None, meteo=lambda session: mock_meteo
        )
        weather = client.get_weather_current(lite=True)

        self.assertEqual(weather.temperature, 12.3456)
        self.assertEqual(weather.apparent_temperature, 11.7891)
        self.assertEqual(weather.humidity, 67.8912)

    def test_rounding_with_different_precision(self):
        """Test rounding with different precision values"""
        mock_meteo = Mock()

        current_data = MockDataObject(
            [
                12.3456,  # temperature
                11.7891,  # apparent_temperature
                67.8912,  # humidity
                15.4567,  # wind_speed
                3,  # weather_code
                2.3456,  # precipitation
            ]
        )

        mock_response = MockResponse(current_data=current_data)
        mock_meteo.weather_api.return_value = [mock_response]

        # Test with precision = 1
        client = WeatherClient(
            self.location, rounding_precision=1, meteo=lambda session: mock_meteo
        )
        weather = client.get_weather_current(lite=True)

        self.assertEqual(weather.temperature, 12.3)
        self.assertEqual(weather.apparent_temperature, 11.8)
        self.assertEqual(weather.humidity, 67.9)

    def test_rounding_numpy_arrays(self):
        """Test that rounding is applied to numpy arrays in hourly data"""
        mock_meteo = Mock()

        # Create hourly data with 24 hours
        now = datetime.now()
        time_start = int(now.timestamp())
        time_end = int((now + timedelta(days=1)).timestamp())

        # Create exactly 24 values
        hourly_data = MockDataObject(
            variables=[
                np.array([12.346] * 24),  # temperature (24 values)
                np.array([11.234] * 24),  # apparent_temperature
                np.array([65.123] * 24),  # humidity
                np.array([10.123] * 24),  # wind_speed
                np.array([3] * 24),  # weather_code
                np.array([1.230] * 24),  # precipitation
            ],
            time_data={"time": time_start, "time_end": time_end, "interval": 3600},
        )

        daily_data = MockDataObject([10.0, 20.0, 50.0])

        mock_response = MockResponse(hourly_data=hourly_data, daily_data=daily_data)
        mock_meteo.weather_api.return_value = [mock_response]

        client = WeatherClient(
            self.location, rounding_precision=2, meteo=lambda session: mock_meteo
        )
        weather = client.get_weather_today(lite=True)

        # Check that values in dataframe are rounded
        self.assertAlmostEqual(
            weather.hourly_data["temperature"].iloc[0], 12.35, places=2
        )
        self.assertAlmostEqual(
            weather.hourly_data["apparent_temperature"].iloc[0], 11.23, places=2
        )
        self.assertAlmostEqual(
            weather.hourly_data["precipitation"].iloc[0], 1.23, places=2
        )


if __name__ == "__main__":
    unittest.main()
