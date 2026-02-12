"""Main window for the weather application."""

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from dinau import Location, WeatherClient

from .current_weather_ui import CurrentWeatherWidget
from .forecast_weather_ui import ForecastWeatherWidget
from .settings_ui import ConfigManager, SettingsWidget
from .stylesheet import STYLESHEET
from .today_weather_ui import TodayWeatherWidget


class WeatherWorker(QThread):
    """Worker thread for fetching weather data."""

    current_weather_ready = pyqtSignal(object)
    today_weather_ready = pyqtSignal(object)
    forecast_weather_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, location: Location | str, lite: bool = False):
        super().__init__()
        self.location = location
        self.lite = lite
        self._is_running = True

    def run(self):
        """Fetch the weather data in a background thread (Avoid application freezing)"""
        try:
            if isinstance(self.location, str):
                self.location = Location(self.location)
            # Create the weather client
            client = WeatherClient(self.location)
            if not self._is_running:
                return
            # Fetch current weather
            current = client.get_weather_current(lite=self.lite)
            self.current_weather_ready.emit(current)
            if not self._is_running:
                return
            # Fetch today's weather
            today = client.get_weather_today(lite=self.lite)
            self.today_weather_ready.emit(today)
            if not self._is_running:
                return
            # Fetch 7-day forecast
            forecast = client.get_weather_forecast(days=7, lite=self.lite)
            self.forecast_weather_ready.emit(forecast)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()

    def stop(self):
        """Stop the worker thread."""
        self._is_running = False


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.location_name = self.config_manager.get_location()
        self.use_pyqtgraph = self.config_manager.get_use_pyqtgraph()
        self.location = None
        self.worker = None
        self._setup_ui()

        # Show the Settings tab if the config is invalid (or missing), else load weather data
        if not self.config_manager.config_exists():
            self.tab_widget.setCurrentIndex(3)  # Settings tab
            self._toggle_weather_tabs(False)
        else:
            self._load_weather_data()

        self.setStyleSheet(STYLESHEET)

    def _setup_ui(self):
        """Initialize the user interface."""
        # Basic Initialization
        self.setWindowTitle("Do I need an umbrella?")
        self.setMinimumSize(900, 700)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        header = self._create_header()
        layout.addWidget(header)
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # Current weather tab
        self.current_weather_widget = CurrentWeatherWidget()
        self.tab_widget.addTab(self.current_weather_widget, "Current Weather")
        # Today's weather tab
        self.today_weather_widget = TodayWeatherWidget(use_pyqtgraph=self.use_pyqtgraph)
        self.tab_widget.addTab(self.today_weather_widget, "Today's Forecast")
        # Weather Forecast tab
        self.forecast_weather_widget = ForecastWeatherWidget(
            use_pyqtgraph=self.use_pyqtgraph
        )
        self.tab_widget.addTab(self.forecast_weather_widget, "7-Day Forecast")
        # Settings tab
        self.settings_widget = SettingsWidget(
            location=self.location_name, use_pyqtgraph=self.use_pyqtgraph
        )
        self.settings_widget.settings_saved.connect(self._on_settings_saved)
        self.tab_widget.addTab(self.settings_widget, "Settings")

        layout.addWidget(self.tab_widget)

    def _create_header(self) -> QWidget:
        """Create the header with the location and refresh button."""
        header = QWidget()
        header.setFixedHeight(70)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 15, 30, 15)
        # Location label
        self.location_label = QLabel(self.location_name)
        self.location_label.setProperty("class", "title")
        layout.addWidget(self.location_label)
        layout.addStretch()
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setProperty("class", "refresh-btn")
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.clicked.connect(self._load_weather_data)
        layout.addWidget(self.refresh_button)
        return header

    def _load_weather_data(self):
        """Load weather data in a background thread."""
        # Stop existing worker if any
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        # Disable the refresh button while loading
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Loading...")
        # Create and start the worker
        location = self.location if self.location else self.location_name
        self.worker = WeatherWorker(location)
        self.worker.current_weather_ready.connect(self._on_current_weather_ready)
        self.worker.today_weather_ready.connect(self._on_today_weather_ready)
        self.worker.forecast_weather_ready.connect(self._on_forecast_weather_ready)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.finished.connect(self._on_loading_finished)
        self.worker.start()

    def _on_current_weather_ready(self, weather):
        """Handle current weather data received."""
        self.current_weather_widget.update_weather(weather)

    def _on_today_weather_ready(self, weather):
        """Handle today's weather data received."""
        self.today_weather_widget.update_weather(weather)

    def _on_forecast_weather_ready(self, weather):
        """Handle 7-day forecast weather data received."""
        self.forecast_weather_widget.update_weather(weather)

    def _on_error(self, error_message: str):
        """Handle error during data loading."""
        QMessageBox.critical(
            self,
            "Error Loading Weather Data",
            f"Failed to load weather data:\n{error_message}\n\nPlease check your internet connection and try again.",
        )

    def _on_loading_finished(self):
        """Handle loading finished."""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh")

    def _on_settings_saved(
        self, location: str, use_pyqtgraph: bool, location_obj: Location
    ):
        """
        Handle settings saved event.

        Args:
            location: New location name
            use_pyqtgraph: Chart library preference
            location_obj: Validated Location object
        """
        # Save to the config file
        self.config_manager.save_settings(location, use_pyqtgraph)
        # Update internal state
        self.use_pyqtgraph = use_pyqtgraph
        self.location_name = location
        self.location = location_obj  # Reuse the validated Location object
        self.location_label.setText(location)
        self.today_weather_widget.set_chart_backend(use_pyqtgraph)
        self.forecast_weather_widget.set_chart_backend(use_pyqtgraph)
        self._toggle_weather_tabs(True)
        self._load_weather_data()
        self.tab_widget.setCurrentIndex(0)
        # Show a confirmation message
        QMessageBox.information(
            self,
            "Settings Saved",
            f"Settings saved successfully!\nLocation: {location}.\nChart Library: {'PyQtGraph' if use_pyqtgraph else 'Matplotlib'}",
        )

    def _toggle_weather_tabs(self, enable: bool):
        """Enable/Disable weather-related tabs"""
        self.tab_widget.setTabEnabled(0, enable)  # Current Weather
        self.tab_widget.setTabEnabled(1, enable)  # Today's Forecast
        self.tab_widget.setTabEnabled(2, enable)  # 7-Day Forecast

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop the worker thread if running
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()
