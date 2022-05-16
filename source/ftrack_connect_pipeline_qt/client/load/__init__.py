#! /usr/bin/env python
# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import copy
import json
from functools import partial

from Qt import QtCore, QtWidgets

from ftrack_connect_pipeline.client import constants
from ftrack_connect_pipeline.utils import ftrack_context_id, str_version

from ftrack_connect_pipeline import constants as core_constants
from ftrack_connect_pipeline.client.loader import LoaderClient

from ftrack_connect_pipeline_qt import constants as qt_constants
from ftrack_connect_pipeline_qt.ui import theme
from ftrack_connect_pipeline_qt.ui.utility.widget.dialog import ModalDialog
from ftrack_connect_pipeline_qt.ui.utility.widget import (
    dialog,
    header,
    definition_selector,
    line,
    tab,
)
from ftrack_connect_pipeline_qt.ui.utility.widget.context_selector import (
    ContextSelector,
)
from ftrack_connect_pipeline_qt.utils import clear_layout

from ftrack_connect_pipeline_qt.client.asset_manager import (
    QtAssetManagerClient,
)
from ftrack_connect_pipeline_qt.ui.assembler.assembler import (
    AssemblerDependenciesWidget,
    AssemblerBrowserWidget,
)


class QtLoaderClient(LoaderClient):
    '''
    Loader client class, as assembler is based on
    '''

    def __init__(self, event_manager):
        super(QtLoaderClient, self).__init__(event_manager)
        self.logger.debug('start qt loader')


