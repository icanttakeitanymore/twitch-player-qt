#!/usr/bin/env python3
from PyQt5 import QtWidgets, QtGui, QtCore
from twitch_api import TwitchData
from twitch_thread import TwitchThread
import sys
import vlc

# Widgets starts with tv_widget_*
# Functions starts with tv_function_*
# Vlc objects starts with tv_vlc_*

class MainApplication(QtWidgets.QApplication):

    def __init__(self, sys):
        QtWidgets.QApplication.__init__(self, sys)
        self.app_icon = QtGui.QIcon("resource/twitch.png")
        self.app_icon_online = QtGui.QIcon("resource/twitch_online.png")
        self.app_tv_player = TwitchPlayer()
        self.app_tv_player.show()
        self.app_tv_player.tv_player.setFocus(3)
        self.app_tv_player.setMinimumSize(640,480)
        self.setApplicationDisplayName("Twitch Player")
        self.setApplicationName("Twitch Player")
        self.app_tv_player.setWindowIcon(self.app_icon)
        self.setWindowIcon(self.app_icon)
        self.app_tray = QtWidgets.QSystemTrayIcon()
        self.app_menu = QtWidgets.QMenu()
        self.app_menu.addAction("Show window", self.app_tv_player.show)
        self.app_menu.addAction("Exit", QtWidgets.QApplication.exit)
        self.app_tray.setIcon(self.app_icon)
        self.app_tray.setContextMenu(self.app_menu)
        self.app_tray.show()
        self.moveToCenter()

    def tv_player_show(self):
        self.app_tv_player.show()
        self.app_tray.setIcon(self.icon)
        
    def moveToCenter(self):
        self.screen = self.desktop()
        self.app_tv_player.move((self.screen.width() - self.app_tv_player.frameSize().width()) / 2,
                            (self.screen.height() - self.app_tv_player.frameSize().height()) / 2)




