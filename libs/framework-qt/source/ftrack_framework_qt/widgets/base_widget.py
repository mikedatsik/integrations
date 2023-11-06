# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack

from Qt import QtWidgets, QtCore, QtGui

from ftrack_framework_widget.widget import FrameworkWidget


class BaseWidget(FrameworkWidget, QtWidgets.QWidget):
    '''Main class to represent base framework widget.'''

    name = 'base_widget'
    ui_type = 'qt'

    def __init__(
        self,
        event_manager,
        client_id,
        context_id,
        plugin_config,
        dialog_connect_methods_callback,
        dialog_property_getter_connection_callback,
        parent=None,
    ):
        '''initialise base widget with *parent*, *session*, *data*,
        *name*, *description*, *options* and *context*
        '''

        QtWidgets.QWidget.__init__(self, parent=parent)
        FrameworkWidget.__init__(
            self,
            event_manager,
            client_id,
            context_id,
            plugin_config,
            dialog_connect_methods_callback,
            dialog_property_getter_connection_callback,
            parent=parent,
        )

        self.pre_build_ui()
        self.build_ui()
        self.post_build_ui()