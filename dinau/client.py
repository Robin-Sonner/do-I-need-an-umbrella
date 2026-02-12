import time
from datetime import datetime, timedelta
from typing import Any, Optional

import numpy as np
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

from .location import Location
from .models import (
    CurrentWeather,
    CurrentWeatherLite,
    DailyWeather,
    DailyWeatherLite,
    WeatherForecast,
    WeatherForecastLite,
)


class WeatherClient:
    """Client for retrieving weather forecasts from Open-Meteo API.

    This client provides methods to fetch current weather conditions,
    today's weather forecast, and multi-day weather forecasts with
    configurable detail levels.
    """

    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"
    AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

    LITE_WEATHER: list[str] = [
        "temperature_2m",
        "apparent_temperature",
        "relative_humidity_2m",
        "wind_speed_10m",
        "weather_code",
        "precipitation",
    ]

    FULL_WEATHER: list[str] = [
        "temperature_2m",
        "apparent_temperature",
        "relative_humidity_2m",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "weather_code",
        "precipitation",
        "snowfall",
        "rain",
        "showers",
        "cloud_cover",
        "pressure_msl",
        "surface_pressure",
    ]

    def __init__(
        self,
        location: Location,
        rounding_precision: Optional[int] = 2,
        meteo=openmeteo_requests.Client,
    ):
        """Initialize the Weather Client.

        :param location: Location to get weather forecasts for
        :type location: Location
        :param rounding_precision: Rounding precision for all numeric values. If None, no rounding is performed (default: 2)
        :type rounding_precision: Optional[int]
        :param meteo: API to use for retrieving weather forecasts. Can be replaced with a mock for testing purposes (default: openmeteo_requests.Client)
        :type meteo: class
        """
        self.location = location
        self._rounding_precision = rounding_precision

        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.meteo = meteo(session=retry_session)  # type: ignore

    def get_weather_current(
        self, lite: bool = False
    ) -> CurrentWeather | CurrentWeatherLite:
        """Retrieve the current weather conditions.

        :param lite: If True, returns only the most important weather information; otherwise returns a detailed report (default: False)
        :type lite: bool
        :return: Dataclass holding information about the current weather
        :rtype: ~dinau.models.CurrentWeather | ~dinau.models.CurrentWeatherLite
        """
        now = time.time()
        params = {
            "latitude": self.location.latitude,
            "longitude": self.location.longitude,
            "current": self.LITE_WEATHER if lite else self.FULL_WEATHER,
            "timezone": "auto",
        }
        responses = self.meteo.weather_api(self.FORECAST_URL, params=params)
        response = responses[0]
        current = response.Current()

        if lite:
            weather = CurrentWeatherLite(
                timestamp=now,
                temperature=self._get_value(0, current),
                apparent_temperature=self._get_value(1, current),
                humidity=self._get_value(2, current),
                wind_speed=self._get_value(3, current),
                weather_code=int(current.Variables(4).Value()),
                precipitation=self._get_value(5, current),
            )
        else:
            weather = CurrentWeather(
                timestamp=now,
                temperature=self._get_value(0, current),
                apparent_temperature=self._get_value(1, current),
                humidity=self._get_value(2, current),
                wind_speed=self._get_value(3, current),
                wind_direction=self._get_value(3, current),
                wind_gust=self._get_value(5, current),
                weather_code=int(current.Variables(6).Value()),
                precipitation=self._get_value(7, current),
                snowfall=self._get_value(8, current),
                rain=self._get_value(9, current),
                showers=self._get_value(10, current),
                cloud_cover=self._get_value(11, current),
                pressure_sea_level=self._get_value(12, current),
                pressure_surface_level=self._get_value(13, current),
            )
        return weather

    def get_weather_today(self, lite: bool = False):
        """Retrieve today's weather forecast.

        :param lite: If True, returns only the most important weather information; otherwise returns a detailed report (default: False)
        :type lite: bool
        :return: Dataclass holding information about today's weather
        :rtype: ~dinau.models.DailyWeather | ~dinau.models.DailyWeatherLite
        """
        now = time.time()
        date = datetime.now().date().strftime("%Y-%m-%d")

        params = {
            "latitude": self.location.latitude,
            "longitude": self.location.longitude,
            "daily": [
                "temperature_2m_min",
                "temperature_2m_max",
                "precipitation_probability_max",
            ],
            "hourly": self.LITE_WEATHER if lite else self.FULL_WEATHER,
            "current": ["weather_code"],
            "timezone": "auto",
            "start_date": date,
            "end_date": date,
        }

        responses = self.meteo.weather_api(self.FORECAST_URL, params=params)
        response = responses[0]
        hourly = response.Hourly()
        daily = response.Daily()

        if lite:
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(
                        hourly.Time() + response.UtcOffsetSeconds(), unit="s", utc=True
                    ),
                    end=pd.to_datetime(
                        hourly.TimeEnd() + response.UtcOffsetSeconds(),
                        unit="s",
                        utc=True,
                    ),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left",
                ),
                "temperature": self._get_values(0, hourly),
                "apparent_temperature": self._get_values(1, hourly),
                "humidity": self._get_values(2, hourly),
                "wind_speed": self._get_values(3, hourly),
                "weather_code": self._get_values(4, hourly),
                "precipitation": self._get_values(5, hourly),
            }

        else:
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(
                        hourly.Time() + response.UtcOffsetSeconds(), unit="s", utc=True
                    ),
                    end=pd.to_datetime(
                        hourly.TimeEnd() + response.UtcOffsetSeconds(),
                        unit="s",
                        utc=True,
                    ),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left",
                ),
                "temperature": self._get_values(0, hourly),
                "apparent_temperature": self._get_values(1, hourly),
                "humidity": self._get_values(2, hourly),
                "wind_speed": self._get_values(3, hourly),
                "wind_direction": self._get_values(4, hourly),
                "wind_gusts": self._get_values(5, hourly),
                "weather_code": self._get_values(6, hourly),
                "precipitation": self._get_values(7, hourly),
                "snowfall": self._get_values(8, hourly),
                "rain": self._get_values(9, hourly),
                "showers": self._get_values(10, hourly),
                "cloud_cover": self._get_values(11, hourly),
                "pressure_sea_level": self._get_values(12, hourly),
                "pressure_surface_level": self._get_values(13, hourly),
            }

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        if lite:
            weather = DailyWeatherLite(
                timestamp=now,
                temperature_min=self._get_values(0, daily)[0],
                temperature_max=self._get_values(1, daily)[0],
                precipitation_probability=self._get_values(2, daily)[0],
                hourly_data=hourly_dataframe,
            )
        else:
            weather = DailyWeather(
                timestamp=now,
                temperature_min=self._get_values(0, daily)[0],
                temperature_max=self._get_values(1, daily)[0],
                precipitation_probability=self._get_values(2, daily)[0],
                hourly_data=hourly_dataframe,
            )
        return weather

    def get_weather_forecast(self, days: int = 7, lite: bool = False):
        """Retrieve weather forecast for multiple days.

        :param days: Number of days to forecast (default: 7)
        :type days: int
        :param lite: If True, returns only the most important weather information; otherwise returns a detailed report (default: False)
        :type lite: bool
        :return: Dataclass holding weather forecast data
        :rtype: ~dinau.models.WeatherForecast | ~dinau.models.WeatherForecastLite
        """
        now = time.time()
        start = datetime.now().date().strftime("%Y-%m-%d")
        end = (datetime.now().date() + timedelta(days=days)).strftime("%Y-%m-%d")
        params = {
            "latitude": self.location.latitude,
            "longitude": self.location.longitude,
            "daily": [
                "temperature_2m_min",
                "temperature_2m_max",
                "temperature_2m_mean",
                "apparent_temperature_mean",
                "precipitation_probability_max",
                "precipitation_sum",
            ],
            "hourly": self.LITE_WEATHER if lite else self.FULL_WEATHER,
            "current": ["weather_code"],
            "timezone": "auto",
            "start_date": start,
            "end_date": end,
        }

        responses = self.meteo.weather_api(self.FORECAST_URL, params=params)
        response = responses[0]
        daily = response.Daily()
        hourly = response.Hourly()

        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(
                    daily.Time() + response.UtcOffsetSeconds(), unit="s", utc=True
                ),
                end=pd.to_datetime(
                    daily.TimeEnd() + response.UtcOffsetSeconds(), unit="s", utc=True
                ),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left",
            ),
            "temperature_min": self._get_values(0, daily),
            "temperature_max": self._get_values(1, daily),
            "temperature_mean": self._get_values(2, daily),
            "apparent_temperature_mean": self._get_values(3, daily),
            "precipitation_probability": self._get_values(4, daily),
            "precipitation_sum": self._get_values(5, daily),
        }

        if lite:
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(
                        hourly.Time() + response.UtcOffsetSeconds(), unit="s", utc=True
                    ),
                    end=pd.to_datetime(
                        hourly.TimeEnd() + response.UtcOffsetSeconds(),
                        unit="s",
                        utc=True,
                    ),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left",
                ),
                "temperature": self._get_values(0, hourly),
                "apparent_temperature": self._get_values(1, hourly),
                "humidity": self._get_values(2, hourly),
                "wind_speed": self._get_values(3, hourly),
                "weather_code": self._get_values(4, hourly),
                "precipitation": self._get_values(5, hourly),
            }

            return WeatherForecastLite(
                timestamp=now,
                daily_data=pd.DataFrame(daily_data),
                hourly_data=pd.DataFrame(hourly_data),
            )

        else:
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(
                        hourly.Time() + response.UtcOffsetSeconds(), unit="s", utc=True
                    ),
                    end=pd.to_datetime(
                        hourly.TimeEnd() + response.UtcOffsetSeconds(),
                        unit="s",
                        utc=True,
                    ),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left",
                ),
                "temperature": self._get_values(0, hourly),
                "apparent_temperature": self._get_values(1, hourly),
                "humidity": self._get_values(2, hourly),
                "wind_speed": self._get_values(3, hourly),
                "wind_direction": self._get_values(4, hourly),
                "wind_gusts": self._get_values(5, hourly),
                "weather_code": self._get_values(6, hourly),
                "precipitation": self._get_values(7, hourly),
                "snowfall": self._get_values(8, hourly),
                "rain": self._get_values(9, hourly),
                "showers": self._get_values(10, hourly),
                "cloud_cover": self._get_values(11, hourly),
                "pressure_sea_level": self._get_values(12, hourly),
                "pressure_surface_level": self._get_values(13, hourly),
            }

            return WeatherForecast(
                timestamp=now,
                daily_data=pd.DataFrame(daily_data),
                hourly_data=pd.DataFrame(hourly_data),
            )

    def _get_value(self, key: int, data: Any) -> float:
        """Get a single value with optional rounding applied.

        :param key: Variable index
        :type key: int
        :param data: Data object containing the variables
        :type data: Any
        :return: Value, optionally rounded to the configured precision
        :rtype: float
        """
        value = data.Variables(key).Value()
        if self._rounding_precision is not None:
            return round(data.Variables(key).Value(), self._rounding_precision)
        return value

    def _get_values(self, key: int, data: Any):
        """Get numpy array values with optional rounding applied.

        :param key: Variable index
        :type key: int
        :param data: Data object containing the variables
        :type data: Any
        :return: Numpy array with values, optionally rounded to the configured precision
        :rtype: numpy.ndarray
        """
        values = data.Variables(key).ValuesAsNumpy()
        if self._rounding_precision is not None:
            return np.round(values, self._rounding_precision)
        return values
