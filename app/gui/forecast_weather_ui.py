"""Widget for displaying a 7-day weather forecast."""

from enum import Enum
from typing import Optional

import pandas as pd
from dinau import WeatherForecast
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .utilities import WEATHER_DESCRIPTION, get_weather_emoji
from .weather_chart import WeatherChart


class DisplayMode(Enum):
    """Display modes for temperature charts."""

    MIN_MAX = "Min/Max Temperature"
    REAL_APPARENT = "Real/Apparent Temperature"


class ForecastWeatherWidget(QWidget):
    """Widget to display 7-day weather forecast."""

    def __init__(self, parent=None, use_pyqtgraph=True):
        """
        Initialize the widget.

        Args:
            parent: Parent widget (optional)
            use_pyqtgraph: If True, use pyqtgraph for charting; otherwise matplotlib
        """
        super().__init__(parent)
        self.current_mode = DisplayMode.MIN_MAX
        self.weather_chart = WeatherChart(use_pyqtgraph)
        self.current_weather: Optional[WeatherForecast] = None
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

    def _create_mode_selector(self) -> QFrame:
        """
        Create a mode selector widget for chart display modes.

        Returns:
            QFrame containing the mode selector
        """
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        label = QLabel("Chart Display Mode:")
        label.setProperty("class", "subtitle")
        layout.addWidget(label)
        # Combo box for display modes
        self.mode_combo = QComboBox()
        for mode in DisplayMode:
            self.mode_combo.addItem(mode.value, mode)
        # Set the index according to the current mode
        index = self.mode_combo.findData(self.current_mode)
        self.mode_combo.setCurrentIndex(index)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.mode_combo.setMinimumWidth(300)
        layout.addWidget(self.mode_combo)

        layout.addStretch()
        return card

    def _on_mode_changed(self, index: int):
        """
        Handle mode selection change.

        Args:
            index: Index of the selected mode
        """
        self.current_mode = self.mode_combo.itemData(index)
        if self.current_weather:
            # Reuse the update function to refresh the charts
            self.update_weather(self.current_weather)

    def _prepare_daily_chart_data(self, weather: WeatherForecast) -> dict:
        """
        Prepare daily data for charting based on the current display mode.

        Args:
            weather: Weather forecast data

        Returns:
            Dictionary with chart configuration
        """
        df = weather.daily_data
        x_labels = [(i, df.iloc[i]["date"].strftime("%a %d")) for i in range(len(df))]

        if self.current_mode == DisplayMode.MIN_MAX:
            return {
                "data": df,
                "temp1_col": "temperature_min",
                "temp2_col": "temperature_max",
                "precip_col": "precipitation_sum",
                "x_labels": x_labels,
                "title": "Min/Max Temperature & Precipitation",
                "label1": "Min Temp",
                "label2": "Max Temp",
                "color1": "#3498db",
                "color2": "#e74c3c",
            }
        else:  # REAL_APPARENT
            return {
                "data": df,
                "temp1_col": "temperature_mean",
                "temp2_col": "apparent_temperature_mean",
                "precip_col": "precipitation_sum",
                "x_labels": x_labels,
                "title": "Real/Apparent Temperature & Precipitation",
                "label1": "Temperature",
                "label2": "Feels Like",
                "color1": "#e74c3c",
                "color2": "#ff9800",
            }

    def update_weather(self, weather: WeatherForecast):
        """
        Update the display with new weather data.

        Args:
            weather: 7-day weather forecast data
        """
        self.current_weather = weather
        self._clear_layout()
        # Overview card with weekly summary
        overview_card = self._create_overview_card(weather)
        self.content_layout.addWidget(overview_card)
        # Umbrella recommendations
        umbrella_days = weather.umbrella_needed()
        if any(umbrella_days):
            umbrella_card = self._create_umbrella_recommendation_card(umbrella_days)
            self.content_layout.addWidget(umbrella_card)
        # Daily forecast cards
        daily_cards = self._create_daily_forecast_cards(weather)
        self.content_layout.addWidget(daily_cards)
        # Temperature chart with current mode
        chart_config = self._prepare_daily_chart_data(weather)
        temp_chart_frame = self._create_chart_card(chart_config)
        self.content_layout.addWidget(temp_chart_frame)
        # Mode selector
        mode_selector = self._create_mode_selector()
        self.content_layout.addWidget(mode_selector)
        # Add stretch to push content to the top
        self.content_layout.addStretch()

    def _create_chart_card(self, config: dict) -> QFrame:
        """
        Create a chart card using the WeatherChart factory.

        Args:
            config: Chart configuration dictionary

        Returns:
            QFrame containing the chart
        """
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        # Title
        title = QLabel(self.current_mode.value)
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        # Create charts
        chart = self.weather_chart.create_temperature_precipitation_chart(**config)
        chart.setMinimumHeight(350)
        layout.addWidget(chart)
        return card

    @staticmethod
    def _create_overview_card(weather: WeatherForecast) -> QFrame:
        """
        Create the overview card with a weekly summary.

        Args:
            weather: 7-day weather forecast data

        Returns:
            QFrame containing the summary
        """
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("7-Day Weather Forecast")
        title.setProperty("class", "title")
        layout.addWidget(title)
        df = weather.daily_data
        avg_temp_min = df["temperature_min"].mean()
        avg_temp_max = df["temperature_max"].mean()
        max_precip_prob = df["precipitation_probability"].max()
        summary_layout = QHBoxLayout()
        temp_label = QLabel(f"Average: {avg_temp_min:.1f}°C - {avg_temp_max:.1f}°C")
        temp_label.setProperty("class", "subtitle")
        summary_layout.addWidget(temp_label)
        summary_layout.addStretch()
        precip_label = QLabel(f"Max precipitation chance: {max_precip_prob:.0f}%")
        precip_label.setProperty("class", "subtitle")
        summary_layout.addWidget(precip_label)

        layout.addLayout(summary_layout)
        return card

    @staticmethod
    def _create_umbrella_recommendation_card(umbrella_days: list[bool]) -> QFrame:
        """
        Create a card with umbrella recommendations for specific days.

        Args:
            umbrella_days: List of booleans indicating whether an umbrella is needed for each day

        Returns:
            QFrame containing the recommendation
        """
        card = QFrame()
        card.setStyleSheet(
            "background-color: #ebf8ff; border: 2px solid #4299e1; border-radius: 8px;"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        header_layout = QHBoxLayout()
        emoji = QLabel("☔")
        emoji.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(emoji)
        # Count days needing umbrella
        umbrella_count = sum(umbrella_days)
        title_text = f"Umbrella needed on {umbrella_count} day{'s' if umbrella_count != 1 else ''} this week"
        text = QLabel(title_text)
        text.setStyleSheet("color: #2c5282; font-size: 16px; font-weight: 600;")
        header_layout.addWidget(text)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        return card

    @staticmethod
    def _create_daily_forecast_cards(weather: WeatherForecast) -> QFrame:
        """
        Create individual cards for each day of the forecast.

        Args:
            weather: 7-day weather forecast data

        Returns:
            QFrame containing the weather information for each day
        """
        container = QFrame()
        container.setProperty("class", "weather-card")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Daily Breakdown")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)

        # Grid for daily cards
        grid = QGridLayout()
        grid.setSpacing(15)
        df = weather.daily_data

        for i in range(len(df)):
            row_data = df.iloc[i]
            # Get the most common weather code for this day
            day_date = row_data["date"].date()
            hourly_day_data = weather.hourly_data[
                weather.hourly_data["date"].dt.date == day_date
            ]
            if len(hourly_day_data) > 0:
                weather_code = int(hourly_day_data["weather_code"].mode().iloc[0])
            else:
                weather_code = 0
            day_card = ForecastWeatherWidget._create_single_day_card(
                row_data, weather_code
            )
            # Arrange in grid: 4 columns for a wider layout
            row = i // 4
            col = i % 4
            grid.addWidget(day_card, row, col)
        layout.addLayout(grid)
        return container

    @staticmethod
    def _create_single_day_card(row_data: pd.Series, weather_code: int) -> QFrame:
        """
        Create a card for a single day's forecast.

        Args:
            row_data: Series containing the weather data for a single day
            weather_code: Weather code for the day

        Returns:
            QFrame containing the forecast information for this day
        """
        card = QFrame()
        card.setProperty("class", "info-card")
        card.setMinimumHeight(180)
        card.setMinimumWidth(180)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        # Day name
        date = row_data["date"]
        day_label = QLabel(date.strftime("%A"))
        day_label.setProperty("class", "info-label")
        day_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #2d3748;")
        day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(day_label)
        # Date
        date_label = QLabel(date.strftime("%b %d"))
        date_label.setProperty("class", "info-label")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(date_label)
        # Weather emoji
        emoji = QLabel(get_weather_emoji(weather_code))
        emoji.setStyleSheet("font-size: 36px;")
        emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(emoji)
        # Weather description
        desc = QLabel(WEATHER_DESCRIPTION.get(weather_code, ""))
        desc.setStyleSheet("font-size: 11px; color: #4a5568;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        # Temperature range
        temp_min = row_data["temperature_min"]
        temp_max = row_data["temperature_max"]
        temp_label = QLabel(f"{temp_min:.0f}° - {temp_max:.0f}°")
        temp_label.setProperty("class", "temperature-range")
        temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(temp_label)
        # Precipitation
        precip = row_data["precipitation_sum"]
        precip_label = QLabel(f"💧 {precip:.0f}mm")
        precip_label.setStyleSheet("font-size: 14px; color: #4a5568;")
        precip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(precip_label)

        layout.addStretch()
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

    def set_chart_backend(self, use_pyqtgraph: bool):
        """
        Set the charting backend.

        Args:
            use_pyqtgraph: If True, use pyqtgraph; otherwise use matplotlib
        """
        self.weather_chart.set_backend(use_pyqtgraph)
