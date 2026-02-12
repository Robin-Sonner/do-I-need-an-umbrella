WEATHER_DESCRIPTION = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_emoji(weather_code: int) -> str:
    """
    Get an emoji representation of the weather code.

    Args:
        weather_code: WMO weather code

    Returns:
        Weather emoji
    """
    if weather_code == 0:
        return "☀️"
    elif weather_code in [1, 2]:
        return "⛅"
    elif weather_code == 3:
        return "☁️"
    elif weather_code in [45, 48]:
        return "🌫️"
    elif weather_code in range(51, 58):
        return "🌧️"
    elif weather_code in range(61, 68):
        return "🌧️"
    elif weather_code in range(71, 78):
        return "❄️"
    elif weather_code in range(80, 87):
        return "🌦️"
    elif weather_code in range(95, 100):
        return "⛈️"
    else:
        return ""
