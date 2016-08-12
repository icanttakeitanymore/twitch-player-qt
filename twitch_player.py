#!/usr/bin/env python3
from PyQt5 import QtWidgets, QtGui, QtCore
from twitch_api import TwitchData
from twitch_thread import TwitchThread
import sys
import vlc
class MainApplication(QtWidgets.QApplication):

    def __init__(self, sys):
        QtWidgets.QApplication.__init__(self, sys)
        self.icon = QtGui.QIcon("resource/twitch.png")
        self.icon_online = QtGui.QIcon("resource/twitch_online.png")
        self.tv_player = TwitchPlayer()
        self.tv_player.show()
        self.tv_player.tv_player.setFocus(3)
        self.tv_player.setMinimumSize(640,480)
        self.setApplicationDisplayName("Twitch Player")
        self.setApplicationName("Twitch Player")
        self.tv_player.setWindowIcon(self.icon)
        self.setWindowIcon(self.icon)
        self.tray = QtWidgets.QSystemTrayIcon()
        self.menu = QtWidgets.QMenu()
        self.menu.addAction("Show window", self.tv_player_show)
        self.menu.addAction("Exit", QtWidgets.QApplication.exit)
        self.tray.setIcon(self.icon)
        self.tray.setContextMenu(self.menu)
        self.tray.show()
        self.moveToCenter()

    def tv_player_show(self):
        self.tv_player.show()
        self.tray.setIcon(self.icon)
    def moveToCenter(self):
        self.screen = self.desktop()
        self.tv_player.move((self.screen.width() - self.tv_player.frameSize().width()) / 2,
                            (self.screen.height() - self.tv_player.frameSize().height()) / 2)




