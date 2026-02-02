import unittest
from unittest.mock import Mock, patch

from dinau import Location


class TestLocation(unittest.TestCase):
    """Test Location class"""

    @patch("location.requests.get")
    def test_location_fetch_coordinates(self, mock_get):
        """Test that coordinates are fetched correctly"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"latitude": 49.4521, "longitude": 11.0767}]
        }
        mock_get.return_value = mock_response

        location = Location("Nuremberg")

        self.assertEqual(location.latitude, 49.4521)
        self.assertEqual(location.longitude, 11.0767)
        self.assertEqual(location.name, "Nuremberg")

    @patch("location.requests.get")
    def test_location_not_found(self, mock_get):
        """Test handling of location not found"""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            Location("NonexistentPlace123456")

        self.assertIn("not found", str(context.exception))

    @patch("location.requests.get")
    def test_location_connection_error(self, mock_get):
        """Test handling of connection errors"""
        import requests

        mock_get.side_effect = requests.RequestException("Network error")

        with self.assertRaises(ConnectionError):
            Location("Nuremberg")


if __name__ == "__main__":
    unittest.main()
