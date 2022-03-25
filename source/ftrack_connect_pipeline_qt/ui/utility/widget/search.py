# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrac

from Qt import QtGui, QtCore, QtWidgets

from ftrack_connect_pipeline_qt import utils
from ftrack_connect_pipeline_qt.ui.utility.widget.circular_button import (
    CircularButton,
)
from ftrack_connect_pipeline_qt.utils import clear_layout


class Search(QtWidgets.QFrame):
    '''
    Display a search box, that can be collapsed and expanded.
    '''

    inputUpdated = QtCore.Signal(object)
    search = QtCore.Signal()
    clear = QtCore.Signal()

    @property
    def text(self):
        return self._input.text() if self._input else ''

    @text.setter
    def text(self, value):
        if self._input:
            self._input.setText(value)

    def __init__(self, parent=None, collapsed=True, collapsable=True):
        super(Search, self).__init__(parent=parent)

        self._collapsed = collapsed
        self._collapsable = collapsable
        self.pre_build()
        self.build()
        self.post_build()

    def pre_build(self):
        '''Prepare general layout.'''
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.layout().setContentsMargins(4, 1, 5, 1)
        self.layout().setSpacing(1)
        self.setMaximumHeight(33)
        self.setMinimumHeight(33)

    def build(self):
        '''Build widgets and parent them.'''
        self.rebuild()

    def post_build(self):
        '''Post Build ui method for events connections.'''
        self._search_button.clicked.connect(self._on_search)

    def rebuild(self):
        # Remove current widgets, clear input
        clear_layout(self.layout())
        if self._collapsed:
            # Just the circular search button
            self.layout().addStretch()
            self._input = None
            self.setStyleSheet('''border:none;''')
            self._search_button = CircularButton('search', '#999999')
            self._search_button.setStyleSheet(
                '''
                border: 1px solid #555555;
                border-radius: 16px;
            '''
            )
        else:
            self._search_button = CircularButton(
                'search', '#999999', diameter=30
            )

        if self._collapsable:
            self.layout().addWidget(self._search_button)

        if not self._collapsed:
            # A bordered input field filling all space, with input and a clear button
            self._search_button.setStyleSheet(
                '''
                    border:none; 
                    background: transparent;
                '''
            )
            self._input = QtWidgets.QLineEdit()
            self._input.setReadOnly(False)
            self._input.textChanged.connect(self._on_input_changed)
            self._input.setPlaceholderText("Type to search")
            self._input.setStyleSheet(
                '''border: none; background: transparent; '''
            )
            self._input.setFocus()
            self.layout().addWidget(self._input, 100)
            # self._clear_button = CircularButton(
            #    'close', '#555555', diameter=30
            # )
            # self._clear_button.setStyleSheet('''border:none;''')
            # self._clear_button.clicked.connect(self._on_clear)
            # self.layout().addWidget(self._clear_button)
            self.setStyleSheet(
                '''
                border: 1px solid #555555;
                border-radius: 16px;
            '''
            )
            if not self._collapsable:
                self.layout().addWidget(self._search_button)

    def _on_search(self):
        if self._collapsable:
            self._collapsed = not self._collapsed
            self.rebuild()
            self.inputUpdated.emit('')

    def _on_input_changed(self):
        self.inputUpdated.emit(self._input.text())

    def _on_clear(self):
        self._input.setText('')
        self._input.setFocus()
        self.clear.emit()
