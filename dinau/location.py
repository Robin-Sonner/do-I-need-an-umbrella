import requests


class Location:
    """
    Represents a geographic location.
    """

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self, name: str):
        self.name = name
        self._fetch_coordinates()

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    def _fetch_coordinates(self) -> None:
        """Fetches latitude and longitude from Open-Meteo Geocoding API"""
        try:
            params = {
                "name": self.name,
                "count": 1,  # Get top result
                "language": "en",
                "format": "json",
            }

            response = requests.get(self.GEOCODING_URL, params=params)
            response.raise_for_status()

            data = response.json()

            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                self._latitude = result["latitude"]
                self._longitude = result["longitude"]
            else:
                raise ValueError(f"Location '{self.name}' not found")

        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch coordinates: {e}")
