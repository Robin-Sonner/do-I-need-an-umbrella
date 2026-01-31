from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yeah")


app = QApplication([])
window = MainView()
window.show()
app.exec()