class TwitchPlayer(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle("Twitch Player")
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
        self.helperwindow  = QtWidgets.QDialog(self, QtCore.Qt.Window)
        self.helperwindow.setWindowModality(QtCore.Qt.WindowModal)
        self.helperwindow.message = QtWidgets.QLabel()
        self.helperwindow.message.setAlignment(QtCore.Qt.AlignHCenter)
        self.helperwindow.ok_button = QtWidgets.QPushButton("ok")
        self.helperwindow.box = QtWidgets.QVBoxLayout()
        self.helperwindow.box.addWidget(self.helperwindow.message)
        self.helperwindow.box.addWidget(self.helperwindow.ok_button)
        self.helperwindow.setLayout(self.helperwindow.box)
        self.helperwindow.setFixedSize(300,100)
        self.helperwindow.ok_button.clicked.connect(self.hide_helper_window)
        # GUI
        #
        self.tv_streamername = QtWidgets.QLineEdit()
        self.tv_streamername.setPlaceholderText("channel name")
        self.tv_channels_button = QtWidgets.QPushButton("Channels")
        self.tv_add_channel = QtWidgets.QPushButton("Add to list")
        self.tv_del_channel = QtWidgets.QPushButton("Delete from list")

        self.online_icon = QtGui.QIcon("resource/streamer_online.png")
        self.offine_icon = QtGui.QIcon("resource/streamer_offline.png")
        self.tv_channels_frame = QtWidgets.QFrame()
        self.tv_channels_box = QtWidgets.QToolBox()
        self.tv_channels_grid = QtWidgets.QGridLayout()
        self.tv_channels_list = QtWidgets.QListView()
        self.tv_channels_refresh_button = QtWidgets.QPushButton("Refresh")
        self.tv_channels_grid.addWidget(self.tv_channels_list,1,1,3,3)
        self.tv_channels_grid.addWidget(self.tv_channels_refresh_button, 3,0)
        self.tv_channels_grid.addWidget(self.tv_add_channel,1,0)
        self.tv_channels_grid.addWidget(self.tv_del_channel,2,0)
        self.tv_channels_frame.setLayout(self.tv_channels_grid)
        self.tv_channels_frame.setFixedHeight(100)
        self.tv_channels_frame.hide()
        #
        self.tv_completer = QtWidgets.QCompleter(self.get_channels())
        self.tv_streamername.setCompleter(self.tv_completer)
        self.tv_streamername.clearFocus()
        self.tv_streamername.setAlignment(QtCore.Qt.AlignHCenter)
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

        self.tv_channels_button.setFixedSize(90,25)
        self.tv_play_button.setFixedSize(90,25)
        self.tv_streamername.setFixedSize(200, 25)
        self.tv_volumeslider.setFixedSize(100, 25)
        self.tv_resolution.setFixedSize(100, 25)
        self.tv_full_screen_button.setFixedSize(90, 25)
        self.tv_open_button.setFixedSize(90, 25)
        self.tv_online_check.setFixedSize(110, 25)
        self.tv_add_channel.setFixedSize(140, 25)
        self.tv_del_channel.setFixedSize(140, 25)

        # Boxes
        self.gbox = QtWidgets.QGridLayout()
        self.top_box_L = QtWidgets.QHBoxLayout()
        self.top_box_L.addWidget(self.tv_streamername)
        self.top_box_L.addWidget(self.tv_open_button)
        self.top_box_L.addWidget(self.tv_channels_button)

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
        self.gbox.addWidget(self.tv_channels_frame,2,0)
        self.gbox.addWidget(self.tv_player, 3, 0)
        self.gbox.addLayout(self.bottom_box_L, 4, 0, QtCore.Qt.AlignLeft)
        self.gbox.addLayout(self.bottom_box_R, 4, 1, QtCore.Qt.AlignRight)

        # Setting Layout
        self.setLayout(self.gbox)

        self.tv_play_button.setDisabled(True)
        self.tv_resolution.setDisabled(True)

        # Signals
        self.tv_play_button.clicked.connect(self.tv_play_button_clicked)
        self.tv_open_button.clicked.connect(self.tv_open_button_clicked)
        self.tv_full_screen_button.clicked.connect(self.full_screen)
        self.tv_add_channel.clicked.connect(self.save_channel)
        self.tv_del_channel.clicked.connect(self.del_channel)
        self.tv_channels_button.clicked.connect(self.show_channels_frame)
        self.channel_upped = 0


    def setVolume(self):
        """setting volume from self.tv_volumeslider"""
        self.mediaplayer.audio_set_volume(self.tv_volumeslider.value())

    def full_screen(self):
        """full screen from self.tv_full_screen_button signal"""
        if self.isFullScreen():
            self.showNormal()
            self.gbox.setContentsMargins(10, 10, 10, 10)
            self.tv_channels_button.show()
            self.tv_play_button.show()
            self.tv_add_channel.show()
            self.tv_del_channel.show()
            self.tv_streamername.show()
            self.tv_volumeslider.show()
            self.tv_resolution.show()
            self.tv_full_screen_button.show()
            self.tv_open_button.show()
            self.tv_online_check.show()
            self.tv_player.underMouse()
            self.tv_channels_frame.hide()
        else:
            self.tv_channels_frame.hide()
            self.tv_channels_button.hide()
            self.tv_add_channel.hide()
            self.tv_del_channel.hide()
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
        if len(self.playlist.m3u8.playlists) == 0 and not self.tv_online_check.isChecked():
            self.helperwindow.message.setText("channel offline")
            self.helperwindow.show()
            return 0
        elif len(self.playlist.m3u8.playlists) == 0 and not self.isHidden():
            self.helperwindow.message.setText("channel offline, online checking is enabled")
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
            self.setWindowTitle("Playing {0}".format(self.tv_streamername.text()))
            self.mediaplayer.play()
    
    def onlinecheck(self):
        # thread
        self.tv_thread = TwitchThread(self.channel)
        self.tv_thread.channel_is_up.connect(self.channel_is_up, QtCore.Qt.QueuedConnection)
        self.tv_thread.start()

    def channel_is_up(self, signal):
        self.channel_upped = signal
        if self.channel_upped:
            # Message
            if app.tv_player.isHidden():
                app.tray.showMessage("Twitch Player",
                                     "{0} is streaming!".format(self.tv_streamername.text()),
                                     msecs=10000)
                app.tray.setIcon(app.icon_online)
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
            self.tv_channels_frame.setFixedWidth(self.width()-25)

        else:
            self.tv_player.setFixedWidth(self.width())

    def save_channel(self):
        from os.path import expanduser
        from os import mkdir
        from os.path import isdir
        import sqlite3
        home_path = expanduser("~")
        if not isdir("{0}/.cache/twitch".format(home_path)):
            mkdir("{0}/.cache/twitch".format(home_path),0o750)
        con = sqlite3.connect(r'file:///{0}/twitch.db?mode=rwc'.format(home_path + "/.cache/twitch"), uri=True)
        cursor = con.cursor()
        createtable = '''CREATE TABLE IF NOT EXISTS channame (name TEXT UNIQUE ON CONFLICT IGNORE);'''
        add_channel = '''INSERT INTO channame (name) VALUES ('{0}');'''.format(self.tv_streamername.text())
        cursor.execute(createtable)
        cursor.execute(add_channel)
        con.commit()
        self.tv_completer = QtWidgets.QCompleter(self.get_channels())
        self.tv_streamername.setCompleter(self.tv_completer)

    def del_channel(self):
        from os.path import expanduser
        from os.path import isfile
        import sqlite3
        home_path = expanduser("~")
        if isfile("{0}/.cache/twitch/twitch.db".format(home_path)):
            con = sqlite3.connect(r'file:///{0}/twitch.db?mode=rw'.format(home_path + "/.cache/twitch"), uri=True)
            cursor = con.cursor()
            del_channel = """DELETE FROM channame WHERE name=\"{0}\";""".format(self.tv_streamername.text())
            cursor.execute(del_channel)
            con.commit()
        self.tv_completer = QtWidgets.QCompleter(self.get_channels())
        self.tv_streamername.setCompleter(self.tv_completer)

    def get_channels(self):
        from os.path import expanduser
        from os import mkdir
        from os.path import isdir
        import sqlite3
        home_path = expanduser("~")
        if not isdir("{0}/.cache/twitch".format(home_path)):
            mkdir("{0}/.cache/twitch".format(home_path), 0o750)
            con = sqlite3.connect(r'file:///{0}/twitch.db?mode=rwc'.format(home_path + "/.cache/twitch"), uri=True)
            cursor = con.cursor()
            createtable = """CREATE TABLE IF NOT EXISTS channame (name TEXT UNIQUE ON CONFLICT IGNORE);"""
            cursor.execute(createtable)
            con.commit()
        con = sqlite3.connect(r'file:///{0}/twitch.db?mode=rwc'.format(home_path + "/.cache/twitch"), uri=True)
        cursor = con.cursor()
        getchannel = """SELECT * FROM channame"""
        cursor.execute(getchannel)
        # data
        connection_data = cursor.fetchall()
        data = []
        for i in connection_data:
            data.append(i[0])
        return data

    # @vlc.callbackmethod
    # def http_error(self,data):
    #    print("here")
    #    return 0
    def show_channels_frame(self):
        if self.tv_channels_frame.isHidden():
            self.tv_channels_button.setDisabled(True)
            self.channels_refresh_frame()
            self.tv_channels_button.setDisabled(False)
        else:
            self.tv_channels_frame.hide()

    def channels_refresh_frame(self):
        self.tv_channels_frame.show()
        data = self.get_channels()
        standardmodel = QtGui.QStandardItemModel()
        for i in range(len(data)):
            print(i)
            online = TwitchData(data[i])
            if online.m3u8.playlists:
                iconfile = self.online_icon
            else:
                iconfile = self.offine_icon
            item = QtGui.QStandardItem(iconfile, data[i])
            standardmodel.appendRow(item)
            self.tv_channels_list.setModel(standardmodel)

if __name__ == "__main__":
    app = MainApplication(sys.argv)
    sys.exit(app.exec_())