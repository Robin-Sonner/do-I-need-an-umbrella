from dataclasses import dataclass
from enum import Enum, auto

import pandas as pd


class AirQualityIndex(Enum):
    """European Air Quality Index categories.

    This enum defines the standard European air quality categories ranging from good to extremely poor conditions.
    """

    GOOD = auto()
    FAIR = auto()
    MODERATE = auto()
    POOR = auto()
    VERY_POOR = auto()
    EXTREMELY_POOR = auto()


@dataclass
class CurrentWeather:
    """Current weather conditions with comprehensive information.

    :param timestamp: Time of the request (Unix Timestamp)
    :type timestamp: float
    :param temperature: Current temperature in Celsius
    :type temperature: float
    :param apparent_temperature: Current feels-like temperature in Celsius
    :type apparent_temperature: float
    :param humidity: Current relative humidity (0-100%)
    :type humidity: float
    :param wind_speed: Current wind speed in km/h
    :type wind_speed: float
    :param wind_direction: Current wind direction in degrees
    :type wind_direction: float
    :param wind_gust: Current wind gust speed in km/h
    :type wind_gust: float
    :param weather_code: Current WMO weather code
    :type weather_code: int
    :param precipitation: Preceding 15 minutes sum in mm
    :type precipitation: float
    :param snowfall: Preceding 15 minutes sum in cm
    :type snowfall: float
    :param rain: Preceding 15 minutes sum in mm
    :type rain: float
    :param showers: Preceding 15 minutes sum in mm
    :type showers: float
    :param cloud_cover: Current cloud cover percentage (0-100%)
    :type cloud_cover: float
    :param pressure_sea_level: Current atmospheric pressure at sea level in hPa
    :type pressure_sea_level: float
    :param pressure_surface_level: Current atmospheric pressure at surface level in hPa
    :type pressure_surface_level: float
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
    """Current weather conditions with only the most important information.

    :param timestamp: Time of the request (Unix Timestamp)
    :type timestamp: float
    :param temperature: Current temperature in Celsius
    :type temperature: float
    :param apparent_temperature: Current feels-like temperature in Celsius
    :type apparent_temperature: float
    :param humidity: Current relative humidity (0-100%)
    :type humidity: float
    :param wind_speed: Current wind speed in km/h
    :type wind_speed: float
    :param weather_code: Current WMO weather code
    :type weather_code: int
    :param precipitation: Preceding 15 minutes sum in mm
    :type precipitation: float
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
    """Weather forecast for a single day with only the most important information.

    :param timestamp: Time of the request (Unix Timestamp)
    :type timestamp: float
    :param temperature_min: Minimum temperature in Celsius
    :type temperature_min: float
    :param temperature_max: Maximum temperature in Celsius
    :type temperature_max: float
    :param precipitation_probability: Probability of precipitation (0-100%)
    :type precipitation_probability: float
    :param hourly_data: Hourly weather data for the day
    :type hourly_data: pd.DataFrame

    .. note::
       The ``hourly_data`` DataFrame contains the following columns:

       - **date** (*datetime*): Datetime of this row
       - **temperature** (*float*): Temperature (Celsius)
       - **apparent_temperature** (*float*): Feels-like temperature
       - **humidity** (*float*): Relative humidity at this time (0-100%)
       - **wind_speed** (*float*): Wind speed
       - **weather_code** (*int*): WMO weather code
       - **precipitation** (*float*): Precipitation amount (mm)

       The DataFrame contains 24 rows (one per hour).
    """

    timestamp: float
    temperature_min: float
    temperature_max: float
    precipitation_probability: float
    hourly_data: pd.DataFrame

    def umbrella_needed(self, threshold: float = 3.0) -> bool:
        """Determines if an umbrella is needed based on the weather data.

        Umbrella points are calculated internally based on the following factors:

        - Precipitation probability (0-100%)
        - Precipitation amount, temperature, and time of precipitation

        :param threshold: Minimum number of 'umbrella points' needed to return True (default: 3.0)
        :type threshold: float
        :return: True if an umbrella is needed, False otherwise
        :rtype: bool
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
    """Weather forecast for a single day with comprehensive information.

    :param timestamp: Time of the request (Unix Timestamp)
    :type timestamp: float
    :param temperature_min: Minimum temperature in Celsius
    :type temperature_min: float
    :param temperature_max: Maximum temperature in Celsius
    :type temperature_max: float
    :param precipitation_probability: Probability of precipitation (0-100%)
    :type precipitation_probability: float
    :param hourly_data: Hourly weather data for the day
    :type hourly_data: pd.DataFrame

    .. note::
       The ``hourly_data`` DataFrame contains the following columns:

       - **date** (*datetime*): Datetime of this row
       - **temperature** (*float*): Temperature
       - **apparent_temperature** (*float*): Feels-like temperature
       - **humidity** (*float*): Relative humidity (0-100%)
       - **wind_speed** (*float*): Wind speed
       - **wind_direction** (*float*): Wind direction in degrees
       - **wind_gusts** (*float*): Wind gust speed
       - **weather_code** (*int*): WMO weather code
       - **precipitation** (*float*): Precipitation amount
       - **snowfall** (*float*): Snowfall amount
       - **rain** (*float*): Rain amount
       - **showers** (*float*): Shower amount
       - **cloud_cover** (*float*): Cloud cover percentage (0-100%)
       - **pressure_sea_level** (*float*): Atmospheric pressure at sea level in hPa
       - **pressure_surface_level** (*float*): Atmospheric pressure at surface level in hPa

       The DataFrame contains 24 rows (one per hour).
    """

    pass


@dataclass
class WeatherForecastLite:
    """Weather forecast for multiple days with only the most important information.

    :param timestamp: Time of the request (Unix Timestamp)
    :type timestamp: float
    :param daily_data: Daily weather data
    :type daily_data: pd.DataFrame
    :param hourly_data: Hourly weather data
    :type hourly_data: pd.DataFrame

    .. note::
       The ``daily_data`` DataFrame contains the following columns:

       - **date** (*datetime*): Datetime of this row
       - **temperature_min** (*float*): Minimum temperature
       - **temperature_max** (*float*): Maximum temperature
       - **temperature_mean** (*float*): Mean temperature
       - **apparent_temperature_mean** (*float*): Mean feels-like temperature
       - **precipitation_probability** (*float*): Probability of precipitation (0-100%)
       - **precipitation_sum** (*float*): Sum of precipitation for the day

       The ``hourly_data`` DataFrame contains the following columns:

       - **date** (*datetime*): Datetime of this row
       - **temperature** (*float*): Temperature (Celsius)
       - **apparent_temperature** (*float*): Feels-like temperature (Celsius)
       - **humidity** (*float*): Relative humidity (0-100%)
       - **wind_speed** (*float*): Wind speed (km/h)
       - **weather_code** (*int*): WMO weather code
       - **precipitation** (*float*): Precipitation amount (mm)
    """

    timestamp: float
    daily_data: pd.DataFrame
    hourly_data: pd.DataFrame

    def umbrella_needed(self, threshold: float = 3.0) -> list[bool]:
        """Determines if an umbrella is needed for each day based on the weather data.

        Umbrella points are calculated internally based on the following factors:

        - Precipitation probability (0-100%)
        - Precipitation amount, temperature, and time of precipitation

        :param threshold: Minimum number of 'umbrella points' needed to return True (default: 3.0)
        :type threshold: float
        :return: List of boolean values, one per day. True if an umbrella is needed for that day, False otherwise
        :rtype: list[bool]
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

    def get_detailed_data(self, section_length: int = 6) -> pd.DataFrame:
        """Calculate weather data with customized section length.

        :param section_length: Number of hours per section (default: 6 for 4 sections per day)
        :type section_length: int
        :return: DataFrame with detailed data containing the following columns:

                 - **date** (*str*): String representation of the section (e.g., "Jan 01 00-06")
                 - **temperature_min** (*float*): Minimum temperature in the section
                 - **temperature_max** (*float*): Maximum temperature in the section
                 - **temperature_mean** (*float*): Mean temperature in the section
                 - **apparent_temperature_mean** (*float*): Mean feels-like temperature in the section
                 - **precipitation_sum** (*float*): Sum of precipitation for the section
        :rtype: pd.DataFrame
        """
        detailed_rows = []
        # Group hourly data by date
        dates = self.hourly_data["date"].dt.date.unique()
        for date in dates:
            # Filter hourly data for this date
            day_hourly = self.hourly_data[
                self.hourly_data["date"].dt.date == date
            ].copy()
            # Divide the day into sections
            num_sections = 24 // section_length
            for section in range(num_sections):
                start_hour = section * section_length
                end_hour = start_hour + section_length
                # Filter data for this section
                section_data = day_hourly[
                    (day_hourly["date"].dt.hour >= start_hour)
                    & (day_hourly["date"].dt.hour < end_hour)
                ]
                if len(section_data) == 0:
                    continue
                # Calculate aggregated values for this section
                detailed_row = {
                    "date": f"{date.strftime('%b %d')} {start_hour:02d}-{end_hour:02d}",
                    "temperature_min": section_data["temperature"].min(),
                    "temperature_max": section_data["temperature"].max(),
                    "temperature_mean": section_data["temperature"].mean(),
                    "apparent_temperature_mean": section_data[
                        "apparent_temperature"
                    ].mean(),
                    "precipitation_sum": section_data["precipitation"].sum(),
                }
                detailed_rows.append(detailed_row)
        return pd.DataFrame(detailed_rows)


