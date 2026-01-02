from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon
import sys
import os
print(os.getcwd())

class Window(QWidget):
    def __init__(self):
        super().__init__()

        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("Riz Media Player")
        self.setGeometry(350, 100, 1200, 800)

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())

