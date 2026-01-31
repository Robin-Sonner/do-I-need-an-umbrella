from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ForecastInterval(Enum):
    """Time intervals for weather forecasts."""

    HOURLY = "hourly"
    DAILY = "daily"


@dataclass
class Location:
    """
    Represents a geographic location.

    Attributes:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        name: Optional name of the location
        timezone: Optional timezone (auto-detected if not provided)
    """

    latitude: float
    longitude: float
    name: Optional[str] = None
    timezone: Optional[str] = None

    def __post_init__(self):
        """Validate coordinates."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(
                f"Invalid latitude: {self.latitude}. Expected value between -90 and 90 degrees"
            )
        if not -180 <= self.longitude <= 180:
            raise ValueError(
                f"Invalid longitude: {self.longitude}. Expected value between -180 and 180 degrees"
            )


@dataclass
class WeatherData:
    """
    Weather data for a specific time point.

    Attributes:
        timestamp: Time of the forecast
        temperature: Temperature in Celsius
        precipitation_probability: Probability of precipitation (0-100%)
        humidity: Relative humidity (0-100%)
        wind_speed: Wind speed in km/h
        weather_code: WMO weather code
    """

    timestamp: datetime
    temperature: Optional[float] = None
    precipitation_probability: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    weather_code: Optional[int] = None

    def needs_umbrella(self, threshold: float = 30.0) -> bool:
        """
        Determine if an umbrella is needed based on precipitation probability.

        Args:
            threshold: Precipitation probability threshold (default: 30%)

        Returns:
            True if an umbrella is recommended, False otherwise
        """
        if self.precipitation_probability is None:
            return False
        return self.precipitation_probability >= threshold


@dataclass
class WeatherForecast:
    """
    Complete weather forecast for a location.

    Attributes:
        location: Location for this forecast
        interval: Forecast interval (hourly or daily)
        data: List of weather data points
        generated_at: When this forecast was generated
    """

    location: Location
    interval: ForecastInterval
    data: list[WeatherData]
    generated_at: datetime

    def get_tomorrow(self) -> Optional[WeatherData]:
        """
        Get tomorrow's weather forecast.

        Returns:
            WeatherData for tomorrow, or None if not available
        """
        if not self.data:
            return None

        now = datetime.now()
        for weather in self.data:
            # Check if this is tomorrow (between 24 and 48 hours from now)
            hours_diff = (weather.timestamp - now).total_seconds() / 3600
            if 20 <= hours_diff <= 30:  # Around 24 hours
                return weather
        return None

    def get_next_days(self, days: int = 7) -> list[WeatherData]:
        """
        Get the weather forecast for the next N days.

        Args:
            days: Number of days to retrieve (default: 7)

        Returns:
            List of WeatherData objects
        """
        return self.data[:days]

    def get_hourly_forecast(self, hours: int = 24) -> list[WeatherData]:
        """
        Get an hourly weather forecast for the next N hours.

        Args:
            hours: Number of hours to retrieve (default: 24)

        Returns:
            List of WeatherData objects
        """
        return self.data[:hours]
