# :coding: utf-8
# :copyright: Copyright (c) 2024 ftrack
import os
import sys
import logging

try:
    from PySide6 import QtWidgets, QtCore
except ImportError:
    from PySide2 import QtWidgets, QtCore

import ftrack_api

from ftrack_utils.version import get_connect_plugin_version
import ftrack_connect.ui.application
import ftrack_connect.ui.widget.overlay
from ftrack_utils.server import send_usage_event

logger = logging.getLogger('ftrack_connect.plugin.publisher_widget')

cwd = os.path.dirname(__file__)
connect_plugin_path = os.path.abspath(os.path.join(cwd, '..'))

# Read version number from __version__.py
__version__ = get_connect_plugin_version(connect_plugin_path)

python_dependencies = os.path.abspath(
    os.path.join(connect_plugin_path, 'dependencies')
)
sys.path.append(python_dependencies)

from ftrack_connect_publisher_widget.publisher import Publisher


class PublisherBlockingOverlay(
    ftrack_connect.ui.widget.overlay.BlockingOverlay
):
    '''Custom blocking overlay for publisher.'''

    def __init__(self, parent, message=''):
        super(PublisherBlockingOverlay, self).__init__(parent, message=message)
        self.confirmButton = QtWidgets.QPushButton('Ok')
        self.contentLayout.insertWidget(
            3,
            self.confirmButton,
            alignment=QtCore.Qt.AlignmentFlag.AlignCenter,
            stretch=0,
        )
        self.confirmButton.hide()
        self.confirmButton.clicked.connect(self.hide)
        self.content.setMinimumWidth(350)


class PublisherWidget(ftrack_connect.ui.application.ConnectWidget):
    name = 'Publish'

    entityChanged = QtCore.Signal(object)

    def __init__(self, session, parent=None):
        '''Instantiate the publisher widget.'''
        super(PublisherWidget, self).__init__(session, parent=parent)

        logger.debug('Initializing PublisherWidget')

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.publishView = Publisher(self.session)
        layout.addWidget(self.publishView)

        self.blockingOverlay = PublisherBlockingOverlay(self)
        self.blockingOverlay.hide()

        self.busyOverlay = ftrack_connect.ui.widget.overlay.BusyOverlay(self)
        self.busyOverlay.hide()

        self.publishView.publishStarted.connect(self._onPublishStarted)

        self.publishView.publishFinished.connect(self._onPublishFinished)

        self.entityChanged.connect(self._onEntityChanged)

    def _onPublishStarted(self):
        '''Callback for publish started signal.'''
        self.blockingOverlay.hide()
        self.busyOverlay.show()

    def _onPublishFinished(self, success):
        '''Callback for publish finished signal.'''
        self.busyOverlay.hide()
        if success:
            self.blockingOverlay.message = (
                'Publish finished!\n \n'
                'Select another task in ftrack or continue to publish using '
                'current task.'
            )
            self.blockingOverlay.confirmButton.show()
            self.blockingOverlay.show()

            send_usage_event(self.session, 'PUBLISHED-FROM-CONNECT')

    def _onEntityChanged(self):
        '''Callback for entityChanged signal.'''
        self.blockingOverlay.hide()
        self.busyOverlay.hide()

    def clear(self):
        '''Reset the publisher to it's initial state.'''
        self._entity = None
        self.publishView.clear()

    def getName(self):
        '''Return name of widget.'''
        return 'Publish'

    def setEntity(self, entity):
        '''Set the *entity* for the publisher.'''
        self._entity = entity
        self.publishView.setEntity(entity)
        self.entityChanged.emit(entity)

    def start(self, event):
        '''Handle *event*.

        event['data'] should contain:

            * entity - The entity to set on the publisher.

        event['data'] may optionally contain:

            components
                a list of dictionaries with name and path, used to
                automatically populate the list of components.

            thumbnail
                an absolute path to an image file to set as the version's
                thumbnail.

            manageData
                If set, a location which can manage data will be picked.

        Clear state, set the *entity* and request to start the publisher.

        '''
        logger.debug('Starting publisher with event: {0}'.format(event))
        entity = event['data']['entity']

        self.clear()
        self.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)

        # Add any components from event data
        components = event['data'].get('components', [])
        for componentData in components:
            self.publishView.componentsList.addItem(
                {
                    'componentName': componentData.get('name'),
                    'resourceIdentifier': componentData.get('path'),
                }
            )

        # Add thumbnail from event data
        thumbnail = event['data'].get('thumbnail')
        if thumbnail:
            self.publishView.thumbnailDropZone.setThumbnail(thumbnail)

        # More information from event data
        manageData = event['data'].get('manageData')
        if manageData:
            self.publishView.setManageData(True)

        entity = self.session.get('Context', entity.get('entityId'))
        logger.debug('Setting entity: {0}'.format(entity))
        if not entity:
            logger.error('No entity found for id: {0}'.format(entity))
        self.setEntity(entity)
        self.requestApplicationFocus.emit(self)

        self.session.event_hub.publish_reply(
            source_event=event, data={'message': 'Publisher started.'}
        )


def get_version_information(event):
    '''Return version information for ftrack connect plugin.'''
    return [dict(name='ftrack-connect-publisher-widget', version=__version__)]


def register(session, **kw):
    '''Register plugin. Called when used as an plugin.'''
    # Validate that session is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an old or incompatible API and
    # return without doing anything.
    if not isinstance(session, ftrack_api.session.Session):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack_api.Session instance.'.format(session)
        )
        return

    #  Uncomment to register plugin
    plugin = ftrack_connect.ui.application.ConnectWidgetPlugin(PublisherWidget)
    plugin.register(session, priority=20)

    # Enable plugin info in Connect about dialog
    session.event_hub.subscribe(
        'topic=ftrack.connect.plugin.debug-information',
        get_version_information,
        priority=20,
    )
