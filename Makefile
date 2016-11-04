# Main TARGET
TARGET = package
# DEBIAN/control
SOURCE = Source: twitch-player-qt5
SELECTION = Selection: video
PRIORITY = Priority: extra
MAINTAINER = "Maintainer: Polozov Boris <polozovbv@gmail.com>"
DEPENDS = Depends: python3-pyqt5, python3-m3u8, python3-requests, python3
VER = Version: 0.1.0
HOMEPAGE = Homepage: https://github.com/polozovbv/twitch-player-qt
PACKAGE = Package: twitch-player-qt5
ARCH = Architecture: all
DESCRIPT = Description: Twitch tv player.
# Path for package
PATH1 = ./usr/share/twitch-player-qt5
PATH2 = ./usr/local/bin
# for use need to change paths
sedline1 = self.app_icon = QtGui.QIcon("resource/twitch.png")
sedline1_1 = self.app_icon = QtGui.QIcon("/usr/share/twitch-player-qt5/resource/twitch.png")

sedline2 = self.app_icon_online = QtGui.QIcon("resource/twitch_online.png")
sedline2_1 = self.app_icon_online = QtGui.QIcon("/usr/share/twitch-player-qt5/resource/twitch_online.png")

sedline3 = self.offine_icon = QtGui.QIcon("resource/streamer_offline.png")
sedline3_1 = self.offine_icon = QtGui.QIcon("/usr/share/twitch-player-qt5/resource/streamer_offline.png")

sedline4 = self.online_icon = QtGui.QIcon("resource/streamer_online.png")
sedline4_4 = self.online_icon = QtGui.QIcon("/usr/share/twitch-player-qt5/resource/streamer_online.png")

all:$(TARGET)
package:
	@echo Preparing..
	@mkdir -p $(PATH1)
	@mkdir -p $(PATH2)
	@cp twitch_player.py $(PATH1)
	@cp twitch_thread.py $(PATH1)
	@cp twitch_api.py $(PATH1)
	@cp -R resource $(PATH1)
	@sed -i -e 's|$(sedline1)|$(sedline1_1)|g' \
		./usr/share/twitch-player-qt5/twitch_player.py
	@sed -i -e 's|$(sedline2)|$(sedline2_1)|g' \
		./usr/share/twitch-player-qt5/twitch_player.py
	@sed -i -e 's|$(sedline3)|$(sedline3_1)|g' \
		./usr/share/twitch-player-qt5/twitch_player.py
	@sed -i -e 's|$(sedline4)|$(sedline4_1)|g' \
		./usr/share/twitch-player-qt5/twitch_player.py
	# exec bin
	@echo Creating sh in /usr/local/bin
	@touch $(PATH2)/twitch-player-qt5
	@printf "#!/bin/sh\n/usr/bin/python3 /usr/share/twitch-player-qt5/twitch_player.py\n" > $(PATH2)/twitch-player-qt5
	@chmod +x $(PATH2)/twitch-player-qt5
	# Shortcut
	@echo Creating .desktop file
	@mkdir -p ./usr/share/applications
	@mkdir -p ./usr/share/pixmaps
	@cp ./resource/twitch.png ./usr/share/pixmaps
	@touch ./usr/share/applications/twitch-player-qt5.desktop
	@echo "[Desktop Entry]" > ./usr/share/applications/twitch-player-qt5.desktop
	@echo Icon=twitch.png >> ./usr/share/applications/twitch-player-qt5.desktop
	@echo "Name=Twitch Player Qt5" >> ./usr/share/applications/twitch-player-qt5.desktop
	@echo Exec=/usr/local/bin/twitch-player-qt5 >> ./usr/share/applications/twitch-player-qt5.desktop
	@echo Type=Allpication >> ./usr/share/applications/twitch-player-qt5.desktop
	@echo "Categories=AudioVideo;Player;" >> ./usr/share/applications/twitch-player-qt5.desktop
	@echo Terminal=false >> ./usr/share/applications/twitch-player-qt5.desktop
	# making package
	@echo Creating package.
	@mkdir DEBIAN
	@touch DEBIAN/control
	@echo $(PACKAGE) > DEBIAN/control
	@echo $(SOURCE) >> DEBIAN/control
	@echo $(ARCH) >> DEBIAN/control
	@echo $(DEPENDS) >> DEBIAN/control
	@echo $(PRIORITY) >> DEBIAN/control
	@echo $(SELECTION) >> DEBIAN/control
	@echo $(VER) >> DEBIAN/control
	@echo $(MAINTAINER) >> DEBIAN/control
	@echo $(DESCRIPT) >> DEBIAN/control
	@touch DEBIAN/postinst
	@chmod +x DEBIAN/postinst
	@echo "#!/bin/sh" >> DEBIAN/postinst
	@echo 'if [ "$1" = "configure" ] && [ -x "`which update-menus 2>/dev/null`" ] ; then update-menus ;fi' >> DEBIAN/postinst
	@echo Clean temp files.
	@mkdir twitch-player-qt5
	@cp -r usr twitch-player-qt5
	@cp -r DEBIAN twitch-player-qt5
	@md5deep -r ./twitch-player-qt5/usr >> ./twitch-player-qt5/DEBIAN/md5sums
	@fakeroot dpkg-deb --build twitch-player-qt5
	@rm -rf twitch-player-qt5
	@echo
	@echo
	@echo "		######################################"
	@echo "		#     For using you want run         #"
	@echo "		# sudo dpkg -i twitch-player-qt5.deb #"
	@echo "		# sudo apt-get -f install            #"
	@echo "		# sudo pip3 install python-vlc       #"
	@echo "		######################################"
	@echo
	@echo
	@echo Done.
clean:
	rm -rf ./usr
	rm -rf ./DEBIAN
	rm -rf ./twitch-player-qt5