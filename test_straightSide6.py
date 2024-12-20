import sys
import signal

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Press Me!")

        self.setFixedSize(QSize(480, 320))

        # Set the central widget of the Window.
        self.setCentralWidget(button)

# handle ctrl+c
signal.signal(signal.SIGINT, signal.SIG_DFL)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()