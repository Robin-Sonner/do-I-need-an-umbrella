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
