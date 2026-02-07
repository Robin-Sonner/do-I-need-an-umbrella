import pyqtgraph as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from pyqtgraph import PlotWidget

from dinau import DailyWeather

from .utilities import get_weather_emoji


class TodayWeatherWidget(QWidget):
    """Widget to display today's weather conditions"""

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

    def update_weather(self, weather: DailyWeather):
        """
        Update the display with new weather data.

        Args:
            weather: Today's weather data (full or lite version)
        """
        self._clear_layout()
        # Main overview card
        overview_card = TodayWeatherWidget._create_overview_card(weather)
        self.content_layout.addWidget(overview_card)
        # Umbrella recommendation
        if weather.umbrella_needed():
            umbrella_card = TodayWeatherWidget._create_umbrella_card()
            self.content_layout.addWidget(umbrella_card)
        # Charts
        if self.use_pyqtgraph:
            charts_card = TodayWeatherWidget._create_pyqtgraph(weather)
        else:
            charts_card = TodayWeatherWidget._create_matplotlib(weather)
        self.content_layout.addWidget(charts_card)
        # Hourly forecast
        hourly_card = TodayWeatherWidget._create_hourly_card(weather)
        self.content_layout.addWidget(hourly_card)
        # Add stretch to push content to the top
        self.content_layout.addStretch()

    @staticmethod
    def _create_overview_card(weather: DailyWeather) -> QFrame:
        """Create the overview card with a daily summary."""
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
        """Create a card recommending to bring an umbrella."""
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

    @staticmethod
    def _create_pyqtgraph(weather: DailyWeather) -> QFrame:
        """Create charts using pyqtgraph."""
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        # Title
        title = QLabel("Weather Charts")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)

        df = weather.hourly_data

        # Temperature and Precipitation Chart
        temp_precip_widget = PlotWidget()
        temp_precip_widget.setBackground("w")
        temp_precip_widget.setMinimumHeight(300)
        temp_precip_widget.showGrid(x=True, y=True, alpha=0.3)
        temp_precip_widget.setLabel("left", "Temperature", units="°C", color="#e74c3c")
        temp_precip_widget.setLabel(
            "right", "Precipitation", units="mm", color="#3498db"
        )
        temp_precip_widget.setLabel("bottom", "Hour")
        temp_precip_widget.setTitle("Temperature & Precipitation")
        temp_precip_widget.setMouseEnabled(x=False, y=False)
        temp_precip_widget.setMenuEnabled(False)
        # Create hours for x-axis
        hours = [i for i in range(len(df))]
        # Temperature line (left axis)
        temp_pen = pg.mkPen(color="#e74c3c", width=3)
        _ = temp_precip_widget.plot(
            hours, df["temperature"].values, pen=temp_pen, name="Temperature"
        )
        # Precipitation bars
        precip_viewbox = pg.ViewBox()
        temp_precip_widget.scene().addItem(precip_viewbox)
        temp_precip_widget.getAxis("right").linkToView(precip_viewbox)
        precip_viewbox.setXLink(temp_precip_widget)
        precip_viewbox.setMouseEnabled(x=False, y=False)

        def update_views():
            precip_viewbox.setGeometry(
                temp_precip_widget.getViewBox().sceneBoundingRect()
            )
            precip_viewbox.linkedViewChanged(
                temp_precip_widget.getViewBox(), precip_viewbox.XAxis
            )

        update_views()
        temp_precip_widget.getViewBox().sigResized.connect(update_views)

        # Create the bar graph for precipitation
        width = 0.6
        bar_graph = pg.BarGraphItem(
            x=hours,
            height=df["precipitation"].values,
            width=width,
            brush="#3498db80",
            pen=pg.mkPen("#3498db", width=1),
        )
        precip_viewbox.addItem(bar_graph)

        # Set the precipitation axis range
        max_precip = df["precipitation"].max()
        if max_precip > 0:
            precip_viewbox.setYRange(0, max_precip * 1.2)
        else:
            precip_viewbox.setYRange(0, 1)

        layout.addWidget(temp_precip_widget)

        # Wind Speed Chart
        wind_widget = PlotWidget()
        wind_widget.setBackground("w")
        wind_widget.setMinimumHeight(250)
        wind_widget.showGrid(x=True, y=True, alpha=0.3)
        wind_widget.setLabel("left", "Wind Speed", units="km/h", color="#2ecc71")
        wind_widget.setLabel("bottom", "Hour")
        wind_widget.setTitle("Wind Speed")
        wind_widget.setMouseEnabled(x=False, y=False)
        wind_widget.setMenuEnabled(False)

        # Create a bar graph for wind speed
        bar_graph_wind = pg.BarGraphItem(
            x=hours,
            height=df["wind_speed"].values,
            width=0.8,
            brush="#2ecc7180",
            pen=pg.mkPen("#2ecc71", width=1),
        )
        wind_widget.addItem(bar_graph_wind)
        # Set x-axis ticks to show every 2 hours
        x_ticks = [(i, str(i)) for i in range(0, 24, 2)]
        ax = wind_widget.getAxis("bottom")
        ax.setTicks([x_ticks])
        layout.addWidget(wind_widget)

        return card

    @staticmethod
    def _create_matplotlib(weather: DailyWeather) -> QFrame:
        """Create charts using matplotlib"""
        card = QFrame()
        card.setProperty("class", "weather-card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Weather Charts (Matplotlib)")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)

        df = weather.hourly_data
        hours = list(range(len(df)))

        # Temperature and Precipitation Chart
        fig1 = Figure(figsize=(8, 4), dpi=100)
        canvas1 = FigureCanvasQTAgg(fig1)
        canvas1.setMinimumHeight(300)
        ax1 = fig1.add_subplot(111)
        ax2 = ax1.twinx()
        # Temperature line
        _ = ax1.plot(
            hours, df["temperature"].values, "r-", linewidth=2, label="Temperature"
        )
        ax1.set_xlabel("Hour")
        ax1.set_ylabel("Temperature (°C)", color="r")
        ax1.tick_params(axis="y", labelcolor="r")
        ax1.grid(True, alpha=0.3)
        # Precipitation bars
        _ = ax2.bar(
            hours,
            df["precipitation"].values,
            alpha=0.5,
            color="b",
            label="Precipitation",
        )
        ax2.set_ylabel("Precipitation (mm)", color="b")
        ax2.tick_params(axis="y", labelcolor="b")
        ax1.set_title("Temperature & Precipitation")
        fig1.tight_layout()
        layout.addWidget(canvas1)

        # Wind Speed Chart
        fig2 = Figure(figsize=(8, 3), dpi=100)
        canvas2 = FigureCanvasQTAgg(fig2)
        canvas2.setMinimumHeight(250)
        ax3 = fig2.add_subplot(111)
        ax3.bar(hours, df["wind_speed"].values, color="g", alpha=0.6)
        ax3.set_xlabel("Hour")
        ax3.set_ylabel("Wind Speed (km/h)")
        ax3.set_title("Wind Speed")
        ax3.grid(True, alpha=0.3)
        fig2.tight_layout()
        layout.addWidget(canvas2)
        return card

    @staticmethod
    def _create_hourly_card(weather: DailyWeather) -> QFrame:
        """Create the hourly forecast card."""
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
    def _create_hourly_item(row) -> QFrame:
        """Create a single hourly forecast item."""
        item = QFrame()
        item.setProperty("class", "info-card")
        item.setMinimumWidth(100)
        item.setMaximumWidth(120)

        # Time
        time_label = QLabel(row["date"].strftime("%H:%M"))
        time_label.setProperty("class", "info-label")
        # Weather emoji
        emoji = QLabel(get_weather_emoji(int(row["weather_code"])))
        emoji.setStyleSheet("font-size: 28px;")
        # Temperature
        temp = QLabel(f"{row['temperature']:.1f}°C")
        temp.setStyleSheet("font-size: 16px; font-weight: 600; color: #2d3748;")
        # Precipitation
        precip = QLabel(f"💧 {row['precipitation']:.1f}mm")
        precip.setStyleSheet("font-size: 11px; color: #4299e1;")
        # Wind speed
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
        self.use_pyqtgraph = use_pyqtgraph
