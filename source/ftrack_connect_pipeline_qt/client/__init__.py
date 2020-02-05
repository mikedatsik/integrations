# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import copy
from Qt import QtCore, QtWidgets
from ftrack_connect_pipeline import client, constants
from ftrack_connect_pipeline_qt.ui.widget import header, host_selector
from ftrack_connect_pipeline_qt.client.widgets import factory
from ftrack_connect_pipeline_qt import constants as qt_constants


class QtHostConnection(client.HostConnection):

    def __init__(self, event_manager, host_data):
        super(QtHostConnection, self).__init__(event_manager, host_data)


class QtClient(client.Client, QtWidgets.QWidget):
    '''
    Base QT client widget class.
    '''

    ui = [constants.UI, qt_constants.UI]
    host_connection = None
    schema = None
    definition = None

    def __init__(self, event_manager,parent=None):
        '''Initialise with *event_manager* , and optional *ui* List and
        *parent* widget'''
        QtWidgets.QWidget.__init__(self, parent=parent)
        client.Client.__init__(self, event_manager)
        self.widget_factory = factory.WidgetFactory(
            event_manager,
            self.ui
        )
        self.pre_build()
        self.build()
        self.post_build()
        self.add_hosts(self.discover_hosts())

    def add_hosts(self, hosts):
        for host in hosts:
            if host in self.hosts:
                continue
            self._host_list.append(host)

    def _host_discovered(self, event):
        '''callback, adds new hosts connection from the given *event* to the
        host_selector'''
        # current_hosts = copy.deepcopy(self.hosts)
        super(QtClient, self)._host_discovered(event)
        self.host_selector.add_hosts(self.hosts)

    def pre_build(self):
        '''Prepare general layout.'''
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

    def build(self):
        '''Build widgets and parent them.'''
        self.header = header.Header(self.session)
        self.layout().addWidget(self.header)

        self.host_selector = host_selector.HostSelector()
        self.layout().addWidget(self.host_selector)

        self.scroll = QtWidgets.QScrollArea()

        self.layout().addWidget(self.scroll)

        self.run_button = QtWidgets.QPushButton('Run')
        self.layout().addWidget(self.run_button)

    def post_build(self):
        '''Post Build ui method for events connections.'''
        self.host_selector.definition_changed.connect(self._definition_changed)
        self.run_button.clicked.connect(self._on_run)

        self.widget_factory.widget_status_updated.connect(
            self._on_widget_status_updated
        )

    def _definition_changed(self, host_connection, schema, definition):
        ''' Triggered when definition_changed is called from the host_selector.
        Generates the widgets interface from the given *host_connection*,
        *schema* and *definition*'''

        self.logger.info('Definition changed !!!')

        if not host_connection:
            return

        self.logger.info('connection {}'.format(host_connection))
        self.host_connection = host_connection

        self.schema = schema
        self.definition = definition

        self.widget_factory.set_host_definitions(
            self.host_connection.host_definitions
        )

        self._current_def = self.widget_factory.create_widget(
            definition['name'],
            schema,
            self.definition,
            host_connection=self.host_connection
        )
        self.scroll.setWidget(self._current_def)

    def _on_widget_status_updated(self, data):
        ''' Triggered when a widget generated by the fabric has emit the
        widget_status_update signal.
        Sets the status from the given *data* to the header
        '''
        status, message = data
        self.header.setMessage(message, status)

    def _on_run(self):
        '''Function called when click the run button'''
        serialized_data= self._current_def.to_json_object()
        self.host_connection.run(serialized_data)