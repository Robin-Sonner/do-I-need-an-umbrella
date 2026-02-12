"""Entry point for the weather application."""

import os
import sys
import traceback
import warnings

import resources  # noqa: F401 (Import used for the app's icon. flake can't recognize that)
from gui import MainWindow
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication


def exception_hook(exc_type, exc_value, exc_traceback):
    """Global exception hook to log crashes to a file."""
    log_path = os.path.join(os.path.dirname(__file__), "crash_log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    # Call the default handler afterwards
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    """Initialize and run the weather application."""
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setApplicationName("Do I need an umbrella?")

    app.setWindowIcon(QIcon(":/umbrella.ico"))

    # Create and show the main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    # Secondary View boxes (used in temperature/precipitation chart) can trigger Runtime Warnings when internal range validations are
    # performed with not yet initialized ranges. I'll hopefully figure out eventually where the signal is emitted, that
    # triggers ViewBoxes bad validation. Maybe something with widget.getViewBox().sigResized.connect(update_views)
    # Ignoring the warnings does not have any benefit on app functionality, I ignore them because they annoy me
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", category=RuntimeWarning, message="overflow encountered in cast"
        )
        main()
