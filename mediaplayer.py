from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QSize, QRectF, QTimer
import sys
import os
print(os.getcwd())

class SmoothProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0  # 0.0 to 1.0
        self.setMinimumHeight(10)

    def setProgress(self, value):
        self.progress = max(0.0, min(1.0, value))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background bar
        bg_rect = QRectF(0, self.height()/2 - 3, self.width(), 6)
        painter.setBrush(QColor(80, 80, 80))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bg_rect, 3, 3)

        # Progress bar
        fg_rect = QRectF(0, self.height()/2 - 3, self.width() * self.progress, 6)
        painter.setBrush(QColor(0, 180, 255))
        painter.drawRoundedRect(fg_rect, 3, 3)

class Window(QWidget):
    def __init__(self):
        super().__init__()

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "ico", "icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("Riz Media Player")
        self.setGeometry(350, 100, 1200, 800)

        self.create_player()
    
    def create_player(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videowidget = QVideoWidget()
        #want a play button, stop button, skip 5sec, go back 5sec, open file

        self.openBtn = QPushButton('Open file')
        self.openBtn.clicked.connect(self.open_file)
        
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

        #self.slider = QSlider(Qt.Horizontal)
        self.slider = SmoothProgressBar()
        self.smoothTimer = QTimer()
        self.smoothTimer.timeout.connect(self.update_smooth_progress)
        self.smoothTimer.start(16)  # ~60 FPS
        #self.slider.setRange(0,0)
        #self.slider.sliderMoved.connect(self.set_position)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)

        hbox.addWidget(self.openBtn)
        hbox.addWidget(self.playBtn)
        hbox.addWidget(self.slider)

        vbox = QVBoxLayout()
        vbox.addWidget(videowidget)
        vbox.addLayout(hbox)

        self.mediaPlayer.setVideoOutput(videowidget)

        self.setLayout(vbox)

        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)

    
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Media")

        if filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playBtn.setEnabled(True)
    
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
        if self.mediaPlayer.duration() > 0:
            real_progress = self.mediaPlayer.position() / self.mediaPlayer.duration()
            self.slider.setProgress(real_progress)
    
    #def position_changed(self, position):
    #    self.slider.setValue(position)
    
    #def duration_changed(self, duration):
    #    self.slider.setRange(0, duration)

    #def set_position(self, position):
    #    self.mediaPlayer.setPosition(position)
        

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())

