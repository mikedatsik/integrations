# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack


from Qt import QtGui, QtCore, QtWidgets
from ftrack_connect_pipeline_qt.client.widgets.schema import JsonObject


class PluginContainerObject(JsonObject):
    '''
    Override widget representation of an object
    '''

    def __init__(
            self, name, schema_fragment, fragment_data,
            previous_object_data, widget_factory, parent=None
    ):
        '''Initialise PluginContainerObject with *name*, *schema_fragment*,
        *fragment_data*, *previous_object_data*, *widget_factory*, *parent*'''
        super(PluginContainerObject, self).__init__(
            name, schema_fragment, fragment_data, previous_object_data,
            widget_factory, parent=parent
        )

    def build(self):
        if self.previous_object_data:
            self.stage_name = self.previous_object_data.get('name')

        self.properties_widgets = {}

        if not self.properties:
            label = QtWidgets.QLabel(
                'Invalid object description (missing properties)',
                self)
            label.setStyleSheet('QLabel { color: red; }')
            self.layout().addWidget(label)
        else:
            if 'widget' in list(self.properties.keys()):
                widget = self.widget_factory.fetch_plugin_widget(
                    self.fragment_data, self.stage_name
                )
                self.layout().addWidget(widget)
            else:
                for k, v in list(self.properties.items()):
                    new_fragment_data = None
                    if self.fragment_data:
                        new_fragment_data = self.fragment_data.get(k)
                    widget = self.widget_factory.create_widget(
                        k, v, new_fragment_data, self.fragment_data
                    )
                    self.layout().addWidget(widget)
                    self.properties_widgets[k] = widget
