# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_framework_core import client
from ftrack_framework_core import constants as core_constants


class LogViewerClient(client.Client):
    '''
    Log Viewer Client Base Class
    '''

    definition_filters = [core_constants.LOG_VIEWER]
    '''Use only definitions that matches the definition_filters'''

    def __init__(self, event_manager):
        '''
        Initialise LogViewerClient with instance of
        :class:`~ftrack_framework_core.event.EventManager`
        '''
        super(LogViewerClient, self).__init__(event_manager)