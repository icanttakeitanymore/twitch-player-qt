from PyQt5 import QtWidgets, QtGui, QtCore
from twitch_api import TwitchData
from twitch_thread import TwitchThread
import vlc


class TwitchPlayer(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        # vlc init
        self.vlc = vlc.Instance()
        # media player object
        self.mediaplayer = self.vlc.media_player_new()
        # bugged
        # self.event_manager = self.mediaplayer.event_manager()
        # self.event_manager.event_attach(vlc.EventType.MediaPlayerEncounteredError, self.http_error,1)
        # frame for video player
        self.tv_player = QtWidgets.QFrame() 
        self.tv_player_constructor = self.tv_player.palette()
        self.tv_player_constructor.setColor(QtGui.QPalette.Window,QtGui.QColor(0, 0, 0))
        self.tv_player.setPalette(self.tv_player_constructor)
        self.tv_player.setAutoFillBackground(True)
        # self.tv_player.underMouse()
        # setting window for video player
        self.mediaplayer.set_xwindow(self.tv_player.winId())
        # helper window
        self.helperwindow = self.closewindow = QtWidgets.QDialog(self, QtCore.Qt.Window)
        self.helperwindow.setWindowModality(QtCore.Qt.WindowModal)
        self.helperwindow.message = QtWidgets.QLabel()
        self.helperwindow.message.setAlignment(QtCore.Qt.AlignHCenter)
        self.helperwindow.ok_button = QtWidgets.QPushButton("ok")
        self.helperwindow.box = QtWidgets.QVBoxLayout()
        self.helperwindow.box.addWidget(self.helperwindow.message)
        self.helperwindow.box.addWidget(self.helperwindow.ok_button)
        self.helperwindow.setLayout(self.helperwindow.box)
        self.helperwindow.setFixedSize(200,100)
        self.helperwindow.ok_button.clicked.connect(self.hide_helper_window)
        # GUI
        self.tv_streamername = QtWidgets.QLineEdit()
        self.tv_resolution = QtWidgets.QComboBox()
        self.tv_open_button = QtWidgets.QPushButton('Open')
        self.tv_online_check = QtWidgets.QCheckBox("online check")
        self.tv_play_button = QtWidgets.QPushButton("Play")
        self.tv_full_screen_button = QtWidgets.QPushButton("Full Screen")
        self.tv_volumeslider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.tv_volumeslider.setMaximum(100)
        self.tv_volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.tv_volumeslider.setToolTip("Volume")
        self.tv_volumeslider.valueChanged.connect(self.setVolume)

        self.tv_play_button.setFixedSize(60,30)
        self.tv_streamername.setFixedSize(200,30)
        self.tv_volumeslider.setFixedSize(100,30)
        self.tv_resolution.setFixedSize(100,30)
        self.tv_full_screen_button.setFixedSize(70,30)
        self.tv_open_button.setFixedSize(60,30)
        self.tv_online_check.setFixedSize(95,30)

        # Boxes
        self.gbox = QtWidgets.QGridLayout()
        self.top_box_L = QtWidgets.QHBoxLayout()
        self.top_box_L.addWidget(self.tv_streamername)
        self.top_box_L.addWidget(self.tv_open_button)

        self.top_box_R = QtWidgets.QHBoxLayout()
        self.top_box_R.addWidget(self.tv_online_check, alignment=QtCore.Qt.AlignRight)

        self.bottom_box_L = QtWidgets.QHBoxLayout()
        self.bottom_box_L.addWidget(self.tv_play_button)
        self.bottom_box_L.addWidget(self.tv_resolution)

        self.bottom_box_R = QtWidgets.QHBoxLayout()
        self.bottom_box_R.setAlignment(QtCore.Qt.AlignRight)
        self.bottom_box_R.addWidget(self.tv_volumeslider)
        self.bottom_box_R.addWidget(self.tv_full_screen_button, alignment=QtCore.Qt.AlignHCenter)
        # Main Box
        self.gbox.addLayout(self.top_box_L, 0, 0, QtCore.Qt.AlignLeft)
        self.gbox.addLayout(self.top_box_R, 0,1, QtCore.Qt.AlignRight)
        self.gbox.addWidget(self.tv_player, 2, 0)
        self.gbox.addLayout(self.bottom_box_L, 3, 0, QtCore.Qt.AlignLeft)
        self.gbox.addLayout(self.bottom_box_R, 3, 1, QtCore.Qt.AlignRight)

        # Setting Layout
        self.setLayout(self.gbox)

        self.tv_play_button.setDisabled(True)
        self.tv_resolution.setDisabled(True)

        # Signals
        self.tv_play_button.clicked.connect(self.tv_play_button_clicked)
        self.tv_open_button.clicked.connect(self.tv_open_button_clicked)
        self.tv_full_screen_button.clicked.connect(self.full_screen)
        self.channel_upped = 0


    def setVolume(self):
        """setting volume from self.tv_volumeslider"""
        self.mediaplayer.audio_set_volume(self.tv_volumeslider.value())

    def full_screen(self):
        """full screen from self.tv_full_screen_button signal"""
        if self.isFullScreen():
            self.showNormal()
            self.gbox.setContentsMargins(10, 10, 10, 10)
            self.tv_play_button.show()
            self.tv_streamername.show()
            self.tv_volumeslider.show()
            self.tv_resolution.show()
            self.tv_full_screen_button.show()
            self.tv_open_button.show()
            self.tv_online_check.show()
            self.tv_player.underMouse()
        else:
            self.tv_streamername.hide()
            self.tv_play_button.hide()
            self.tv_streamername.hide()
            self.tv_volumeslider.hide()
            self.tv_resolution.hide()
            self.tv_full_screen_button.hide()
            self.tv_open_button.hide()
            self.tv_online_check.hide()
            self.gbox.setContentsMargins(0,0,0,0)
            self.showFullScreen()

    def mouseDoubleClickEvent(self, event):
        """Double click for full_screen()"""
        self.full_screen()

    def tv_open_button_clicked(self):	
        """getting twitch playlist"""
        if self.mediaplayer.is_playing():
            self.mediaplayer.stop()
        self.tv_resolution.setDisabled(False)
        self.channel = self.tv_streamername.text()
        try:
            self.playlist = TwitchData(self.channel)
        except KeyError:
            self.helperwindow.message.setText("channel non found")
            self.helperwindow.show()

            return 0
        if len(self.playlist.m3u8.playlists) == 0:
            self.helperwindow.message.setText("channel offline")
            self.helperwindow.show()
        if len(self.playlist.m3u8.playlists) == 0 and self.tv_online_check.isChecked():
            self.onlinecheck()
        for source in self.playlist.m3u8.playlists:
            self.tv_volumeslider.setValue(50)
            data = source.stream_info
            self.tv_resolution.addItem(str(data.resolution[1]), source.uri)
            self.tv_play_button.setDisabled(False)

    def tv_play_button_clicked(self):
        """playing video"""
        if self.mediaplayer.is_playing():
            self.tv_play_button.setText("Play")
            self.mediaplayer.stop()
            self.tv_resolution.setDisabled(False)
        else:
            self.tv_resolution.setDisabled(True)
            self.tv_play_button.setText("Stop")
            self.mediaplayer.set_mrl(self.tv_resolution.currentData())
            self.mediaplayer.play()
    
    def onlinecheck(self):
        # thread
        self.tv_thread = TwitchThread(self.channel)
        self.tv_thread.channel_is_up.connect(self.channel_is_up, QtCore.Qt.QueuedConnection)
        self.tv_thread.start()

    def channel_is_up(self, signal):
        self.channel_upped = signal
        if self.channel_upped:
            self.helperwindow.message.setText("upped")
            self.helperwindow.show()
            self.tv_open_button_clicked()
    def closeEvent(self, event):
        self.closewindow = QtWidgets.QDialog(self, QtCore.Qt.Window)
        self.closewindow.setWindowModality(QtCore.Qt.WindowModal)
        self.closewindow.button1 = QtWidgets.QPushButton('Quit')
        self.closewindow.button2 = QtWidgets.QPushButton('Hide')
        self.closewindow.hbox = QtWidgets.QHBoxLayout()
        self.closewindow.hbox.addWidget(self.closewindow.button1)
        self.closewindow.hbox.addWidget(self.closewindow.button2)
        self.closewindow.setLayout(self.closewindow.hbox)
        self.closewindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.closewindow.button1.clicked.connect(QtWidgets.qApp.quit)
        self.closewindow.button2.clicked.connect(self.hide_to_tray)
        self.closewindow.setWindowTitle('Exit Twitch Player')
        self.closewindow.setFixedSize(200, 100)
        self.closewindow.show()
        self.mediaplayer.stop()
        event.ignore()

    def hide_to_tray(self):
        self.hide()
        self.closewindow.hide()

    def hide_helper_window(self):
        self.helperwindow.hide()

    def resizeEvent(self, resizeEvent):
        if (not self.isFullScreen()):
            self.tv_player.setFixedWidth(self.width()-25)

        else:
            self.tv_player.setFixedWidth(self.width())

    # @vlc.callbackmethod
    # def http_error(self,data):
    #    print("here")
    #    return 0