@dataclass
class WeatherForecast(WeatherForecastLite):
    """Weather forecast for multiple days with comprehensive information.

    :param timestamp: Time of the request (Unix Timestamp)
    :type timestamp: float
    :param daily_data: Daily weather data
    :type daily_data: pd.DataFrame
    :param hourly_data: Hourly weather data
    :type hourly_data: pd.DataFrame

    .. note::
       The ``daily_data`` DataFrame contains the following columns:

       - **date** (*datetime*): Datetime of this row
       - **temperature_min** (*float*): Minimum temperature
       - **temperature_max** (*float*): Maximum temperature
       - **temperature_mean** (*float*): Mean temperature
       - **apparent_temperature_mean** (*float*): Mean feels-like temperature
       - **precipitation_probability** (*float*): Probability of precipitation (0-100%)
       - **precipitation_sum** (*float*): Sum of precipitation for the day

       The ``hourly_data`` DataFrame contains the following columns:

       - **date** (*datetime*): Datetime of this row
       - **temperature** (*float*): Temperature
       - **apparent_temperature** (*float*): Feels-like temperature
       - **humidity** (*float*): Relative humidity (0-100%)
       - **wind_speed** (*float*): Wind speed
       - **wind_direction** (*float*): Wind direction in degrees
       - **wind_gusts** (*float*): Wind gust speed
       - **weather_code** (*int*): WMO weather code
       - **precipitation** (*float*): Precipitation amount
       - **snowfall** (*float*): Snowfall amount
       - **rain** (*float*): Rain amount
       - **showers** (*float*): Shower amount
       - **cloud_cover** (*float*): Cloud cover percentage (0-100%)
       - **pressure_sea_level** (*float*): Atmospheric pressure at sea level in hPa
       - **pressure_surface_level** (*float*): Atmospheric pressure at surface level in hPa
    """

    pass
