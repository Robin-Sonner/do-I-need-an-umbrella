"""Widget for displaying today's weather conditions."""

import pandas as pd
from dinau import DailyWeather
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .utilities import get_weather_emoji
from .weather_chart import WeatherChart


class TodayWeatherWidget(QWidget):
    """Widget to display today's weather conditions."""

    def __init__(self, parent=None, use_pyqtgraph=True):
        """
        Initialize the widget.

        Args:
            parent: Parent widget (optional)
            use_pyqtgraph: If True, use pyqtgraph for charting; otherwise matplotlib
        """
        super().__init__(parent)
        self.weather_chart = WeatherChart(use_pyqtgraph=use_pyqtgraph)
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

    def update_weather(self, weather: DailyWeather):
        """
        Update the display with new weather data.

        Args:
            weather: Today's weather data
        """
        self._clear_layout()
        # Main overview card
        overview_card = TodayWeatherWidget._create_overview_card(weather)
        self.content_layout.addWidget(overview_card)
        # Umbrella recommendation
        if weather.umbrella_needed():
            umbrella_card = TodayWeatherWidget._create_umbrella_card()
            self.content_layout.addWidget(umbrella_card)
        # Charts card
        charts_card = self._create_charts_card(weather.hourly_data)
        self.content_layout.addWidget(charts_card)
        # Hourly forecast
        hourly_card = self._create_hourly_card(weather)
        self.content_layout.addWidget(hourly_card)
        # Add stretch to push content to the top
        self.content_layout.addStretch()

    @staticmethod
    def _create_overview_card(weather: DailyWeather) -> QFrame:
        """
        Create the overview card with a daily summary.

        Args:
            weather: Today's weather data

        Returns:
            QFrame representing the summary
        """
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        # Title
        title = QLabel("Today's Weather")
        title.setProperty("class", "title")
        layout.addWidget(title)
        # Temperature range
        temp_layout = QHBoxLayout()
        temp_range = QLabel(
            f"{weather.temperature_min:.1f}°C - {weather.temperature_max:.1f}°C"
        )
        temp_range.setProperty("class", "temperature-range")
        temp_layout.addWidget(temp_range)
        temp_layout.addStretch()
        layout.addLayout(temp_layout)
        # Precipitation probability
        precip_label = QLabel(
            f"Precipitation probability: {weather.precipitation_probability:.0f}%"
        )
        precip_label.setProperty("class", "subtitle")
        layout.addWidget(precip_label)
        return card

    @staticmethod
    def _create_umbrella_card() -> QFrame:
        """
        Create a card recommending to bring an umbrella.

        Returns:
            QFrame representing the umbrella recommendation
        """
        card = QFrame()
        card.setStyleSheet(
            "background-color: #ebf8ff; border: 2px solid #4299e1; border-radius: 8px;"
        )
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        emoji = QLabel("☔")
        emoji.setStyleSheet("font-size: 32px;")
        layout.addWidget(emoji)
        text = QLabel("Don't forget your umbrella today!")
        text.setStyleSheet("color: #2c5282; font-size: 16px; font-weight: 500;")
        layout.addWidget(text)
        layout.addStretch()
        return card

    def _create_charts_card(self, hourly_data: pd.DataFrame) -> QFrame:
        """
        Create the charts card using the WeatherCharts factory.

        Args:
            hourly_data: DataFrame with hourly weather data

        Returns:
            QFrame containing the weather charts
        """
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        # Title
        title = QLabel("Weather Charts")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        # Temperature and Precipitation Chart
        temp_precip_chart = self.weather_chart.create_temperature_precipitation_chart(
            hourly_data
        )
        temp_precip_chart.setMinimumHeight(300)
        layout.addWidget(temp_precip_chart)
        # Wind Speed Chart
        wind_chart = self.weather_chart.create_wind_speed_chart(hourly_data)
        wind_chart.setMinimumHeight(250)
        layout.addWidget(wind_chart)
        return card

    @staticmethod
    def _create_hourly_card(weather: DailyWeather) -> QFrame:
        """
        Create the hourly forecast card.

        Args:
            weather: Weather data for today

        Returns:
            QFrame containing a representation of the hourly forecast
        """
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        # Title
        title = QLabel("Hourly Forecast")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        # Horizontal scroll for hourly data
        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(180)
        # Container for hourly items
        hourly_container = QWidget()
        hourly_layout = QHBoxLayout(hourly_container)
        hourly_layout.setSpacing(15)
        hourly_layout.setContentsMargins(0, 0, 0, 0)
        # Create hourly items (show only every 2 hours to avoid clutter)
        df = weather.hourly_data
        for i in range(0, len(df), 2):
            row = df.iloc[i]
            hourly_item = TodayWeatherWidget._create_hourly_item(row)
            hourly_layout.addWidget(hourly_item)
        hourly_layout.addStretch()
        scroll.setWidget(hourly_container)
        layout.addWidget(scroll)
        return card

    @staticmethod
    def _create_hourly_item(row: pd.Series) -> QFrame:
        """
        Helper function to create a single hourly forecast item.

        Args:
            row: Series containing the weather data for a single hour

        Returns:
            Q-Frame containing a representation of the forecast for this hour
        """
        item = QFrame()
        item.setProperty("class", "info-card")
        item.setMinimumWidth(100)
        item.setMaximumWidth(120)

        # Data
        time_label = QLabel(row["date"].strftime("%H:%M"))
        time_label.setProperty("class", "info-label")
        emoji = QLabel(get_weather_emoji(int(row["weather_code"])))
        emoji.setStyleSheet("font-size: 28px;")
        temp = QLabel(f"{row['temperature']:.1f}°C")
        temp.setStyleSheet("font-size: 16px; font-weight: 600; color: #2d3748;")
        precip = QLabel(f"💧 {row['precipitation']:.1f}mm")
        precip.setStyleSheet("font-size: 11px; color: #4299e1;")
        wind = QLabel(f"🌬️ {row['wind_speed']:.0f}km/h")
        wind.setStyleSheet("font-size: 11px; color: #718096;")

        layout = QVBoxLayout(item)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for label in [time_label, emoji, temp, precip, wind]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

        return item

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

    def set_chart_backend(self, use_pyqtgraph: bool):
        """
        Set the charting backend.

        Args:
            use_pyqtgraph: If True, use pyqtgraph; otherwise use matplotlib
        """
        self.weather_chart.set_backend(use_pyqtgraph)
