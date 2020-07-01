# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack


from Qt import QtCore, QtWidgets
from ftrack_connect_pipeline_qt.client.widgets.schema import BaseJsonWidget


class JsonNumber(BaseJsonWidget):
    '''Widget representation of an number'''

    def __init__(
            self, name, schema_fragment, fragment_data,
            previous_object_data, widget_factory, parent=None
    ):
        '''Initialise JsonNumber with *name*, *schema_fragment*,
        *fragment_data*, *previous_object_data*, *widget_factory*, *parent*'''
        super(JsonNumber, self).__init__(
            name, schema_fragment, fragment_data, previous_object_data,
            widget_factory, parent=parent
        )

    def build(self):
        hbox = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel(self.name)
        self.spin  = QtWidgets.QDoubleSpinBox()

        self.label.setToolTip(self.description)

        hbox.addWidget(self.label)
        hbox.addWidget(self.spin)

        self.layout().addLayout(hbox)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def to_json_object(self):
        return self.spin.value()
