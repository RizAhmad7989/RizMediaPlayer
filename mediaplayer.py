from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QMenuBar, QMenu, QAction
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer, QPropertyAnimation, QEasingCurve, QCoreApplication
import sys
import os
from SmoothProgressBar import SmoothProgressBar
from Visualiser import Visualiser
from ClickableVideoWidget import ClickableVideoWidget

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.last_seek_time = 0
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "ico", "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setFocusPolicy(Qt.StrongFocus) #window receives keyboard focus

        self.setWindowTitle("Riz Media Player")
        self.setGeometry(350, 100, 1200, 800)

        self.menu_bar = QMenuBar(self)

        #File Menu
        self.file_menu = QMenu("File", self)
        self.open_action = QAction("Open File", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.help_action = QAction("Help", self)
        self.help_action.setShortcut(Qt.CTRL+Qt.Key_H)
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut(QKeySequence.Close)
        self.file_menu.addActions([self.open_action, self.help_action])
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.open_action.triggered.connect(self.open_file)
        self.exit_action.triggered.connect(QCoreApplication.instance().quit)

        #View Menu
        self.view_menu = QMenu("View", self)
        self.fullscreen_action = QAction("Fullscreen", self)
        self.fullscreen_action.setShortcut(Qt.Key_F)
        self.view_menu.addActions([self.fullscreen_action])

        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
        
        self.create_player()
    
    def create_player(self):
        self.visualiser = Visualiser()
        self.visualiser.hide() #hide till audio file detected
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videowidget = ClickableVideoWidget(self)
        #want a play button, stop button, skip 5sec, go back 5sec, open file
        
        
        #absolute paths with forward slashes
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
        
        self.slider = SmoothProgressBar(self)
        self.slider.setSeekCallback(self.seek_to_ratio)
        self.smoothTimer = QTimer()
        self.smoothTimer.timeout.connect(self.update_smooth_progress)
        self.smoothTimer.start(16)  # ~60 FPS
        self.slider.setDragStartCallback(self.on_drag_start)
        self.slider.setDragEndCallback(self.on_drag_end)


        hbox = QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)

        hbox.addWidget(self.playBtn)
        

        vbox = QVBoxLayout()
        
        vbox.setMenuBar(self.menu_bar)
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.view_menu)

        vbox.addWidget(videowidget, stretch=1)
        vbox.addWidget(self.visualiser)

        self.mediaPlayer.videoAvailableChanged.connect(self.on_video_available)
        
        vbox.addWidget(self.slider)
        vbox.addLayout(hbox, stretch=0)  
        self.mediaPlayer.setVideoOutput(videowidget)

        self.setLayout(vbox)

        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)

    
    def open_file(self):
        #self.visualiser.hide()
        was_playing = self.mediaPlayer.state() == QMediaPlayer.PlayingState
        self.mediaPlayer.pause()
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Media",
            "",
            "Audio/Video Files (*.mp3 *.wav *.flac *.aac *.ogg *.m4a *.mp4 *.avi *.mov *.wmv *.webm);;"
            "Audio Files (*.mp3 *.wav *.flac *.aac *.ogg *.m4a);;"
            "Video Files (*.mp4 *.avi *.mov *.wmv *.webm)"
        )

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

        #limit seeks to around 10 FPS
        if now - self.last_seek_time < 1/10:
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
        duration = self.mediaPlayer.duration()
        if duration > 0:
            final_ratio = self.slider.getProgress()
            self.mediaPlayer.setPosition(int(duration * final_ratio))

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
        duration = self.mediaPlayer.duration()

        new_pos = max(0, min(pos + seconds * 1000, duration))
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

    def on_video_available(self, available):
        if available:
            self.visualiser.hide()
        else:
            self.visualiser.show()


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())

