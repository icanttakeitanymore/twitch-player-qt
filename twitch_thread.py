from PyQt5 import QtCore
from twitch_api import TwitchData
import time

class TwitchThread(QtCore.QThread):
    # Этот красс является потоком основного процесса.
    # Определяем сигнал, он возвращает строку.
    channel_is_up = QtCore.pyqtSignal(int)

    # При инициализации экземпляра инициализируется конструктор класса QThread
    def __init__(self,channel,parent=None):
        QtCore.QThread.__init__(self,parent)
        self.channel = channel
        self.check = 0
    # В этом методе находится тело потока.
    def run(self):
        while(not self.check):
            print("here")
            try:
                self.playlist = TwitchData(self.channel)
            except KeyError:
                print("channel non found")
                return 1
            if len(self.playlist.m3u8.playlists) != 0:
                self.channel_is_up.emit(1)
                self.check = 1
            self.sleep(3)

    def time_pass(self):
        pass




