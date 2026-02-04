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
from .today_weather_ui import TodayWeatherWidget
from .utilities import STYLESHEET, create_placeholder


class WeatherWorker(QThread):
    """Worker thread for fetching weather data."""

    current_weather_ready = pyqtSignal(object)
    today_weather_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, location_name: str, lite: bool = False):
        super().__init__()
        self.location_name = location_name
        self.lite = lite
        self._is_running = True

    def run(self):
        """Fetch the weather data in a background thread (Avoid application freezing)"""
        try:
            # Create the location and weather client
            location = Location(self.location_name)
            client = WeatherClient(location)
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
        self.location_name = "Freiburg"  # TODO: make configurable via Settings Tab
        self.use_pyqtgraph = True  # TODO: make configurable via Settings Tab
        self.worker = None
        self._setup_ui()
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
        self.tab_widget.addTab(create_placeholder(), "7-Day Forecast")
        # Settings tab
        self.tab_widget.addTab(create_placeholder(), "Settings")

        layout.addWidget(self.tab_widget)

    def _create_header(self) -> QWidget:
        """Create the header with the location and refresh button."""
        header = QWidget()
        header.setStyleSheet(
            "background-color: white; border-bottom: 1px solid #e2e8f0;"
        )
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
        self.worker = WeatherWorker(self.location_name)
        self.worker.current_weather_ready.connect(self._on_current_weather_ready)
        self.worker.today_weather_ready.connect(self._on_today_weather_ready)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.finished.connect(self._on_loading_finished)
        self.worker.start()

    def _on_current_weather_ready(self, weather):
        """Handle current weather data received."""
        self.current_weather_widget.update_weather(weather)

    def _on_today_weather_ready(self, weather):
        """Handle today's weather data received."""
        self.today_weather_widget.update_weather(weather)

    def _on_error(self, error_message: str):
        """Handle error during data loading."""
        self.current_weather_widget.show_error(error_message)
        self.today_weather_widget.show_error(error_message)

        # Show error dialog
        QMessageBox.critical(
            self,
            "Error Loading Weather Data",
            f"Failed to load weather data:\n{error_message}\n"
            "Please check your internet connection and try again.",
        )

    def _on_loading_finished(self):
        """Handle loading finished."""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh")

    def set_chart_backend(self, use_pyqtgraph: bool):
        """
        Set the chart backend for weather displays.

        Args:
            use_pyqtgraph: If True, use pyqtgraph; otherwise use matplotlib
        """
        self.use_pyqtgraph = use_pyqtgraph
        self.today_weather_widget.set_chart_backend(use_pyqtgraph)
        self._load_weather_data()  # Reload data to refresh charts

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop the worker thread if running
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()
