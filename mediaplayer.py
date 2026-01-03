from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QSize, QRectF, QTimer, QPropertyAnimation, QEasingCurve
import sys
import os

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QRectF, Qt


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

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.last_seek_time = 0
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "ico", "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setFocusPolicy(Qt.StrongFocus) #window receives keyboard focus

        self.setWindowTitle("Riz Media Player")
        self.setGeometry(350, 100, 1200, 800)

        self.create_player()
    
    def create_player(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videowidget = QVideoWidget()
        #want a play button, stop button, skip 5sec, go back 5sec, open file

        self.openBtn = QPushButton('Open file')
        self.openBtn.clicked.connect(self.open_file)
        self.openBtn.setFixedSize(96, 32)
        
        
        # Build absolute paths with forward slashes (Qt requires this)
        base = os.path.dirname(__file__).replace("\\", "/")

        self.play_normal = f"{base}/assets/png/playbtn.png"
        self.play_hover = f"{base}/assets/png/playbtn_hover.png"
        self.play_pressed = f"{base}/assets/png/playbtn_pressed.png"

        self.pause_normal = f"{base}/assets/png/pausebtn.png"
        self.pause_hover = f"{base}/assets/png/pausebtn_hover.png"
        self.pause_pressed = f"{base}/assets/png/pausebtn_pressed.png"

        self.play_stylesheet = f"""QPushButton {{
            border: none;
            background: transparent;
            qproperty-icon: url({self.play_normal});
        }}
        QPushButton:hover {{
            qproperty-icon: url({self.play_hover});
        }}
        QPushButton:pressed {{
            qproperty-icon: url({self.play_pressed});
        }}
        """

        self.pause_stylesheet = f"""QPushButton {{
            border: none;
            background: transparent;
            qproperty-icon: url({self.pause_normal});
        }}
        QPushButton:hover {{
            qproperty-icon: url({self.pause_hover});
        }}
        QPushButton:pressed {{
            qproperty-icon: url({self.pause_pressed});
        }}
        """

        self.playBtn = QPushButton()
        self.playBtn.setFixedSize(32, 32)
        self.playBtn.setIconSize(QSize(32, 32))
        self.playBtn.setEnabled(False)
        self.playBtn.setStyleSheet(self.play_stylesheet)        
        self.playBtn.clicked.connect(self.play_media)
        
        self.slider = SmoothProgressBar()
        self.slider.setSeekCallback(self.seek_to_ratio)
        self.smoothTimer = QTimer()
        self.smoothTimer.timeout.connect(self.update_smooth_progress)
        self.smoothTimer.start(16)  # ~60 FPS
        self.slider.setDragStartCallback(self.on_drag_start)
        self.slider.setDragEndCallback(self.on_drag_end)


        hbox = QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)

        hbox.addWidget(self.openBtn)
        hbox.addWidget(self.playBtn)
        

        vbox = QVBoxLayout()
        vbox.addWidget(videowidget, stretch=1)
        vbox.addWidget(self.slider)
        vbox.addLayout(hbox, stretch=0)  
        #vbox.addSpacing()
        self.mediaPlayer.setVideoOutput(videowidget)

        self.setLayout(vbox)

        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)

    
    def open_file(self):
        was_playing = self.mediaPlayer.state() == QMediaPlayer.PlayingState
        self.mediaPlayer.pause()
        filename, _ = QFileDialog.getOpenFileName(self, "Open Media")

        if filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playBtn.setEnabled(True)
            self.mediaPlayer.play()

        if was_playing:
            self.mediaPlayer.play()
    
    def play_media(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setStyleSheet(self.pause_stylesheet)
        else:
            self.playBtn.setStyleSheet(self.play_stylesheet)

    def update_smooth_progress(self):
        duration = self.mediaPlayer.duration()
        if duration > 0 and not self.slider.dragging: #when user not moving slider
            ratio = self.mediaPlayer.position() / duration
            self.slider.setProgress(ratio)
    
    def seek_to_ratio(self, ratio):
        import time
        now = time.time()

        # Limit seeks to ~30 FPS
        if now - self.last_seek_time < 1/30:
            return

        self.last_seek_time = now

        duration = self.mediaPlayer.duration()
        if duration > 0:
            new_pos = int(duration * ratio)
            self.mediaPlayer.setPosition(new_pos)
    
    def on_drag_start(self):
        self.was_playing = (self.mediaPlayer.state() == QMediaPlayer.PlayingState)
        self.mediaPlayer.pause()

    def on_drag_end(self):
        if self.was_playing:
            self.mediaPlayer.play()
    
    def keyPressEvent(self, event):
        key = event.key()
        mods = event.modifiers()

        match key:
            #play/pause
            case Qt.Key_Space | Qt.Key_K:
                self.play_media()
                event.accept()
            
            #skip back/forward
            case Qt.Key_J:
                self.skip_seconds(-10)
                event.accept()
            
            case Qt.Key_L:
                self.skip_seconds(10)
                event.accept()

            case Qt.Key_Left:
                self.skip_seconds(-5)
                event.accept()
            
            case Qt.Key_Right:
                self.skip_seconds(5)
                event.accept()

            #TODO: volume controls

            #Fullscreen
            case Qt.Key_F:
                self.toggle_fullscreen()
                event.accept()
                    
            #Open File
            case Qt.Key_O if mods & Qt.ControlModifier:
                self.open_file()
                event.accept()

            #Default case
            case _:
                super().keyPressEvent(event)
    
    def skip_seconds(self, seconds):
        pos = self.mediaPlayer.position()
        new_pos = max(0, pos + seconds * 1000)
        self.mediaPlayer.setPosition(new_pos)
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.fade_window(1.0, 0.0, 180, finished_callback=self.exit_fullscreen)
        else:
            self.fade_window(1.0, 0.0, 180, finished_callback=self.enter_fullscreen)
    
    def enter_fullscreen(self):
        self.showFullScreen()
        self.fade_window(0.0, 1.0, 180)
    
    def exit_fullscreen(self):
        self.showNormal()
        self.fade_window(0.0, 1.0, 180)
    
    def fade_window(self, start, end, duration=250, finished_callback=None):
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        if finished_callback:
            self.anim.finished.connect(finished_callback)
        
        self.anim.start()


       

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())

