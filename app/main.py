import sys

from gui import MainWindow
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication


def main():
    """Initialize and run the weather application."""
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setApplicationName("Do I need an umbrella?")

    # Create and show the main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
