from datetime import datetime
from typing import Any
import requests

from models import Location, WeatherForecast, WeatherData, ForecastInterval
from exceptions import WeatherAPIError, LocationNotFoundError, NetworkError


class WeatherClient:
    """
    Client for retrieving weather forecasts from Open-Meteo API.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self, timeout: int = 10):
        """
        Initialize the Weather Client.

        Args:
            timeout: Request timeout in seconds (default: 10)
        """
        self.timeout = timeout
        self.session = requests.Session()

    def get_location(self, city_name: str) -> Location:
        """
        Convert a city name to geographic coordinates.

        Args:
            city_name: Name of the city to geocode

        Returns:
            Location object with coordinates

        Raises:
            LocationNotFoundError: If the location cannot be found.
            NetworkError: If the API request fails
        """
        try:
            params = {"name": city_name, "count": 1, "language": "en", "format": "json"}

            response = self.session.get(
                self.GEOCODING_URL, params=params, timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            if not data.get("results"):
                raise LocationNotFoundError(f"Location '{city_name}' not found")

            result = data["results"][0]
            return Location(
                latitude=result["latitude"],
                longitude=result["longitude"],
                name=result["name"],
                timezone=result.get("timezone"),
            )

        except requests.RequestException as e:
            raise NetworkError(f"Failed to geocode location: {e}")

    def get_forecast(
        self,
        location: Location,
        interval: ForecastInterval = ForecastInterval.DAILY,
        days: int = 7,
        include_temperature: bool = True,
        include_precipitation: bool = True,
        include_humidity: bool = True,
        include_wind: bool = True,
    ) -> WeatherForecast:
        """
        Retrieve the weather forecast for the provided location.

        Args:
            location: Location to get forecast for. Use geocode_location() to convert a city name to coordinates.
            interval: Forecast interval (hourly or daily)
            days: Number of days to forecast (default: 7, max: 16)
            include_temperature: Include temperature data
            include_precipitation: Include precipitation probability
            include_humidity: Include humidity data
            include_wind: Include wind speed data

        Returns:
            WeatherForecast object containing the forecast data

        Raises:
            WeatherAPIError: If the API request fails

        Note:
            16 days is the maximum that the underlying API (Open-Meteo) supports.
        """
        # Build parameters based on the interval
        params: dict[str, Any] = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "forecast_days": min(days, 16),
        }

        if location.timezone:
            params["timezone"] = location.timezone

        # Select variables based on the interval
        variables: list[str] = []

        if interval == ForecastInterval.DAILY:
            if include_temperature:
                variables.extend(["temperature_2m_max", "temperature_2m_min"])
            if include_precipitation:
                variables.append("precipitation_probability_max")
            if include_humidity:
                variables.append("relative_humidity_2m_mean")
            if include_wind:
                variables.append("wind_speed_10m_max")
            variables.append("weather_code")
            params["daily"] = ",".join(variables)

        else:  # HOURLY
            if include_temperature:
                variables.append("temperature_2m")
            if include_precipitation:
                variables.append("precipitation_probability")
            if include_humidity:
                variables.append("relative_humidity_2m")
            if include_wind:
                variables.append("wind_speed_10m")
            variables.append("weather_code")
            params["hourly"] = ",".join(variables)

        try:
            response = self.session.get(
                self.BASE_URL, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            weather_data = WeatherClient._parse_response(data, interval)

            return WeatherForecast(
                location=location,
                interval=interval,
                data=weather_data,
                generated_at=datetime.now(),
            )

        except requests.RequestException as e:
            raise WeatherAPIError(f"Failed to retrieve forecast: {e}")

    @staticmethod
    def _parse_response(
        data: dict[str, Any], interval: ForecastInterval
    ) -> list[WeatherData]:
        """
        Parse API response into WeatherData objects.

        Args:
            data: JSON response from the API
            interval: Forecast interval

        Returns:
            List of WeatherData objects
        """
        weather_list: list[WeatherData] = []

        if interval == ForecastInterval.DAILY:
            daily_data = data.get("daily", {})
            times = daily_data.get("time", [])

            for i, time_str in enumerate(times):
                timestamp = datetime.fromisoformat(time_str)

                # For daily data, use max temperature or average of min/max
                temp_max = daily_data.get("temperature_2m_max", [None] * len(times))[i]
                temp_min = daily_data.get("temperature_2m_min", [None] * len(times))[i]
                temperature = None
                if temp_max is not None and temp_min is not None:
                    temperature = (temp_max + temp_min) / 2
                elif temp_max is not None:
                    temperature = temp_max

                weather_list.append(
                    WeatherData(
                        timestamp=timestamp,
                        temperature=temperature,
                        precipitation_probability=daily_data.get(
                            "precipitation_probability_max", [None] * len(times)
                        )[i],
                        humidity=daily_data.get(
                            "relative_humidity_2m_mean", [None] * len(times)
                        )[i],
                        wind_speed=daily_data.get(
                            "wind_speed_10m_max", [None] * len(times)
                        )[i],
                        weather_code=daily_data.get(
                            "weather_code", [None] * len(times)
                        )[i],
                    )
                )

        else:  # HOURLY
            hourly_data = data.get("hourly", {})
            times = hourly_data.get("time", [])

            for i, time_str in enumerate(times):
                timestamp = datetime.fromisoformat(time_str)

                weather_list.append(
                    WeatherData(
                        timestamp=timestamp,
                        temperature=hourly_data.get(
                            "temperature_2m", [None] * len(times)
                        )[i],
                        precipitation_probability=hourly_data.get(
                            "precipitation_probability", [None] * len(times)
                        )[i],
                        humidity=hourly_data.get(
                            "relative_humidity_2m", [None] * len(times)
                        )[i],
                        wind_speed=hourly_data.get(
                            "wind_speed_10m", [None] * len(times)
                        )[i],
                        weather_code=hourly_data.get(
                            "weather_code", [None] * len(times)
                        )[i],
                    )
                )

        return weather_list

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
