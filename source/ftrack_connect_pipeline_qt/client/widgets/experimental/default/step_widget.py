# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import logging
from ftrack_connect_pipeline_qt.client.widgets.experimental import BaseUIWidget
from Qt import QtGui, QtCore, QtWidgets


class DefaultStepWidget(BaseUIWidget):
    '''Widget representation of a boolean'''
    def __init__(self, name, fragment_data, parent=None):
        '''Initialise JsonBoolean with *name*, *schema_fragment*,
        *fragment_data*, *previous_object_data*, *widget_factory*, *parent*'''

        self.step_optional = False

        super(DefaultStepWidget, self).__init__(
            name, fragment_data, parent=parent
        )

    def pre_build(self):
        self.step_optional = self.fragment_data.get('optional')

    def build(self):
        self._widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        self._widget.setLayout(main_layout)
