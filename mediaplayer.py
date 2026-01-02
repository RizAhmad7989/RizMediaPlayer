from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
import sys
import os
print(os.getcwd())

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
        
        playicon_path = os.path.join(os.path.dirname(__file__), "assets", "ico", "play.ico")
        pauseicon_path = os.path.join(os.path.dirname(__file__), "assets", "ico", "pause.ico")
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        #self.playBtn.setIcon(QIcon(playicon_path))
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_media)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,0)

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
            self.playBtn.setIcon(self.style().standardIcon(QIcon.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(QIcon.SP_MediaPlay))
    
    def position_changed(self, position):
        self.slider.setValue(position)
    
    def duration_changed(self, duration):
        self.slider.stRange(0, duration)
        

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())

