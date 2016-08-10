#!/usr/bin/env python3

from PyQt5 import QtWidgets, QtGui, QtCore
from api_parser import TwitchData
import vlc
import time

class MainApplication(QtWidgets.QApplication):
    def __init__(self, sys):
        QtWidgets.QApplication.__init__(self, sys)
        self.tv_player = TwitchPlayer()
        self.tv_player.show()
        self.tv_player.setMinimumSize(640,480)
        self.setApplicationDisplayName("Twitch Player")
        self.setApplicationName("Twitch Player")
        self.tv_player.setWindowTitle("Twitch Player")
        self.icon = QtGui.QIcon("resource/twitch.png")
        self.tv_player.setWindowIcon(self.icon)
        self.setWindowIcon(self.icon)
        self.tray = QtWidgets.QSystemTrayIcon()
        self.menu = QtWidgets.QMenu()
        self.menu.addAction("Show window",self.tv_player.show)
        self.menu.addAction("Exit", QtWidgets.QApplication.exit)
        self.tray.setIcon(self.icon)
        self.tray.setContextMenu(self.menu)
        self.tray.show()


class TwitchPlayer(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        # vlc init
        self.vlc = vlc.Instance()
        
        self.mediaplayer = self.vlc.media_player_new()

        self.tv_player = QtWidgets.QFrame() 
        self.tv_player_constructor = self.tv_player.palette()
        self.tv_player_constructor.setColor(QtGui.QPalette.Window,QtGui.QColor(0,0,0))
        self.tv_player.setPalette(self.tv_player_constructor)
        self.tv_player.setAutoFillBackground(True)

        self.mediaplayer.set_xwindow(self.tv_player.winId())
        
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

        self.gbox = QtWidgets.QGridLayout()
        self.header_box = QtWidgets.QHBoxLayout()
        self.header_box.addWidget(self.tv_streamername)
        self.header_box.addWidget(self.tv_open_button)
        self.header_box.addWidget(self.tv_online_check)
        self.bottom_box = QtWidgets.QHBoxLayout()
        self.bottom_box.addWidget(self.tv_full_screen_button)
        self.bottom_box.addWidget(self.tv_play_button)
        self.bottom_box.addWidget(self.tv_resolution)
        self.bottom_box.addWidget(self.tv_volumeslider)

        self.gbox.addLayout(self.header_box, 1, 0)
        self.gbox.addWidget(self.tv_player,2,0)
        self.gbox.addLayout(self.bottom_box, 3, 0)


        self.setLayout(self.gbox)
        
        self.tv_play_button.setDisabled(True)
        self.tv_resolution.setDisabled(True)

        self.tv_play_button.clicked.connect(self.tv_play_button_clicked)
        self.tv_open_button.clicked.connect(self.tv_open_button_clicked)
        self.tv_full_screen_button.clicked.connect(self.full_screen)

    def setVolume(self):
        self.mediaplayer.audio_set_volume(self.tv_volumeslider.value())

    def full_screen(self):
        if self.isFullScreen():
            self.showNormal()
            self.gbox.setContentsMargins(10, 10, 10, 10)
            self.tv_streamername.show()
            self.tv_play_button.show()
            self.tv_streamername.show()
            self.tv_volumeslider.show()
            self.tv_resolution.show()
            self.tv_full_screen_button.show()
            self.tv_open_button.show()
            self.tv_online_check.show()
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
        self.full_screen()
    def tv_open_button_clicked(self):	
        self.tv_resolution.setDisabled(False)
        self.channel = self.tv_streamername.text()
        self.playlist = TwitchData(self.channel)
        if len(self.playlist.m3u8.playlists) == 0 and self.tv_online_check.isChecked():
            self.onlinecheck()
        for source in self.playlist.m3u8.playlists:
            self.tv_volumeslider.setValue(50)
            data = source.stream_info
            self.tv_resolution.addItem(str(data.resolution[1]), source.uri)
            self.tv_play_button.setDisabled(False)
   

    def tv_play_button_clicked(self):
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
        self.playlist = TwitchData(self.channel)
        while len(self.playlist.m3u8.playlists) == 0 and self.tv_online_check.isChecked():
            self.playlist = TwitchData(self.channel)
            time.sleep(60)
            print("here")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.mediaplayer.stop()
if __name__ == "__main__":
    import sys
    app = MainApplication(sys.argv)
    
    sys.exit(app.exec_())
    
