# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import webbrowser

from PySide import QtCore, QtGui

import header_rc
import ftrack

class Ui_Header(object):

    def setupUi(self, Header):
        Header.setObjectName("Header")
        Header.resize(198, 35)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Header.sizePolicy().hasHeightForWidth())
        Header.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(Header)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setContentsMargins(9, 0, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.logoLabel = QtGui.QLabel(Header)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.logoLabel.sizePolicy().hasHeightForWidth()
        )
        self.logoLabel.setSizePolicy(sizePolicy)
        self.logoLabel.setMinimumSize(QtCore.QSize(21, 22))
        self.logoLabel.setMaximumSize(QtCore.QSize(21, 22))
        self.logoLabel.setText("")
        self.logoLabel.setTextFormat(QtCore.Qt.AutoText)
        self.logoLabel.setPixmap(QtGui.QPixmap(":/fbox.png"))
        self.logoLabel.setScaledContents(False)
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayout.addWidget(self.logoLabel)
        self.titleLabel = QtGui.QLabel(Header)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.horizontalLayout.addWidget(self.titleLabel)
        spacerItem = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.userButton = QtGui.QPushButton(Header)
        self.userButton.setMinimumSize(QtCore.QSize(35, 35))
        self.userButton.setMaximumSize(QtCore.QSize(35, 35))
        self.userButton.setText("")
        self.userButton.setIconSize(QtCore.QSize(30, 30))
        self.userButton.setFlat(True)
        self.userButton.setObjectName("userButton")
        self.horizontalLayout.addWidget(self.userButton)

        self.retranslateUi(Header)
        QtCore.QObject.connect(
            self.userButton, QtCore.SIGNAL("clicked()"), Header.openHelp
        )
        QtCore.QMetaObject.connectSlotsByName(Header)

    def retranslateUi(self, Header):
        Header.setWindowTitle(QtGui.QApplication.translate(
            "Header", "Form", None, QtGui.QApplication.UnicodeUTF8)
        )
        self.titleLabel.setText(QtGui.QApplication.translate(
            "Header", "Title", None, QtGui.QApplication.UnicodeUTF8)
        )


class SimpleHeaderWidget(QtGui.QWidget):

    def __init__(self, parent=None, task=None):
        QtGui.QWidget.__init__(self, parent)

        self.current_user = ftrack.User(os.getenv('LOGNAME'))
        self.ui = Ui_Header()
        self.ui.setupUi(self)
        self.setFixedHeight(40)
        self.resize(198, 35)

        icon = self.getUserIcon()
        self.ui.userButton.setIcon(icon)

        logoPixmap = QtGui.QPixmap(':ftrack/image/light/ftrackLogoGrey')
        self.ui.logoLabel.setPixmap(
            logoPixmap.scaled(
                self.ui.logoLabel.size(), QtCore.Qt.KeepAspectRatio
            )
        )

        p = self.palette()
        currentColor = p.color(QtGui.QPalette.Window)
        p.setBrush(
            QtGui.QPalette.Window, QtGui.QBrush(currentColor.darker(200))
        )
        self.setPalette(p)
        self.setAutoFillBackground(True)

    def getUserIcon(self):
        import urllib
        img = QtGui.QImage()
        default_user_icon = os.environ["FTRACK_SERVER"] + "/img/userplaceholder.png"
        user_icon = self.current_user.getThumbnail() or default_user_icon
        img.loadFromData(urllib.urlopen(user_icon).read())
        return QtGui.QIcon(QtGui.QPixmap(img))

    def setTitle(self, title):
        self.ui.titleLabel.setText(title)

    def openHelp(self):
        webbrowser.open(self.helpUrl)

class HeaderWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(HeaderWidget, self).__init__(parent=parent)
        self.header = SimpleHeaderWidget()
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.header)
        self.__create_message_area()

        self.resize(198, 35)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)


    def __create_message_area(self):
        self.message_area = QtGui.QLabel('', parent=self)
        self.message_area.setObjectName('ftrack-message-area-info')
        self.message_area.resize(QtCore.QSize(900, 80))
        self.message_area.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )
        self.message_area.setVisible(False)
        self.layout.addWidget(self.message_area)

    def setHeaderTitle(self, title):
        self.header.ui.titleLabel.setText(title)

    def setMessage(self, message, type='info'):
        message_types = ['info', 'warning', 'error']
        if type not in message_types:
            raise ValueError('Message type should be one of: %' ', '.join(message_types))

        class_type = 'ftrack-header-message-%s' % type
        self.message_area.setObjectName(class_type)
        self.message_area.setText(message)
        self.message_area.setVisible(True)

    def getCurrentUser(self):
        return self.header.current_user