class TwitchPlayer(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle("Twitch Player")
        # vlc init
        self.tv_vlc_vlcobj = vlc.Instance("--ipv4-timeout=1000")
        # media player object
        self.tv_vlc_mediaplayer = self.tv_vlc_vlcobj.media_player_new()
        # EndCatcher
        self.tv_vlc_event_manager = self.tv_vlc_mediaplayer.event_manager()
        self.tv_vlc_event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.http_error, None)
        # frame for video player
        self.tv_player = QtWidgets.QFrame() 
        self.tv_player_constructor = self.tv_player.palette()
        self.tv_player_constructor.setColor(QtGui.QPalette.Window,QtGui.QColor(0, 0, 0))
        self.tv_player.setPalette(self.tv_player_constructor)
        self.tv_player.setAutoFillBackground(True)
        # self.tv_player.underMouse()
        # setting window for video player
        self.tv_vlc_mediaplayer.set_xwindow(self.tv_player.winId())

        # GUI
        # helper window init
        self.tv_widgets_helper_window()
        # channels
        self.tv_widget_channel_name = QtWidgets.QLineEdit()
        self.tv_widget_channel_name.setPlaceholderText("channel name")
        # completer
        self.tv_completer = QtWidgets.QCompleter(self.tv_function_get_channels_from_cache())
        self.tv_widget_channel_name.setCompleter(self.tv_completer)
        self.tv_widget_channel_name.clearFocus()
        self.tv_widget_channel_name.setAlignment(QtCore.Qt.AlignHCenter)
        # channels
        self.tv_widget_channels_menu_button = QtWidgets.QPushButton("Channels")
        self.tv_widget_channels_menu_add_button = QtWidgets.QPushButton("Add to list")
        self.tv_widget_channels_menu_del_button = QtWidgets.QPushButton("Delete from list")
        # channels icons
        self.online_icon = QtGui.QIcon("resource/streamer_online.png")
        self.offine_icon = QtGui.QIcon("resource/streamer_offline.png")
        
        self.tv_widget_channels_frame = QtWidgets.QFrame()
        self.tv_channels_box = QtWidgets.QToolBox()
        self.tv_channels_grid = QtWidgets.QGridLayout()
        self.tv_channels_list = QtWidgets.QListView()
        self.tv_channels_refresh_button = QtWidgets.QPushButton("Refresh")
        self.tv_channels_grid.addWidget(self.tv_channels_list,1,1,3,3)
        self.tv_channels_grid.addWidget(self.tv_channels_refresh_button, 3,0)
        self.tv_channels_grid.addWidget(self.tv_widget_channels_menu_add_button,1,0)
        self.tv_channels_grid.addWidget(self.tv_widget_channels_menu_del_button,2,0)
        self.tv_widget_channels_frame.setLayout(self.tv_channels_grid)
        self.tv_widget_channels_frame.setFixedHeight(100)
        self.tv_widget_channels_frame.hide()
        self.tv_widget_open_button = QtWidgets.QPushButton('Open')
        self.tv_online_check = QtWidgets.QCheckBox("online check")

        # bottom line
        self.tv_widget_resolutions_menu = QtWidgets.QComboBox()
        

        self.tv_widget_play_button = QtWidgets.QPushButton("Play")
        self.tv_widget_fullscreen_button = QtWidgets.QPushButton("Full Screen")
        self.tv_widget_volumeslider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.tv_widget_volumeslider.setMaximum(100)
        self.tv_widget_volumeslider.setValue(self.tv_vlc_mediaplayer.audio_get_volume())
        self.tv_widget_volumeslider.setToolTip("Volume")
        self.tv_widget_volumeslider.valueChanged.connect(self.setVolume)

        self.tv_widget_channels_menu_button.setFixedSize(90,25)
        self.tv_widget_play_button.setFixedSize(90,25)
        self.tv_widget_channel_name.setFixedSize(200, 25)
        self.tv_widget_volumeslider.setFixedSize(100, 25)
        self.tv_widget_resolutions_menu.setFixedSize(100, 25)
        self.tv_widget_fullscreen_button.setFixedSize(90, 25)
        self.tv_widget_open_button.setFixedSize(90, 25)
        self.tv_online_check.setFixedSize(110, 25)
        self.tv_widget_channels_menu_add_button.setFixedSize(140, 25)
        self.tv_widget_channels_menu_del_button.setFixedSize(140, 25)

        # Boxes
        self.gbox = QtWidgets.QGridLayout()
        self.top_box_L = QtWidgets.QHBoxLayout()
        self.top_box_L.addWidget(self.tv_widget_channel_name)
        self.top_box_L.addWidget(self.tv_widget_open_button)
        self.top_box_L.addWidget(self.tv_widget_channels_menu_button)

        self.top_box_R = QtWidgets.QHBoxLayout()

        self.top_box_R.addWidget(self.tv_online_check, alignment=QtCore.Qt.AlignRight)

        self.bottom_box_L = QtWidgets.QHBoxLayout()
        self.bottom_box_L.addWidget(self.tv_widget_play_button)
        self.bottom_box_L.addWidget(self.tv_widget_resolutions_menu)

        self.bottom_box_R = QtWidgets.QHBoxLayout()
        self.bottom_box_R.setAlignment(QtCore.Qt.AlignRight)
        self.bottom_box_R.addWidget(self.tv_widget_volumeslider)
        self.bottom_box_R.addWidget(self.tv_widget_fullscreen_button, alignment=QtCore.Qt.AlignHCenter)
        # Main Box
        self.gbox.addLayout(self.top_box_L, 0, 0, QtCore.Qt.AlignLeft)
        self.gbox.addLayout(self.top_box_R, 0,1, QtCore.Qt.AlignRight)
        self.gbox.addWidget(self.tv_widget_channels_frame,2,0)
        self.gbox.addWidget(self.tv_player, 3, 0)
        self.gbox.addLayout(self.bottom_box_L, 4, 0, QtCore.Qt.AlignLeft)
        self.gbox.addLayout(self.bottom_box_R, 4, 1, QtCore.Qt.AlignRight)

        # Setting Layout
        self.setLayout(self.gbox)

        self.tv_widget_play_button.setDisabled(True)
        self.tv_widget_resolutions_menu.setDisabled(True)

        # Signals
        self.tv_widget_play_button.clicked.connect(self.tv_function_play_button_clicked)
        self.tv_widget_open_button.clicked.connect(self.tv_function_twitch_get_channel)
        self.tv_widget_fullscreen_button.clicked.connect(self.full_screen)
        self.tv_widget_channels_menu_add_button.clicked.connect(self.tv_function_save_channel_to_cache)
        self.tv_widget_channels_menu_del_button.clicked.connect(self.tv_function_del_channel_from_cache)
        self.tv_widget_channels_menu_button.clicked.connect(self.tv_function_show_channels_frame)
        self.channel_upped = 0

    ###
    ###
    # Interface functions
    ###
    ###

    def tv_widgets_helper_window(self):
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
        self.tv_vlc_mediaplayer.stop()
        event.ignore()

    def hide_to_tray(self):
        self.hide()
        self.closewindow.hide()

    def hide_helper_window(self):
        self.helperwindow.hide()

    def resizeEvent(self, resizeEvent):
        if (not self.isFullScreen()):
            self.tv_player.setFixedWidth(self.width() - 25)
            self.tv_widget_channels_frame.setFixedWidth(self.width() - 25)

        else:
            self.tv_player.setFixedWidth(self.width())
            
    def setVolume(self):
        """setting volume from self.tv_widget_volumeslider"""
        self.tv_vlc_mediaplayer.audio_set_volume(self.tv_widget_volumeslider.value())

    def full_screen(self):
        """full screen from self.tv_widget_fullscreen_button signal"""
        if self.isFullScreen():
            self.showNormal()
            self.gbox.setContentsMargins(10, 10, 10, 10)
            self.tv_widget_channels_menu_button.show()
            self.tv_widget_play_button.show()
            self.tv_widget_channels_menu_add_button.show()
            self.tv_widget_channels_menu_del_button.show()
            self.tv_widget_channel_name.show()
            self.tv_widget_volumeslider.show()
            self.tv_widget_resolutions_menu.show()
            self.tv_widget_fullscreen_button.show()
            self.tv_widget_open_button.show()
            self.tv_online_check.show()
            self.tv_player.underMouse()
            self.tv_widget_channels_frame.hide()
        else:
            self.tv_widget_channels_frame.hide()
            self.tv_widget_channels_menu_button.hide()
            self.tv_widget_channels_menu_add_button.hide()
            self.tv_widget_channels_menu_del_button.hide()
            self.tv_widget_channel_name.hide()
            self.tv_widget_play_button.hide()
            self.tv_widget_channel_name.hide()
            self.tv_widget_volumeslider.hide()
            self.tv_widget_resolutions_menu.hide()
            self.tv_widget_fullscreen_button.hide()
            self.tv_widget_open_button.hide()
            self.tv_online_check.hide()
            self.gbox.setContentsMargins(0,0,0,0)
            self.showFullScreen()

    def mouseDoubleClickEvent(self, event):
        """Double click for full_screen()"""
        self.full_screen()
    
    ###
    ###
    # Player Functions
    ###
    ###
    def tv_function_twitch_get_channel(self):
        """getting twitch playlist"""
        if self.tv_vlc_mediaplayer.is_playing():
            self.tv_vlc_mediaplayer.stop()
        self.tv_widget_resolutions_menu.setDisabled(False)
        self.channel = self.tv_widget_channel_name.text()
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
            self.tv_function_online_check()

        for source in self.playlist.m3u8.playlists:
            self.tv_widget_volumeslider.setValue(50)
            data = source.stream_info
            self.tv_widget_resolutions_menu.addItem(str(data.resolution[1]), source.uri)
            self.tv_widget_play_button.setDisabled(False)

    def tv_function_play_button_clicked(self):
        """playing video"""
        if self.tv_vlc_mediaplayer.is_playing():
            self.tv_widget_play_button.setText("Play")
            self.tv_vlc_mediaplayer.stop()
            self.tv_widget_resolutions_menu.setDisabled(False)
        else:
            self.tv_widget_resolutions_menu.setDisabled(True)
            self.tv_widget_play_button.setText("Stop")
            self.tv_vlc_mediaplayer.set_mrl(self.tv_widget_resolutions_menu.currentData())
            self.setWindowTitle("Playing {0}".format(self.tv_widget_channel_name.text()))
            self.tv_vlc_mediaplayer.play()
    
    def tv_function_online_check(self):
        # thread
        self.tv_thread = TwitchThread(self.channel)
        self.tv_thread.tv_function_channel_is_up.connect(self.tv_function_channel_is_up, QtCore.Qt.QueuedConnection)
        self.tv_thread.start()

    def tv_function_channel_is_up(self, signal):
        self.channel_upped = signal
        if self.channel_upped:
            # Message
            if app.app_tv_player.isHidden():
                app.app_tray.showMessage("Twitch Player",
                                     "{0} is streaming!".format(self.tv_widget_channel_name.text()),
                                     msecs=10000)
                app.app_tray.setIcon(app.icon_online)
            self.tv_widget_tv_function_twitch_get_channel()

    
    def tv_function_save_channel_to_cache(self):
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
        add_channel = '''INSERT INTO channame (name) VALUES ('{0}');'''.format(self.tv_widget_channel_name.text())
        cursor.execute(createtable)
        cursor.execute(add_channel)
        con.commit()
        self.tv_completer = QtWidgets.QCompleter(self.tv_function_get_channels_from_cache())
        self.tv_widget_channel_name.setCompleter(self.tv_completer)

    def tv_function_del_channel_from_cache(self):
        from os.path import expanduser
        from os.path import isfile
        import sqlite3
        home_path = expanduser("~")
        if isfile("{0}/.cache/twitch/twitch.db".format(home_path)):
            con = sqlite3.connect(r'file:///{0}/twitch.db?mode=rw'.format(home_path + "/.cache/twitch"), uri=True)
            cursor = con.cursor()
            del_channel_sql = """DELETE FROM channame WHERE name=\"{0}\";""".format(self.tv_widget_channel_name.text())
            cursor.execute(del_channel_sql)
            con.commit()
        self.tv_completer = QtWidgets.QCompleter(self.tv_function_get_channels_from_cache())
        self.tv_widget_channel_name.setCompleter(self.tv_completer)

    def tv_function_get_channels_from_cache(self):
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

    @vlc.callbackmethod
    def http_error(self,event, data):
        app.app_tray.showMessage("Twitch Player", "Channel is offline", 10000)

    def tv_function_show_channels_frame(self):
        if self.tv_widget_channels_frame.isHidden():
            self.tv_widget_channels_menu_button.setDisabled(True)
            self.tv_function_channels_refresh_frame()
            self.tv_widget_channels_menu_button.setDisabled(False)
        else:
            self.tv_widget_channels_frame.hide()

    def tv_function_channels_refresh_frame(self):
        self.tv_widget_channels_frame.show()
        data = self.tv_function_get_channels_from_cache()
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