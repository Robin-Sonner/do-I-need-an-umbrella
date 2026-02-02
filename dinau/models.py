from dataclasses import dataclass
from enum import Enum, auto
import pandas as pd


class AirQualityIndex(Enum):
    """European Air Quality Index categories."""

    GOOD = auto()
    FAIR = auto()
    MODERATE = auto()
    POOR = auto()
    VERY_POOR = auto()
    EXTREMELY_POOR = auto()


@dataclass
class CurrentWeather:
    """
    Current weather conditions. Comprehensive information

    Attributes:
        timestamp: Time of the request (Unix Timestamp)
        temperature: Current temperature in Celsius
        apparent_temperature: Current Feels-like temperature in Celsius
        humidity: Current Relative humidity (0-100%)
        wind_speed: Current wind speed in km/h
        wind_direction: Current Wind direction in degrees
        wind_gust: Current Wind gust speed in km/h
        weather_code: Current WMO weather code
        precipitation: Preceding 15 minutes sum in mm
        snowfall: Preceding 15 minutes sum in cm
        rain: Preceding 15 minutes sum in mm
        showers: Preceding 15 minutes sum in mm
        cloud_cover: Current Cloud cover percentage (0-100%)
        pressure_sea_level: Current Atmospheric pressure at sea level in hPa
        pressure_surface_level Current Atmospheric pressure at surface level in hPa
    """

    timestamp: float
    temperature: float
    apparent_temperature: float
    humidity: float
    wind_speed: float
    wind_direction: float
    wind_gust: float
    weather_code: int
    precipitation: float
    snowfall: float
    rain: float
    showers: float
    cloud_cover: float
    pressure_sea_level: float
    pressure_surface_level: float


@dataclass
class CurrentWeatherLite:
    """
    Current weather conditions. Only the most important information.
    Attributes:
        timestamp: Time of the request (Unix Timestamp)
        temperature: Current temperature in Celsius
        apparent_temperature: Current Feels-like temperature in Celsius
        humidity: Current Relative humidity (0-100%)
        wind_speed: Current wind speed in km/h
        weather_code: Current WMO weather code
        precipitation: Preceding 15 minutes sum in mm
    """

    timestamp: float
    temperature: float
    apparent_temperature: float
    humidity: float
    wind_speed: float
    weather_code: int
    precipitation: float


@dataclass
class DailyWeatherLite:
    """
    Weather forecast for a single day. Only the most important information.

    Attributes:
        timestamp: Time of the request (Unix Timestamp)
        temperature_min: Minimum temperature in Celsius
        temperature_max: Maximum temperature in Celsius
        precipitation_probability: Probability of precipitation (0-100%)
        hourly_data: Hourly weather data for the day

    Notes:
        hourly_data contains the columns:
        - date: datetime of this row
        - temperature: Temperature (Celsius)
        - apparent_temperature: Feels-like temperature
        - humidity: Relative humidity at this time (0-100%)
        - wind_speed: Wind speed
        - weather_code: WMO weather code
        - precipitation: Precipitation amount (mm)
        Except for date (datetime) and weather_code (int), all columns contain float values.
        There are 24 rows in hourly_data.
    """

    timestamp: float
    temperature_min: float
    temperature_max: float
    precipitation_probability: float
    hourly_data: pd.DataFrame

    def umbrella_needed(self, threshold: float = 3.0) -> bool:
        """
        Determines if an umbrella is needed based on the weather data.

        Internally, Umbrella points are calculated based on the following factors:
            - Precipitation probability (0-100%)
            - Precipitation amount, temperature, and time of precipitation

        Args:
            threshold: Minimum number of 'umbrella points' needed to return true

        Returns:
            bool: True if an umbrella is needed, else False
        """
        df = self.hourly_data.copy()

        # Probability factor (0–2)
        probability_factor = (self.precipitation_probability / 100.0) * 2.0

        # Temperature factor. Snow is ignored. Rain at cold temperature is weighted higher
        temp_factor = pd.Series(1.0, index=df.index)
        temp_factor[df["temperature"] < 0] = 0.0
        temp_factor[df["temperature"].between(0, 20, inclusive="left")] = 1.5

        # Time of day factor. Morning/Evening hours are weighted higher, rain at night is weighted less
        hours = df["date"].dt.hour
        time_factor = pd.Series(1.0, index=df.index)
        # Morning (6–9) and evening (16–19)
        time_factor[hours.between(6, 9)] = 1.5
        time_factor[hours.between(16, 19)] = 1.5
        # Night (22–5)
        night_mask = (hours >= 22) | (hours <= 5)
        time_factor[night_mask] = 0.75

        # Umbrella points
        umbrella_points = (
            df["precipitation"] * probability_factor * temp_factor * time_factor
        ).sum()

        return umbrella_points >= threshold


