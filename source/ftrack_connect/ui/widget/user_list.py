# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.item_list
import ftrack_connect.ui.widget.user
import ftrack_connect.ui.widget.label


class GroupHeader(QtGui.QLabel):
    '''Group header widget.'''
    def __init__(self, parent=None):
        super(GroupHeader, self).__init__(parent)
        self.setObjectName('header')

    def value(self):
        '''Return value for group header.'''
        return self.text()


class UserList(ftrack_connect.ui.widget.item_list.ItemList):
    '''User list widget.'''

    #: Signal to handle click events.
    itemClicked = QtCore.Signal(object)

    def __init__(self, groups=None, parent=None):
        '''Initialise widget with *groups*.'''
        if groups is None:
            groups = []

        super(UserList, self).__init__(
            widgetFactory=self._createWidget,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )
        self.setObjectName('presence-list')
        self.list.setSelectionMode(
            QtGui.QAbstractItemView.NoSelection
        )
        self.list.setShowGrid(False)

        for group in groups:
            self.addUser(group.capitalize())

    def _createWidget(self, item):
        '''Return user widget for *item*.'''
        if item is None:
            item = {}

        if isinstance(item, basestring):
            return GroupHeader(item)

        widget = ftrack_connect.ui.widget.user.User(**item)
        widget.itemClicked.connect(
            self.itemClicked.emit
        )

        return widget

    def userExists(self, userId):
        '''Return true if *userId* exists.'''
        if self.getUser(userId):
            return True

        return False

    def getUser(self, userId):
        '''Return user if in list otherwise None.'''
        for row in range(self.count()):
            widget = self.list.widgetAt(row)
            value = self.widgetItem(widget)

            if isinstance(value, dict) and value['userId'] == userId:
                return widget

        return None

    def addUser(self, item, row=None):
        '''Add *item* at *row*.

        If *row* is not specified, then append item to end of list.

        '''
        if not isinstance(item, basestring):
            group = item.get('group')
            row = self.indexOfItem(group.capitalize())

            if row is None:
                raise ValueError('group {0} not recognized'.format(group))

            row += 1

        return super(UserList, self).addItem(item, row=row)

    def updatePosition(self, user):
        '''Update position of *user* based on user's group.'''
        row = self.indexOfItem(user.value())

        if row:
            self.removeItem(row)

            value = user.value()

            if not user.online:
                value['group'] = 'offline'

            self.addUser(value)
