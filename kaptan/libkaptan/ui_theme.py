# Copyright 2016 Metehan Özbek <mthnzbk@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from PyQt6.QtWidgets import QWizardPage, QLabel, QGroupBox, QCheckBox, QVBoxLayout, QSpacerItem, QSizePolicy, QHBoxLayout,\
    QSpinBox, QComboBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import *
from os.path import join
import os
from .tools import Parser
from .tabwidget import ThemeTabWidget

class ThemeWidget(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSubTitle(self.tr("<h2>Customize Your Desktop</h2>"))

        vlayout = QVBoxLayout(self)

        labelLayout = QHBoxLayout()
        imageLabel = QLabel()
        imageLabel.setMaximumSize(64, 64)
        imageLabel.setPixmap(QIcon.fromTheme("preferences-desktop-color").pixmap(64, 64))
        labelLayout.addWidget(imageLabel)

        label = QLabel(self)
        label.setText(self.tr("<p>Choose your favorite theme and desktop type. Customize Pisi Linux with colorful styles and themes.</p>"))
        labelLayout.addWidget(label)
        vlayout.addLayout(labelLayout)

        vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        self.createGroupBox(vlayout)
        self.createDesktopOption(vlayout)

        self.desktopCount = 1
        self.desktopType = "org.kde.desktopcontainment"
        self.iconSet = None
        self.mouseCursor = None
        self.showDesktop = False
        self.widgetStyle = "breeze"
        self.windowStyle = None
        self.colorScheme = None
        self.desktopTheme = None


    def createGroupBox(self, layout):
        group1 = QGroupBox(self)
        group1.setMinimumHeight(200)
        layout.addWidget(group1)

        grLayout = QVBoxLayout(group1)
        tabWidget = ThemeTabWidget(group1)
        grLayout.addWidget(tabWidget)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))

        tabWidget.listWidgetIconSet.itemClicked.connect(self.iconSetSelect)
        tabWidget.listWidgetMouseCursor.itemClicked.connect(self.mouseCursorSelect)
        tabWidget.listWidgetWindowStyle.itemClicked.connect(self.windowStyleSelect)
        # tabWidget.comboBoxWidgetStyle.currentIndexChanged[str].connect(self.widgetStyleSelect)
        tabWidget.comboBoxWidgetStyle.currentTextChanged.connect(self.widgetStyleSelect)
        tabWidget.listWidgetDesktopTheme.itemClicked.connect(self.desktopThemeSelect)
        tabWidget.listWidgetColorScheme.itemClicked.connect(self.colorSchemeSelect)


    def createDesktopOption(self, layout):
        hlayout = QHBoxLayout(self)
        layout.addLayout(hlayout)

        vlayout1 = QVBoxLayout()
        vlayout2 = QVBoxLayout()
        hlayout.addLayout(vlayout1)
        hlayout.addItem(QSpacerItem(20, 30, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        hlayout.addLayout(vlayout2)

        label1 = QLabel()
        label1.setText(self.tr("Desktop Type"))
        vlayout1.addWidget(label1)
        label2 = QLabel()
        label2.setText(self.tr("Number of Desktops"))
        vlayout2.addWidget(label2)

        comboBox = QComboBox()
        comboBox.addItem(self.tr("Desktop View"))
        comboBox.addItem(self.tr("Folder View"))
        comboBox.currentIndexChanged.connect(self.desktopTypeCreate)
        vlayout1.addWidget(comboBox)
        spinBox = QSpinBox()
        spinBox.setMinimum(1)
        spinBox.setMaximum(20)
        spinBox.valueChanged.connect(self.desktopCreate)
        vlayout2.addWidget(spinBox)
        self.checkBox = QCheckBox()
        self.checkBox.setText(self.tr("Add Show Desktop Applet"))
        self.checkBox.clicked.connect(self.showDesktopF)
        hlayout.addItem(QSpacerItem(20, 30, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        hlayout.addWidget(self.checkBox)

    def windowStyleSelect(self, item):
        self.windowStyle = item.setStyleText

    def widgetStyleSelect(self, text):
        self.widgetStyle = text.lower()

    def desktopThemeSelect(self, item):
        self.desktopTheme = item.panelText

    def colorSchemeSelect(self, item):
        self.colorScheme = item.colorSchemeName

    def showDesktopF(self):
        self.showDesktop = self.checkBox.isChecked()

    def iconSetSelect(self, item):
        self.iconSet = str(item.text()).lower()

    def mouseCursorSelect(self, item):
        self.mouseCursor = item.text()

    def desktopCreate(self, value):
        self.desktopCount = value

    def desktopTypeCreate(self, value):
        if value == 0:
            self.desktopType = "org.kde.desktopcontainment"
        else:
            self.desktopType = "org.kde.plasma.folder"

    def execute(self):
        settings = QSettings(join(QDir.homePath(), ".config", "kwinrc"), QSettings.Format.IniFormat)
        settings.setValue("Desktops/Number", self.desktopCount)
        settings.setValue("Desktops/Rows", 2)
        settings.sync()

        if self.iconSet != None:
            settings = QSettings(join(QDir.homePath(), ".config", "kdeglobals"), QSettings.Format.IniFormat)
            settings.setValue("Icons/Theme", self.iconSet)
            settings.sync()

            os.system("rm -rf {}".format(join(QDir.homePath(), ".cache", "icon-cache.kcache")))

        if self.widgetStyle != None:
            settings = QSettings(join(QDir.homePath(), ".config", "kdeglobals"), QSettings.Format.IniFormat)
            settings.setValue("KDE/widgetStyle", self.widgetStyle.lower())
            settings.sync()

        if self.windowStyle != None:
            settings = QSettings(join(QDir.homePath(), ".config", "kwinrc"), QSettings.Format.IniFormat)
            settings.setValue("org.kde.kdecoration2/library", self.windowStyle)
            settings.sync()

            prc = QProcess()
            prc.startDetached("kwin_x11", ["--replace"]) #kwinrc yi sisteme işleyen komut.

        if self.desktopTheme != None:
            settings = QSettings(join(QDir.homePath(), ".config", "plasmarc"), QSettings.Format.IniFormat)
            settings.setValue("Theme/name", self.desktopTheme)
            settings.sync()

        if self.mouseCursor != None:
            # settings = QSettings(join(QDir.homePath(), ".config", "kcminputrc"), QSettings.Format.IniFormat)
            # settings.setValue("Mouse/cursorTheme", self.mouseCursor)
            # settings.sync()
            # print(self.mouseCursor)

            prc = QProcess()
            prc.startDetached("plasma-apply-cursortheme", ["{}".format(self.mouseCursor)]) #fare imlecini sisteme işleyen komut.

        if self.colorScheme != None:
            colorSettings = QSettings(join("/usr/share/color-schemes", self.colorScheme), QSettings.Format.IniFormat)
            colorParameter = colorSettings.allKeys()
            print(join("/usr/share/color-schemes", self.colorScheme))
            settings = QSettings(join(QDir.homePath(), ".config", "kdeglobals"), QSettings.Format.IniFormat)
            for parameter in colorParameter:
                print(parameter, colorSettings.value(parameter))
                settings.setValue(parameter, colorSettings.value(parameter))

            settings.sync()

            #Ayar gruplarında olan : karakterini %3A ya çevirdiği için bu yöntem ile çözüyoruz.
            with open(join(QDir.homePath(), ".config", "kdeglobals"), "r+") as rep:
                cache = rep.read().replace("%3A", ":")
                rep.seek(0)
                rep.truncate()
                rep.write(cache)

        configFilePath = join(QDir.homePath(), ".config", "plasma-org.kde.plasma.desktop-appletsrc")

        parser = Parser(configFilePath)

        if self.desktopTypeCreate != None:
            parser.setDesktopType(self.desktopType)

        # desktopView = parser.getDesktopType()
        #no need for these lines, parser is already executing this logic
        # if self.desktopType != desktopView[1]:
        #    parser.setDesktopType(self.desktopType)

        if self.showDesktop:
            parser.setShowDesktopApplet()
