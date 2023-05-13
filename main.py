from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
import sys


def input_positions():
    window.close()
    print("Button 1 clicked")


def output_positions():
    print("Button 2 clicked")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.FramelessWindowHint)
        # Load the user interface from the .ui file
        loadUi('UI-UX/ui files/home_page.ui', self)
        # Connect any signals and slots as needed
        self.newStyle.clicked.connect(input_positions)
        self.oldStyle.clicked.connect(output_positions)
        self.quit.clicked.connect(self.close)


class InputWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('UI-UX/ui files/input_positions.ui', self)


class OutputWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('UI-UX/ui files/output_positions.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
