"""Widget and Manager for the application settings."""

import configparser
from pathlib import Path

from dinau import Location
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class ConfigManager:
    """Manages application configuration stored in config.ini."""

    def __init__(self, config_file: str = "config.ini"):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self):
        """Load configuration from a file if it exists."""
        if self.config_file.exists():
            self.config.read(self.config_file)

    def config_exists(self) -> bool:
        """
        Check if the configuration file exists.

        Returns:
            True if the config file exists, False otherwise
        """
        return self.config_file.exists() and self.has_required_settings()

    def has_required_settings(self) -> bool:
        """
        Check if all required settings are present.

        Returns:
            True if all required settings exist, False otherwise
        """
        try:
            return (
                self.config.has_section("General")
                and self.config.has_option("General", "location")
                and self.config.has_option("General", "use_pyqtgraph")
            )
        except Exception:
            return False

    def get_location(self) -> str:
        """
        Get the configured location.

        Returns:
            Location name or default value
        """
        if self.config.has_option("General", "location"):
            return self.config.get("General", "location")
        return "Freiburg"

    def get_use_pyqtgraph(self) -> bool:
        """
        Get the chart library preference.

        Returns:
            True for pyqtgraph, False for matplotlib
        """
        if self.config.has_option("General", "use_pyqtgraph"):
            return self.config.getboolean("General", "use_pyqtgraph")
        return True

    def save_settings(self, location: str, use_pyqtgraph: bool):
        """
        Save settings to a configuration file.

        Args:
            location: Location name
            use_pyqtgraph: Whether to use pyqtgraph (True) or matplotlib (False)
        """
        if not self.config.has_section("General"):
            self.config.add_section("General")
        self.config.set("General", "location", location)
        self.config.set("General", "use_pyqtgraph", str(use_pyqtgraph))
        with open(self.config_file, "w") as f:
            self.config.write(f)


class SettingsWidget(QWidget):
    """Widget for application settings."""

    settings_saved = pyqtSignal(
        str, bool, object
    )  # location, use_pyqtgraph, location_obj

    def __init__(
        self, parent=None, location: str = "Freiburg", use_pyqtgraph: bool = True
    ):
        """
        Initialize the settings widget.

        Args:
            parent: Parent widget
            location: Initial location value
            use_pyqtgraph: Initial chart library preference
        """
        super().__init__(parent)
        self.location = location
        self.use_pyqtgraph = use_pyqtgraph
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
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(10, 10, 10, 10)
        # Title
        title_label = QLabel("Settings")
        title_label.setProperty("class", "title")
        content_layout.addWidget(title_label)
        # Location Settings Card
        location_card = self._create_location_card()
        content_layout.addWidget(location_card)
        # Chart Library Settings Card
        chart_card = self._create_chart_library_card()
        content_layout.addWidget(chart_card)
        # Save Button
        save_button = QPushButton("Save Settings")
        save_button.setProperty("class", "save-btn")
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        save_button.setMinimumHeight(45)
        save_button.clicked.connect(self._on_save_clicked)
        content_layout.addWidget(save_button)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _create_location_card(self) -> QFrame:
        """Create the location settings card."""
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        # Card title
        title = QLabel("Location")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        # Description
        desc = QLabel(
            "Enter the name of your city to get weather information."
            "Examples: Freiburg, Berlin"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #718096; font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(desc)
        # Location input
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter city name...")
        self.location_input.setText(self.location)
        self.location_input.setMinimumHeight(40)
        layout.addWidget(self.location_input)
        return card

    def _create_chart_library_card(self) -> QFrame:
        """Create the chart library settings card."""
        card = QFrame()
        card.setProperty("class", "weather-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        # Card title
        title = QLabel("Chart Library")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        # Description
        desc = QLabel("Choose which library to use for rendering weather charts. ")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #718096; font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(desc)
        # Radio button group
        self.chart_button_group = QButtonGroup(self)
        # PyQtGraph option
        pyqtgraph_container = QFrame()
        pyqtgraph_container.setProperty("class", "chart")
        pyqtgraph_layout = QVBoxLayout(pyqtgraph_container)
        pyqtgraph_layout.setSpacing(5)
        self.pyqtgraph_radio = QRadioButton("PyQtGraph")
        self.pyqtgraph_radio.setStyleSheet("font-size: 15px; color: #2d3748;")
        self.pyqtgraph_radio.setChecked(self.use_pyqtgraph)
        self.chart_button_group.addButton(self.pyqtgraph_radio, 1)
        pyqtgraph_layout.addWidget(self.pyqtgraph_radio)
        layout.addWidget(pyqtgraph_container)
        # Matplotlib option
        matplotlib_container = QFrame()
        matplotlib_layout = QVBoxLayout(matplotlib_container)
        matplotlib_container.setProperty("class", "chart")
        matplotlib_layout.setSpacing(5)
        self.matplotlib_radio = QRadioButton("Matplotlib")
        self.matplotlib_radio.setStyleSheet("font-size: 15px;color: #2d3748;")
        self.matplotlib_radio.setChecked(not self.use_pyqtgraph)
        self.chart_button_group.addButton(self.matplotlib_radio, 2)
        matplotlib_layout.addWidget(self.matplotlib_radio)
        layout.addWidget(matplotlib_container)
        return card

    def _on_save_clicked(self):
        """Handle save button click by validating and emitting a signal with the updated settings."""
        location = self.location_input.text().strip()
        if not location:
            QMessageBox.critical(
                self, "Location Empty", "Please enter a valid location."
            )
            return

        # Validate that the location exists and by creating a Location object
        try:
            location_obj = Location(location)
        except ValueError:
            QMessageBox.critical(
                self,
                "Invalid Location",
                f"The location '{location}' could not be found.\n\n"
                "Maybe there's a different name you could try? Also check for typos.",
            )
            return
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Validating Location",
                f"An error occurred while validating the location:\n{str(e)}\n\n"
                "Please check your internet connection and try again.",
            )
            return

        use_pyqtgraph = self.pyqtgraph_radio.isChecked()
        # We can emit the Location for later use by the MainWindow
        self.settings_saved.emit(location, use_pyqtgraph, location_obj)

    def update_settings(self, location: str, use_pyqtgraph: bool):
        """
        Update the displayed settings.

        Args:
            location: Location name
            use_pyqtgraph: Chart library preference
        """
        self.location = location
        self.use_pyqtgraph = use_pyqtgraph
        self.location_input.setText(location)
        self.pyqtgraph_radio.setChecked(use_pyqtgraph)
        self.matplotlib_radio.setChecked(not use_pyqtgraph)