class QtAssemblerClient(QtLoaderClient, dialog.Dialog):
    '''Compound client dialog containing the assembler based on loader with the asset manager docked'''

    ui_types = [constants.UI_TYPE, qt_constants.UI_TYPE]

    contextChanged = QtCore.Signal(object)  # Client context has changed

    _shown = False

    assembler_match_extension = (
        False  # Have assembler match on file extension (relaxed)
    )

    asset_fetch_chunk_size = (
        10  # Amount of assets to fetch at a time within the browser
    )

    ASSEMBLE_MODE_DEPENDENCIES = 0
    ASSEMBLE_MODE_BROWSE = 1
    assemble_mode = -1
    ''' The mode assembler is in - resolve dependencies or manual browse '''

    hard_refresh = True
    ''' Flag telling assembler that next refresh should include dependency resolve '''

    def __init__(self, event_manager, modes, asset_list_model, parent=None):

        dialog.Dialog.__init__(self, parent=parent)
        QtLoaderClient.__init__(self, event_manager)

        self.logger.debug('start qt assembler')

        self.modes = modes
        self._asset_list_model = asset_list_model
        self._shown = False

        if self.getTheme():
            self.setTheme(self.getTheme())
            if self.getThemeBackgroundStyle():
                self.setProperty('background', self.getThemeBackgroundStyle())
        self.setProperty('docked', 'true' if self.is_docked() else 'false')
        self.setObjectName(
            '{}_{}'.format(
                qt_constants.MAIN_FRAMEWORK_WIDGET, self.__class__.__name__
            )
        )

        self.scroll = None

        self.pre_build()
        self.build()
        self.post_build()

        self.set_context_id(self.context_id or ftrack_context_id())
        if self.context_id:
            self.add_hosts(self.discover_hosts())

        self.setWindowTitle('ftrack Connect Assembler')
        self.resize(1000, 500)

    def getTheme(self):
        '''Return the client theme, return None to disable themes. Can be overridden by child.'''
        return 'dark'

    def setTheme(self, selected_theme):
        theme.applyTheme(self, selected_theme, 'plastique')

    def getThemeBackgroundStyle(self):
        return 'ftrack'

    def is_docked(self):
        return False

    def pre_build(self):
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.layout().setContentsMargins(16, 16, 16, 16)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(16, 16, 16, 16)
        self.header = header.Header(self.session, parent=self.parent())
        self.header.setMinimumHeight(50)
        # Create and add the asset manager client
        self.asset_manager = QtAssetManagerClient(
            self.event_manager,
            self._asset_list_model,
            is_assembler=True,
            parent=self.parent(),
        )

    def build_left_widget(self):
        '''Left split pane content'''

        self._left_widget = QtWidgets.QWidget()
        self._left_widget.setLayout(QtWidgets.QVBoxLayout())
        self._left_widget.layout().setContentsMargins(0, 0, 0, 0)
        self._left_widget.layout().setSpacing(0)

        self._left_widget.layout().addWidget(self.header)

        self._left_widget.layout().addWidget(
            line.Line(style='solid', parent=self.parent())
        )

        self.progress_widget = (
            factory.AssemblerWidgetFactory.create_progress_widget(
                parent=self.parent()
            )
        )
        self.header.content_container.layout().addWidget(
            self.progress_widget.widget
        )

        # Have definition selector but invisible unless there are multiple hosts
        self.host_and_definition_selector = (
            definition_selector.AssemblerDefinitionSelector(
                parent=self.parent()
            )
        )
        self.host_and_definition_selector.refreshed.connect(
            partial(self.refresh, True)
        )
        self._left_widget.layout().addWidget(self.host_and_definition_selector)

        # Have a tabbed widget for the different import modes

        self._tab_widget = AssemblerTabWidget()
        self._tab_widget.setFocusPolicy(QtCore.Qt.NoFocus)

        # Build dynamically to save resources if lengthy asset lists

        self._dep_widget = QtWidgets.QWidget()
        self._dep_widget.setLayout(QtWidgets.QVBoxLayout())
        self._dep_widget.layout().setContentsMargins(0, 0, 0, 0)
        self._dep_widget.layout().setSpacing(0)

        self._tab_widget.addTab(self._dep_widget, 'Suggestions')

        self._browse_widget = QtWidgets.QWidget()
        self._browse_widget.setLayout(QtWidgets.QVBoxLayout())
        self._browse_widget.layout().setContentsMargins(0, 0, 0, 0)
        self._browse_widget.layout().setSpacing(0)

        self._tab_widget.addTab(self._browse_widget, 'Browse')

        self._left_widget.layout().addWidget(self._tab_widget)

        # Set initial import mode, do not rebuild it as AM will trig it when it
        # has fetched assets
        self._tab_widget.setCurrentIndex(self.ASSEMBLE_MODE_DEPENDENCIES)
        self.set_assemble_mode(self.ASSEMBLE_MODE_DEPENDENCIES)

        button_widget = QtWidgets.QWidget()
        button_widget.setLayout(QtWidgets.QHBoxLayout())
        button_widget.layout().setContentsMargins(2, 4, 8, 0)
        button_widget.layout().addStretch()
        self.run_button_no_load = AddRunButton('ADD TO SCENE')
        button_widget.layout().addWidget(self.run_button_no_load)
        self.run_button = LoadRunButton('LOAD INTO SCENE')
        self.run_button.setFocus()
        button_widget.layout().addWidget(self.run_button)
        self._left_widget.layout().addWidget(button_widget)

        self._asset_selection_updated()

        return self._left_widget

    def build_right_widget(self):
        '''Right split pane content'''

        self._right_widget = QtWidgets.QWidget()
        self._right_widget.setLayout(QtWidgets.QVBoxLayout())
        self._right_widget.layout().setContentsMargins(0, 0, 0, 0)
        self._right_widget.layout().setSpacing(0)

        self.context_selector = ContextSelector(
            self.session, parent=self.parent()
        )
        self._right_widget.layout().addWidget(
            self.context_selector, QtCore.Qt.AlignTop
        )

        self._right_widget.layout().addWidget(
            line.Line(style='solid', parent=self.parent())
        )

        self._right_widget.layout().addWidget(self.asset_manager, 100)

        return self._right_widget

    def build(self):
        '''Build assembler widget.'''

        # Create a splitter and add to client
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.build_left_widget())
        self.splitter.addWidget(self.build_right_widget())
        self.splitter.setHandleWidth(1)
        self.splitter.setSizes([600, 200])

        self.layout().addWidget(self.splitter, 100)

    def post_build(self):
        self.context_selector.entityChanged.connect(
            self._on_context_selector_context_changed
        )
        self.host_and_definition_selector.hostChanged.connect(self.change_host)
        self.host_and_definition_selector.definitionChanged.connect(
            self.change_definition
        )

        if self.event_manager.mode == constants.LOCAL_EVENT_MODE:
            self.host_and_definition_selector.host_widget.hide()

        self.context_selector.changeContextClicked.connect(
            self._launch_context_selector
        )
        self.host_and_definition_selector.hostsDiscovered.connect(
            self._on_hosts_discovered
        )
        self._tab_widget.currentChanged.connect(self._on_tab_changed)
        self.asset_manager.assetsDiscovered.connect(self._assets_discovered)
        self.run_button.setFocus()
        self.run_button_no_load.clicked.connect(
            partial(self.run, "init_nodes")
        )
        self.run_button.clicked.connect(partial(self.run, "init_and_load"))

    def _on_context_selector_context_changed(self, context_entity):
        '''Updates the option dictionary with provided *context* when
        entityChanged of context_selector event is triggered'''

        self.set_context_id(context_entity['id'])

        # Reset definition selector and clear client
        self.host_and_definition_selector.clear_definitions()
        self.host_and_definition_selector.populate_definitions()
        self._clear_widget()

    def set_context_id(self, context_id):
        '''Set the context id for this client'''
        if context_id and context_id != self.context_id:
            discover_hosts = self.context_id is None
            self.change_context(context_id)
            if discover_hosts:
                self.add_hosts(self.discover_hosts())

    def _on_hosts_discovered(self, host_connections):
        self.host_and_definition_selector.setVisible(len(host_connections) > 1)

    def change_context(self, context_id):
        """
        Assign the given *context_id* as the current :obj:`context_id` and to the
        :attr:`~ftrack_connect_pipeline.client.HostConnection.context_id` emit
        on_context_change signal.
        """
        super(QtAssemblerClient, self).change_context(context_id)
        self.context_selector.set_context_id(self.context_id)
        self.contextChanged.emit(context_id)

    def add_hosts(self, host_connections):
        '''
        Adds the given *host_connections*

        *host_connections* : list of
        :class:`~ftrack_connect_pipeline.client.HostConnection`
        '''
        for host_connection in host_connections:
            if host_connection in self.host_connections:
                continue
            if self.context_id:
                host_connection.context_id = self.context_id
            self._host_connections.append(host_connection)

    def _host_discovered(self, event):
        '''
        Callback, add the :class:`~ftrack_connect_pipeline.client.HostConnection`
        of the new discovered :class:`~ftrack_connect_pipeline.host.HOST` from
        the given *event*.

        *event*: :class:`ftrack_api.event.base.Event`
        '''
        super(QtAssemblerClient, self)._host_discovered(event)
        if self.definition_filter:
            self.host_and_definition_selector.definition_title_filter = (
                self.definition_filter
            )
        if self.definition_extensions_filter:
            self.host_and_definition_selector.definition_extensions_filter = (
                self.definition_extensions_filter
            )
        self.host_and_definition_selector.add_hosts(self.host_connections)

    def _clear_widget(self):
        if self.scroll and self.scroll.widget():
            self.scroll.widget().deleteLater()

    def change_host(self, host_connection):
        self._clear_widget()
        super(QtAssemblerClient, self).change_host(host_connection)
        self.context_selector.host_changed(host_connection)
        # Feed the host to the asset manager
        self.asset_manager.change_host(host_connection)

    def _assets_discovered(self):
        '''The assets in AM has been discovered, refresh at our end.'''
        self.refresh()

    def _on_tab_changed(self, index):
        self.set_assemble_mode(index)
        self.refresh(True)

    def set_assemble_mode(self, assemble_mode):
        if assemble_mode != self.assemble_mode:
            self.assemble_mode = assemble_mode
            active_tab_widget = (
                self._dep_widget
                if self.assemble_mode == self.ASSEMBLE_MODE_DEPENDENCIES
                else self._browse_widget
            )
            inactive_tab_widget = (
                self._dep_widget
                if self.assemble_mode != self.ASSEMBLE_MODE_DEPENDENCIES
                else self._browse_widget
            )
            # Clear the other tab
            clear_layout(inactive_tab_widget.layout())
            # Create tab widget
            self._assembler_widget = (
                AssemblerDependenciesWidget(self)
                if self.assemble_mode == self.ASSEMBLE_MODE_DEPENDENCIES
                else AssemblerBrowserWidget(self)
            )
            active_tab_widget.layout().addWidget(self._assembler_widget)
            self._assembler_widget.listWidgetCreated.connect(
                self._on_component_list_created
            )

    def _on_component_list_created(self, component_list):
        component_list.selectionUpdated.connect(self._asset_selection_updated)

    def refresh(self, force_hard_refresh=False):
        super(QtLoaderClient, self).refresh()
        if force_hard_refresh:
            self.hard_refresh = True
        if self.hard_refresh:
            self._assembler_widget.rebuild()
            self.hard_refresh = False

    def _asset_selection_updated(self, asset_selection=None):
        loadable_count = self._assembler_widget.loadable_count
        s = ''
        if loadable_count > 0:
            if len(asset_selection or []) > 0:
                s = ' {} ASSET{}'.format(
                    len(asset_selection),
                    'S' if len(asset_selection) > 1 else '',
                )
            else:
                s = ' ALL ASSETS'
        self.run_button_no_load.setText('ADD{} TO SCENE'.format(s))
        self.run_button_no_load.setEnabled(loadable_count > 0)
        self.run_button.setText('LOAD{} INTO SCENE'.format(s))
        self.run_button.setEnabled(loadable_count > 0)

    def reset(self):
        '''Assembler is shown again after being hidden.'''
        super(QtAssemblerClient, self).reset()
        self.asset_manager.asset_manager_widget.rebuild.emit()
        self._assembler_widget.reset()
        self.progress_widget.hide_widget()
        self.progress_widget.clear_components()

    def setup_widget_factory(self, widget_factory, definition, context_id):
        widget_factory.set_definition(definition)
        widget_factory.set_context(context_id, definition['asset_type'])
        widget_factory.host_connection = self._host_connection
        widget_factory.set_definition_type(definition['type'])

    def _on_run_plugin(self, plugin_data, method):
        '''Function called to run one single plugin *plugin_data* with the
        plugin information and the *method* to be run has to be passed'''
        self.run_plugin(plugin_data, method, self.engine_type)

    def _open_assembler(self):
        '''Open the assembler and close client if dialog'''
        if not self.is_docked():
            self.hide()
        self.host_connection.launch_widget(core_constants.ASSEMBLER)

    def run(self, method=None):
        '''(Override) Function called when click the run button.'''
        # Load batch of components, any selected
        component_widgets = self._assembler_widget.component_list.selection(
            as_widgets=True
        )
        if len(component_widgets) == 0:
            dlg = ModalDialog(
                self.parent(),
                title='ftrack Assembler',
                question='Load all?',
                prompt=True,
            )
            if dlg.exec_():
                # Select and use all loadable - having definition
                component_widgets = (
                    self._assembler_widget.component_list.get_loadable()
                )
        if len(component_widgets) > 0:
            # Each component contains a definition ready to run and a factory,
            # run them one by one. Start by preparing progress widget
            self.progress_widget.prepare_add_components()
            self.progress_widget.set_status(
                constants.RUNNING_STATUS, 'Initializing...'
            )
            for component_widget in component_widgets:
                component = self._assembler_widget.component_list.model.data(
                    component_widget.index
                )[0]
                factory = component_widget.factory
                factory.progress_widget = (
                    self.progress_widget
                )  # Have factory update main progress widget
                self.progress_widget.add_version(component)
                factory.build_progress_ui(component)
            self.progress_widget.components_added()

            self.progress_widget.show_widget()
            failed = 0
            for component_widget in component_widgets:
                # Prepare progress widget
                component = self._assembler_widget.component_list.model.data(
                    component_widget.index
                )[0]
                self.progress_widget.set_status(
                    constants.RUNNING_STATUS,
                    'Loading {} / {}...'.format(
                        str_version(component['version']), component['name']
                    ),
                )
                definition = component_widget.definition
                factory = component_widget.factory
                factory.listen_widget_updates()

                engine_type = definition['_config']['engine_type']

                # Set method to importer plugins
                if method:
                    for component in definition['components']:
                        for stage in component['stages']:
                            if stage['type'] != 'importer':
                                continue
                            for plugin in stage['plugins']:
                                if plugin['type'] != 'importer':
                                    continue
                                plugin['default_method'] = method

                self.run_definition(definition, engine_type)
                # Did it go well?
                if factory.has_error:
                    failed += 1
                component_widget.factory.end_widget_updates()

            succeeded = len(component_widgets) - failed
            if succeeded > 0:
                if failed == 0:
                    self.progress_widget.set_status(
                        constants.SUCCESS_STATUS,
                        'Successfully {} {}/{} asset{}!'.format(
                            'loaded' if method == 'run' else 'tracked',
                            succeeded,
                            len(component_widgets),
                            's' if len(component_widgets) > 1 else '',
                        ),
                    )
                else:
                    self.progress_widget.set_status(
                        constants.WARNING_STATUS,
                        'Successfully {} {}/{} asset{}, {} failed - check logs for more information!'.format(
                            'loaded' if method == 'run' else 'tracked',
                            succeeded,
                            len(component_widgets),
                            's' if len(component_widgets) > 1 else '',
                            failed,
                        ),
                    )
                self.asset_manager.asset_manager_widget.rebuild.emit()
            else:
                self.progress_widget.set_status(
                    constants.ERROR_STATUS,
                    'Could not {} asset{} - check logs for more information!'.format(
                        'loaded' if method == 'run' else 'tracked',
                        's' if len(component_widgets) > 1 else '',
                    ),
                )

    def reset(self):
        '''Reset a client that has become visible after being hidden.'''
        self.set_context_id(ftrack_context_id())
        self.host_and_definition_selector.refresh()

    def conditional_rebuild(self):
        if self._shown:
            # Refresh when re-opened
            self.host_and_definition_selector.refresh()
        self._shown = True

    def _launch_context_selector(self):
        '''Close client (if not docked) and open entity browser.'''
        if not self.is_docked():
            self.hide()
        self.host_connection.launch_widget(core_constants.CHANGE_CONTEXT)

    def show(self):
        if self._shown:
            # Widget has been shown before, reload dependencies
            self.reset()
        super(QtAssemblerClient, self).show()
        self._shown = True


class AssemblerTabWidget(tab.TabWidget):
    def __init__(self, parent=None):
        super(AssemblerTabWidget, self).__init__(parent=parent)


class AddRunButton(QtWidgets.QPushButton):
    def __init__(self, label, parent=None):
        super(AddRunButton, self).__init__(label, parent=parent)
        self.setMaximumHeight(32)
        self.setMinimumHeight(32)


class LoadRunButton(QtWidgets.QPushButton):
    def __init__(self, label, parent=None):
        super(LoadRunButton, self).__init__(label, parent=parent)
        self.setMaximumHeight(32)
        self.setMinimumHeight(32)
