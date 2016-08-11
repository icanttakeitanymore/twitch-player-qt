#!/usr/bin/env python3
import sys
from PyQt5 import QtWidgets, QtGui
from twitch_player import TwitchPlayer


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


if __name__ == "__main__":
    app = MainApplication(sys.argv)
    sys.exit(app.exec_())

