# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from Qt import QtCore, QtWidgets

from PySide2 import (
    QtWebEngineWidgets,
)  # Qt.py does not provide QtWebEngineWidgets

from ftrack_connect_pipeline.utils import get_current_context_id
from ftrack_connect_pipeline.client import Client
from ftrack_connect_pipeline_qt.ui.utility.widget import dialog, header
from ftrack_connect_pipeline_qt.ui import theme


class QtWebViewClient(Client, dialog.Dialog):
    '''Web widget viewer client base - a dialog for rendering web content within
    framework'''

    def __init__(self, event_manager, parent=None):

        dialog.Dialog.__init__(self, parent=parent)
        Client.__init__(self, event_manager)

        self._context = None

        if self.getTheme():
            self.setTheme(self.getTheme())
            if self.getThemeBackgroundStyle():
                self.setProperty('background', self.getThemeBackgroundStyle())

        self.pre_build()
        self.build()

        self.resize(500, 600)

    def getTheme(self):
        '''Return the client theme, return None to disable themes. Can be overridden by child.'''
        return 'dark'

    def setTheme(self, selected_theme):
        theme.applyFont()
        theme.applyTheme(self, selected_theme, 'plastique')

    def getThemeBackgroundStyle(self):
        '''Return the theme background color style. Can be overridden by child.'''
        return 'ftrack'

    def pre_build(self):
        self._header = header.Header(self.session, parent=self.parent())
        self._web_engine_view = QtWebEngineWidgets.QWebEngineView(
            parent=self.parent()
        )
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def build(self):
        self.layout().addWidget(self._header)
        self.layout().addWidget(self._web_engine_view, 100)

    def set_context_id(self, context_id):
        '''Set the context ID supplied bu *context_id* and load web contents'''
        self._context = self.session.query(
            'Task where id={}'.format(context_id)
        ).one()
        self._web_engine_view.load(self.get_url())

    def show(self):
        '''Show the dialog, sets the context to default and loads content if not done previously'''
        if self._context is None:
            self.set_context_id(get_current_context_id())
        super(QtWebViewClient, self).show()

    def get_url(self):
        '''Retreive the URL of content to view'''
        raise NotImplementedError()


class QtInfoWebViewClient(QtWebViewClient):
    '''Show the current context(task) info within a web client dialog'''

    def __init__(self, event_manger, unused_asset_model, parent=None):
        super(QtInfoWebViewClient, self).__init__(event_manger, parent=parent)
        self.setWindowTitle('Task info')

    def get_url(self):
        return self.session.get_widget_url('info', entity=self._context)


class QtTasksWebViewClient(QtWebViewClient):
    '''Show assigned tasks with a web client dialog'''

    def __init__(self, event_manger, unused_asset_model, parent=None):
        super(QtTasksWebViewClient, self).__init__(event_manger, parent=parent)
        self.setWindowTitle('My Tasks')

    def get_url(self):
        return self.session.get_widget_url('tasks')
