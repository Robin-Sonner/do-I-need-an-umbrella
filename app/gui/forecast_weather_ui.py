"""Widget for displaying 7-day weather forecast."""

import pyqtgraph as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
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
from pyqtgraph import PlotWidget

from dinau import WeatherForecast

from .utilities import WEATHER_DESCRIPTION, get_weather_emoji


class ForecastWeatherWidget(QWidget):
    """Widget to display 7-day weather forecast."""

    def __init__(self, parent=None, use_pyqtgraph=True):
        super().__init__(parent)
        self.use_pyqtgraph = use_pyqtgraph
        if self.use_pyqtgraph:
            pg.setConfigOptions(antialias=True)
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

    def update_weather(self, weather: WeatherForecast):
        """
        Update the display with new weather data.

        Args:
            weather: 7-day weather forecast data
        """
        self._clear_layout()
        # Overview card with weekly summary
        overview_card = self._create_overview_card(weather)
        self.content_layout.addWidget(overview_card)
        # Umbrella recommendations
        umbrella_days = weather.umbrella_needed()
        if any(umbrella_days):
            umbrella_card = self._create_umbrella_recommendation_card(
                weather, umbrella_days
            )
            self.content_layout.addWidget(umbrella_card)
        # Daily forecast cards
        daily_cards = self._create_daily_forecast_cards(weather, umbrella_days)
        self.content_layout.addWidget(daily_cards)
        # Temperature trend chart
        if self.use_pyqtgraph:
            temp_chart = self._create_pyqtgraph_temperature_chart(weather)
        else:
            temp_chart = self._create_matplotlib_temperature_chart(weather)
        self.content_layout.addWidget(temp_chart)
        # Precipitation chart
        if self.use_pyqtgraph:
            precip_chart = self._create_pyqtgraph_precipitation_chart(weather)
        else:
            precip_chart = self._create_matplotlib_precipitation_chart(weather)
        self.content_layout.addWidget(precip_chart)
        # Add stretch to push content to the top
        self.content_layout.addStretch()

    @staticmethod
    def _create_overview_card(weather: WeatherForecast) -> QFrame:
        """Create the overview card with a weekly summary."""
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
    def _create_umbrella_recommendation_card(
        weather: WeatherForecast, umbrella_days: list[bool]
    ) -> QFrame:
        """Create a card with umbrella recommendations for specific days."""
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
    def _create_daily_forecast_cards(
        weather: WeatherForecast, umbrella_days: list[bool]
    ) -> QFrame:
        """Create individual cards for each day of the forecast."""
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
            needs_umbrella = umbrella_days[i]
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
                row_data, weather_code, needs_umbrella
            )
            # Arrange in grid: 4 columns for a wider layout
            row = i // 4
            col = i % 4
            grid.addWidget(day_card, row, col)
        layout.addLayout(grid)
        return container

    @staticmethod
    def _create_single_day_card(
        row_data, weather_code: int, needs_umbrella: bool
    ) -> QFrame:
        """Create a card for a single day's forecast."""
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
        date_label.setStyleSheet("font-size: 12px; color: #718096;")
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
        temp_range = QLabel(
            f"{row_data['temperature_min']:.0f}° - {row_data['temperature_max']:.0f}°C"
        )
        temp_range.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #2d3748; margin-top: 5px;"
        )
        temp_range.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(temp_range)
        # Precipitation probability
        precip = QLabel(f"💧 {row_data['precipitation_probability']:.0f}%")
        precip.setStyleSheet("font-size: 12px; color: #4299e1;")
        precip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(precip)
        # Umbrella indicator
        if needs_umbrella:
            umbrella = QLabel("☔ Umbrella needed")
            umbrella.setStyleSheet(
                "font-size: 11px; color: #e53e3e; font-weight: 600; margin-top: 3px;"
            )
            umbrella.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(umbrella)

        layout.addStretch()
        return card

    @staticmethod
    def _create_pyqtgraph_temperature_chart(weather: WeatherForecast) -> QFrame:
        """Create temperature trend chart using pyqtgraph."""
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        # Title
        title = QLabel("Temperature Trend")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        # Chart
        chart_widget = PlotWidget()
        chart_widget.setBackground("w")
        chart_widget.setMinimumHeight(300)
        chart_widget.showGrid(x=True, y=True, alpha=0.3)
        chart_widget.setLabel("left", "Temperature", units="°C")
        chart_widget.setLabel("bottom", "Day")
        chart_widget.setTitle("Daily Temperature Range")
        chart_widget.setMouseEnabled(x=False, y=False)
        chart_widget.setMenuEnabled(False)
        df = weather.daily_data
        days = list(range(len(df)))
        # Min temperature line
        min_pen = pg.mkPen(color="#3498db", width=3, style=Qt.PenStyle.DashLine)
        chart_widget.plot(
            days,
            df["temperature_min"].values,
            pen=min_pen,
            name="Min Temp",
            symbol="o",
            symbolSize=8,
            symbolBrush="#3498db",
        )
        # Max temperature line
        max_pen = pg.mkPen(color="#e74c3c", width=3)
        chart_widget.plot(
            days,
            df["temperature_max"].values,
            pen=max_pen,
            name="Max Temp",
            symbol="o",
            symbolSize=8,
            symbolBrush="#e74c3c",
        )
        # Fill between min and max
        fill = pg.FillBetweenItem(
            chart_widget.plot(days, df["temperature_min"].values, pen=None),
            chart_widget.plot(days, df["temperature_max"].values, pen=None),
            brush=pg.mkBrush(color=(231, 76, 60, 50)),
        )
        chart_widget.addItem(fill)
        # Set x-axis labels to day names
        x_ticks = [(i, df.iloc[i]["date"].strftime("%a %d")) for i in range(len(df))]
        ax = chart_widget.getAxis("bottom")
        ax.setTicks([x_ticks])
        chart_widget.addLegend()
        layout.addWidget(chart_widget)
        return card

    @staticmethod
    def _create_matplotlib_temperature_chart(weather: WeatherForecast) -> QFrame:
        """Create a temperature trend chart using matplotlib."""
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        # Title
        title = QLabel("Temperature Trend")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        # Chart
        fig = Figure(figsize=(10, 4), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumHeight(300)
        ax = fig.add_subplot(111)
        df = weather.daily_data
        days = list(range(len(df)))
        day_labels = [df.iloc[i]["date"].strftime("%a %d") for i in days]
        # Plot min and max temperatures
        ax.plot(
            days,
            df["temperature_min"].values,
            "b--o",
            linewidth=2,
            label="Min Temp",
            markersize=8,
        )
        ax.plot(
            days,
            df["temperature_max"].values,
            "r-o",
            linewidth=2,
            label="Max Temp",
            markersize=8,
        )
        # Fill between
        ax.fill_between(
            days,
            df["temperature_min"].values,
            df["temperature_max"].values,
            alpha=0.2,
            color="red",
        )
        ax.set_xlabel("Day")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title("Daily Temperature Range")
        ax.set_xticks(days)
        ax.set_xticklabels(day_labels, rotation=0)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        layout.addWidget(canvas)
        return card

    @staticmethod
    def _create_pyqtgraph_precipitation_chart(weather: WeatherForecast) -> QFrame:
        """Create precipitation probability chart using pyqtgraph."""
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        # Title
        title = QLabel("Precipitation Probability")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        # Chart
        chart_widget = PlotWidget()
        chart_widget.setBackground("w")
        chart_widget.setMinimumHeight(250)
        chart_widget.showGrid(x=True, y=True, alpha=0.3)
        chart_widget.setLabel("left", "Probability", units="%")
        chart_widget.setLabel("bottom", "Day")
        chart_widget.setTitle("Chance of Precipitation")
        chart_widget.setMouseEnabled(x=False, y=False)
        chart_widget.setMenuEnabled(False)
        df = weather.daily_data
        days = list(range(len(df)))
        # Bar graph for precipitation probability
        bar_graph = pg.BarGraphItem(
            x=days,
            height=df["precipitation_probability"].values,
            width=0.6,
            brush="#3498db80",
            pen=pg.mkPen("#3498db", width=2),
        )
        chart_widget.addItem(bar_graph)
        # Set y-axis range
        chart_widget.setYRange(0, 105)
        # Set x-axis labels
        x_ticks = [(i, df.iloc[i]["date"].strftime("%a %d")) for i in range(len(df))]
        ax = chart_widget.getAxis("bottom")
        ax.setTicks([x_ticks])
        layout.addWidget(chart_widget)
        return card

    @staticmethod
    def _create_matplotlib_precipitation_chart(weather: WeatherForecast) -> QFrame:
        """Create a precipitation probability chart using matplotlib."""
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        # Title
        title = QLabel("Precipitation Probability")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        # Chart
        fig = Figure(figsize=(10, 3.5), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumHeight(250)
        ax = fig.add_subplot(111)
        df = weather.daily_data
        days = list(range(len(df)))
        day_labels = [df.iloc[i]["date"].strftime("%a %d") for i in days]
        # Bar chart
        ax.bar(
            days,
            df["precipitation_probability"].values,
            color="#3498db",
            alpha=0.7,
            edgecolor="#2980b9",
            linewidth=2,
        )
        ax.set_xlabel("Day")
        ax.set_ylabel("Probability (%)")
        ax.set_title("Chance of Precipitation")
        ax.set_xticks(days)
        ax.set_xticklabels(day_labels, rotation=0)
        ax.set_ylim(0, 105)
        ax.grid(True, alpha=0.3, axis="y")

        fig.tight_layout()
        layout.addWidget(canvas)

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
        self.use_pyqtgraph = use_pyqtgraph
