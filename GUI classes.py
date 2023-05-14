from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
import sys
import cv2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.FramelessWindowHint)
        loadUi('UI-UX/ui files/home_page.ui', self)

        self.input_window = None
        self.output_window = None
        self.newStyle.clicked.connect(self.input_positions)
        self.oldStyle.clicked.connect(self.output_positions)
        self.quit.clicked.connect(self.close)

    def input_positions(self):
        self.input_window = InputWindow()
        self.input_window.show()

    def output_positions(self):
        self.output_window = OutputWindow()
        self.output_window.show()


class InputWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('UI-UX/ui files/input_positions.ui', self)

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.cap.isOpened():
            print("Unable to open webcam")
            exit()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(img))

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()


class OutputWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('UI-UX/ui files/output_positions.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
