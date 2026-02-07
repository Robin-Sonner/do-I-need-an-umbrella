from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

WEATHER_DESCRIPTION = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_emoji(weather_code: int) -> str:
    """
    Get an emoji representation of the weather code.

    Args:
        weather_code: WMO weather code

    Returns:
        Weather emoji
    """
    if weather_code == 0:
        return "☀️"
    elif weather_code in [1, 2]:
        return "⛅"
    elif weather_code == 3:
        return "☁️"
    elif weather_code in [45, 48]:
        return "🌫️"
    elif weather_code in range(51, 58):
        return "🌧️"
    elif weather_code in range(61, 68):
        return "🌧️"
    elif weather_code in range(71, 78):
        return "❄️"
    elif weather_code in range(80, 87):
        return "🌦️"
    elif weather_code in range(95, 100):
        return "⛈️"
    else:
        return ""


def create_placeholder() -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label = QLabel("Coming soon")
    label.setStyleSheet("font-size: 18px; color: #718096;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    return widget


STYLESHEET = """
/* Main Window */
QMainWindow {
    background-color: #f5f7fa;
}

/* Tab Widget */
QTabWidget::pane {
    border: none;
    background-color: white;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #e8ecef;
    color: #4a5568;
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
    min-width: 120px;
}

QTabBar::tab:selected {
    background-color: white;
    color: #2d3748;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #dfe3e8;
}

/* Weather Cards */
QFrame[class="weather-card"] {
    background-color: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

QFrame[class="info-card"] {
    background-color: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

QLabel {
    line-height: 1.5;
}

QLabel[class="title"] {
    font-size: 24px;
    font-weight: 600;
    color: #1a202c;
}

QLabel[class="subtitle"] {
    font-size: 16px;
    font-weight: 500;
    color: #4a5568;
}

QLabel[class="temperature-main"] {
    font-size: 64px;
    font-weight: 300;
    color: #2d3748;
}

QLabel[class="temperature-range"] {
    font-size: 20px;
    font-weight: 400;
    color: #4a5568;
}

QLabel[class="info-label"] {
    font-size: 12px;
    font-weight: 500;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel[class="info-value"] {
    font-size: 20px;
    font-weight: 600;
    color: #2d3748;
}

QLabel[class="weather-description"] {
    font-size: 18px;
    font-weight: 400;
    color: #4a5568;
}

/* Scroll Area */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #f7fafc;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e0;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0aec0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f7fafc;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e0;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0aec0;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Loading Label */
QLabel[class="loading"] {
    font-size: 16px;
    color: #718096;
}

/* Error Label */
QLabel[class="error"] {
    font-size: 14px;
    color: #e53e3e;
    background-color: #fff5f5;
    border: 1px solid #fc8181;
    border-radius: 6px;
    padding: 12px;
}

/* Refresh Button */
QPushButton[class="refresh-btn"] {
    background-color: #4299e1;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 14px;
}

QPushButton[class="refresh-btn"]:hover {
    background-color: #3182ce;
}

QPushButton[class="refresh-btn"]:pressed {
    background-color: #2c5282;
}

QPushButton[class="refresh-btn"]:disabled {
    background-color: #a0aec0;
}

/* Save Button */
QPushButton[class="save-btn"] {
    background-color: #48bb78;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 15px;
}

QPushButton[class="save-btn"]:hover {
    background-color: #38a169;
}

QPushButton[class="save-btn"]:pressed {
    background-color: #2f855a;
}

QPushButton[class="save-btn"]:disabled {
    background-color: #a0aec0;
}

/* Entry field */
QLineEdit {
    padding: 8px 12px;
    border: 2px solid #e2e8f0;
    border-radius: 6px;
    font-size: 14px;
    background-color: white;
}

QLineEdit:focus {
    border-color: #4299e1;
    outline: none;
}

/* Charts */
QFrame[class="chart"] {
    background-color: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 15px;
}

QFrame[class="chart"]:hover {
    border-color: #cbd5e0;
}
"""
