from PyQt5.QtMultimediaWidgets import QVideoWidget

class ClickableVideoWidget(QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = parent #reference to main window
    
    def mousePressEvent(self, event):
        if self.window:
            self.window.play_media()
        
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if self.window:
            self.window.toggle_fullscreen()
            self.window.play_media()
        
        event.accept()