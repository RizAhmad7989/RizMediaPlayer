from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QLinearGradient
import random

class Visualiser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.num_bars = 32
        self.bar_values = [0] * self.num_bars #list of heights, 0 to 1 for each bar

        #60fps timer

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_bars)
        self.timer.start(16)

        self.setMinimumHeight(150)
    
    #each bar goes up/down, values are clamped between 0 and 1
    def update_bars(self):
        #placeholder random values, feed audio later
        self.bar_values = [
            max(0, min(1, v + random.uniform(-0.15, 0.15)))
            for v in self.bar_values
        ]
        self.update() 

    #called whenever needs to redraw
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) #makes edges smooth

        width = self.width()
        height = self.height()

        bar_width = width/self.num_bars

        for i, value in enumerate(self.bar_values):
            bar_height = value * height

            x = i * bar_width
            y = height - bar_height

            #glowing gradient
            gradient = QLinearGradient(x, y, x, height)
            gradient.setColorAt(0.0, QColor(0, 200, 255, 220))
            gradient.setColorAt(1.0, QColor(0, 80, 160, 80))

            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(
                int(x + 2), 
                int(y), 
                int(bar_width - 4), 
                int(bar_height), 
                4, 
                4)
