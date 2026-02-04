"""Widget for displaying current weather information."""

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from dinau import CurrentWeather

from .utilities import WEATHER_DESCRIPTION, get_weather_emoji


class CurrentWeatherWidget(QWidget):
    """Widget to display current weather conditions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Content widget
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(20)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        # Initially show loading state
        self._show_loading()

    def _show_loading(self):
        """Display loading state."""
        self._clear_layout()
        loading_label = QLabel("Loading weather data...")
        loading_label.setProperty("class", "loading")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(loading_label)
        self.content_layout.addStretch()

    def _clear_layout(self):
        """Clear all widgets from the content layout."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def update_weather(self, weather: CurrentWeather):
        """
        Update the display with new weather data.

        Args:
            weather: Current weather data
        """
        self._clear_layout()
        # Main weather card
        main_card = CurrentWeatherWidget._create_main_card(weather)
        self.content_layout.addWidget(main_card)
        # Details grid
        details_card = self._create_details_card(weather)
        self.content_layout.addWidget(details_card)
        # Add stretch to push content to the top
        self.content_layout.addStretch()

    @staticmethod
    def _create_main_card(weather: CurrentWeather) -> QFrame:
        """Create the main weather display card."""
        card = QFrame()
        card.setProperty("class", "weather-card")
        card.setMinimumHeight(200)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Weather emoji and description
        weather_layout = QHBoxLayout()
        weather_layout.setContentsMargins(0, 10, 0, 10)
        emoji_label = QLabel(get_weather_emoji(weather.weather_code))
        emoji_label.setStyleSheet("font-size: 48px;")
        weather_layout.addWidget(emoji_label)
        desc_label = QLabel(
            WEATHER_DESCRIPTION.get(
                weather.weather_code, "Sorry, no description available"
            )
        )
        desc_label.setProperty("class", "weather-description")
        desc_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        weather_layout.addWidget(desc_label)
        weather_layout.addStretch()
        layout.addLayout(weather_layout)

        # Temperature
        temp_label = QLabel(f"{weather.temperature:.1f}°C")
        temp_label.setProperty("class", "temperature-main")
        temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(temp_label)

        # Feels like temperature
        feels_like_label = QLabel(f"Feels like {weather.apparent_temperature:.1f}°C")
        feels_like_label.setProperty("class", "subtitle")
        feels_like_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(feels_like_label)

        # Last updated
        time_label = QLabel(
            f"Updated at {datetime.fromtimestamp(weather.timestamp).strftime("%H:%M")}"
        )
        time_label.setStyleSheet("color: #a0aec0; font-size: 12px; margin-top: 10px;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(time_label)

        return card

    @staticmethod
    def _create_details_card(weather: CurrentWeather) -> QFrame:
        """Create the weather details card."""
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Details")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)

        # Grid for weather details
        grid = QGridLayout()
        grid.setSpacing(20)
        details = [
            ("Humidity", f"{weather.humidity:.0f}%", 0, 0),
            ("Wind Speed", f"{weather.wind_speed:.1f} km/h", 0, 1),
            ("Precipitation", f"{weather.precipitation:.1f} mm", 1, 0),
            ("Wind Direction", f"{weather.wind_direction:.0f}°", 1, 1),
            ("Wind Gust", f"{weather.wind_gust:.1f} km/h", 2, 0),
            ("Cloud Cover", f"{weather.cloud_cover:.0f}%", 2, 1),
            ("Pressure (Sea)", f"{weather.pressure_sea_level:.0f} hPa", 3, 0),
            ("Pressure (Surface)", f"{weather.pressure_surface_level:.0f} hPa", 3, 1),
        ]
        # Show additional precipitation types if relevant
        if weather.rain > 0:
            details.append(("Rain", f"{weather.rain:.1f} mm", 4, 0))
        if weather.snowfall > 0:
            details.append(("Snowfall", f"{weather.snowfall:.1f} cm", 4, 1))
        if weather.showers > 0:
            details.append(("Showers", f"{weather.showers:.1f} mm", 5, 0))
        # Create info cards for each detail
        for label_text, value_text, row, col in details:
            info_card = CurrentWeatherWidget._create_info_card(label_text, value_text)
            grid.addWidget(info_card, row, col)
        layout.addLayout(grid)

        return card

    @staticmethod
    def _create_info_card(label: str, value: str) -> QFrame:
        """Create a small info card for a weather detail."""
        card = QFrame()
        card.setProperty("class", "info-card")
        card.setMinimumHeight(70)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(5)

        label_widget = QLabel(label)
        label_widget.setProperty("class", "info-label")
        layout.addWidget(label_widget)
        value_widget = QLabel(value)
        value_widget.setProperty("class", "info-value")
        layout.addWidget(value_widget)

        return card

    def show_error(self, error_message: str):
        """
        Show an error message.

        Args:
            error_message: Error message to display
        """
        self._clear_layout()
        error_label = QLabel(f"Error: {error_message}")
        error_label.setProperty("class", "error")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setWordWrap(True)
        self.content_layout.addWidget(error_label)
        self.content_layout.addStretch()