@dataclass
class DailyWeather(DailyWeatherLite):
    """
    Weather forecast for a single day. Comprehensive information.

    Attributes:
        timestamp: Time of the request (Unix Timestamp)
        temperature_min: Minimum temperature in Celsius
        temperature_max: Maximum temperature in Celsius
        precipitation_probability: Probability of precipitation (0-100%)
        hourly_data: Hourly weather data for the day

    Notes:
        hourly_data contains the columns:
        - date: datetime of this row
        - temperature: Temperature
        - apparent_temperature: Feels-like temperature
        - humidity: Relative humidity (0-100%)
        - wind_speed: Wind speed
        - wind_direction: Wind direction in degrees
        - wind_gusts: Wind gust speed
        - weather_code: WMO weather code
        - precipitation: Precipitation amount
        - snowfall: Snowfall amount
        - rain: Rain amount
        - showers: Shower amount
        - cloud_cover: Cloud cover percentage (0-100%)
        - pressure_sea_level: Atmospheric pressure at sea level in hPa
        - pressure_surface_level: Atmospheric pressure at surface level in hPa
        Except for date (datetime) and weather_code (int), all columns contain float values.
        There are 24 rows in hourly_data.
    """

    pass


@dataclass
class WeatherForecastDailyLite:
    """
    Weather forecast for multiple days. Only the most important information.

    Attributes:
        timestamp: Time of the request (Unix Timestamp)
        daily_data: Daily weather data.
        hourly_data: Hourly weather data.

    Notes:
        daily_data contains the columns:
        - date: datetime of this row
        - temperature_min: Minimum temperature
        - temperature_max: Maximum temperature
        - precipitation_probability: Probability of precipitation (0-100%)
        hourly_data contains the columns:
        - date: datetime of this row
        - temperature: Temperature (Celsius)
        - apparent_temperature: feels-like temperature (Celsius)
        - humidity: Relative humidity (0-100%)
        - wind_speed: Wind speed (km/h)
        - weather_code: WMO weather code
        - precipitation: Precipitation amount (mm)
        Except for date (datetime) and weather_code (int), all columns contain float values.

    """

    timestamp: float
    daily_data: pd.DataFrame
    hourly_data: pd.DataFrame

    def umbrella_needed(self, threshold: float = 3.0) -> list[bool]:
        """
        Determines if an umbrella is needed for each day based on the weather data.

        Internally, Umbrella points are calculated based on the following factors:
            - Precipitation probability (0-100%)
            - Precipitation amount, temperature, and time of precipitation

        Args:
            threshold: Minimum number of 'umbrella points' needed to return true

        Returns:
            list[bool]: List of boolean values, one per day. True if an umbrella
                        is needed for that day, else False
        """
        results = []

        # Iterate over each day
        dates = self.daily_data["date"].dt.date.unique()
        for date in dates:
            daily_row = self.daily_data[self.daily_data["date"].dt.date == date].iloc[0]
            hourly_df = self.hourly_data[
                self.hourly_data["date"].dt.date == date
            ].copy()

            # Probability factor (0–2)
            probability_factor = (daily_row["precipitation_probability"] / 100.0) * 2.0
            # Temperature factor. Snow is ignored. Rain at cold temperature is weighted higher
            temp_factor = pd.Series(1.0, index=hourly_df.index)
            temp_factor[hourly_df["temperature"] < 0] = 0.0
            temp_factor[hourly_df["temperature"].between(0, 20, inclusive="left")] = 1.5
            # Time of day factor. Morning/Evening hours are weighted higher, rain at night is weighted less
            hours = hourly_df["date"].dt.hour
            time_factor = pd.Series(1.0, index=hourly_df.index)
            # Morning (6–9) and evening (16–19)
            time_factor[hours.between(6, 9)] = 1.5
            time_factor[hours.between(16, 19)] = 1.5
            # Night (22–5)
            night_mask = (hours >= 22) | (hours <= 5)
            time_factor[night_mask] = 0.75
            # Umbrella points
            umbrella_points = (
                hourly_df["precipitation"]
                * probability_factor
                * temp_factor
                * time_factor
            ).sum()

            results.append(umbrella_points >= threshold)

        return results


@dataclass
class WeatherForecastDaily(WeatherForecastDailyLite):
    """
    Weather forecast for multiple days. Comprehensive information.

    Attributes:
        timestamp: Time of the request (Unix Timestamp)
        daily_data: Daily weather data.
        hourly_data: Hourly weather data.

    Notes:
        daily_data contains the columns:
        - date: datetime of this row
        - temperature_min: Minimum temperature
        - temperature_max: Maximum temperature
        - precipitation_probability: Probability of precipitation (0-100%)
        hourly_data contains the columns:
        - date: datetime of this row
        - temperature: Temperature
        - apparent_temperature: Feels-like temperature
        - humidity: Relative humidity (0-100%)
        - wind_speed: Wind speed
        - wind_direction: Wind direction in degrees
        - wind_gusts: Wind gust speed
        - weather_code: WMO weather code
        - precipitation: Precipitation amount
        - snowfall: Snowfall amount
        - rain: Rain amount
        - showers: Shower amount
        - cloud_cover: Cloud cover percentage (0-100%)
        - pressure_sea_level: Atmospheric pressure at sea level in hPa
        - pressure_surface_level: Atmospheric pressure at surface level in hPa
        Except for date (datetime) and weather_code (int), all columns contain float values.
    """

    pass
