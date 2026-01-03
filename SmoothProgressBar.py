from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRectF


class SmoothProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0  # 0.0 to 1.0
        self.dragging = False
        self.seek_callback = None
        self.setMinimumHeight(30)
        self.drag_start_callback = None
        self.drag_end_callback = None
        

    def setProgress(self, value):
        if not self.dragging:  #don't override while dragging
            self.progress = max(0.0, min(1.0, value))
            self.update()

    def setSeekCallback(self, callback):
        self.seek_callback = callback

    def setDragStartCallback(self, callback):
        self.drag_start_callback = callback

    def setDragEndCallback(self, callback):
        self.drag_end_callback = callback

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bar_y = self.height() / 2 - 3

        # Background bar
        bg_rect = QRectF(0, bar_y, self.width() - 1, 6)
        painter.setBrush(QColor(70, 70, 70))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bg_rect, 3, 3)

        # Progress bar
        fg_rect = QRectF(0, bar_y, self.width() * self.progress - 1, 6)
        painter.setBrush(QColor(191, 64, 191))
        painter.drawRoundedRect(fg_rect, 3, 3)

        # Draggable circle
        circle_x = self.width() * self.progress
        circle_radius = 10

        circle_y = (self.height() - circle_radius * 2) / 2

        # Clamp so the circle stays fully inside the bar
        circle_x = max(circle_radius, min(self.width() - circle_radius - 1, circle_x))

        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QPen(Qt.black, 1))

        rect = QRectF(
            circle_x - circle_radius, 
            circle_y,
            circle_radius * 2,
            circle_radius * 2
        )

        painter.drawEllipse(rect)

    def mousePressEvent(self, event):
        self.dragging = True
        if self.drag_start_callback:
            self.drag_start_callback()
        self._update_drag(event.x())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self._update_drag(event.x())

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self._update_drag(event.x())
        if self.drag_end_callback:
            self.drag_end_callback()


    def _update_drag(self, x, final=False):
        width = self.width()
        ratio = max(0.0, min(1.0, x / width))
        self.progress = ratio
        self.update()

        if self.seek_callback:
            self.seek_callback(ratio)