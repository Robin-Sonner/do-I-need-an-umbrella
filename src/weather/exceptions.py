class WeatherAPIError(Exception):
    """Base exception for Weather API errors."""

    pass


class LocationNotFoundError(WeatherAPIError):
    """Raised when a location cannot be found or geocoded."""

    pass


class InvalidParameterError(WeatherAPIError):
    """Raised when invalid parameters are provided."""

    pass


class NetworkError(WeatherAPIError):
    """Raised when network communication fails."""

    pass
