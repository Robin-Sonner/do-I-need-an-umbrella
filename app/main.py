import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget


class ApplicationController:
    def __init__(self):
        pass


class ApplicationView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = ApplicationController()

        self.setWindowTitle("Do I need an umbrella?")
        self.resize(900, 700)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        navigation_bar = QWidget()
        main_layout.addWidget(navigation_bar)


def main():
    app = QApplication(sys.argv)

    # Basic initialization
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    app.setApplicationName("Do I need an umbrella?")

    # Create and show the main window
    window = ApplicationView()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
