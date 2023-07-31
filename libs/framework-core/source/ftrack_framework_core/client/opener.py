# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_framework_core import client
from ftrack_framework_core import constants


class OpenerClient(client.Client):
    '''
    Opener Client Base Class
    '''

    definition_filters = [constants.OPENER]

    def __init__(self, event_manager):
        '''
        Initialise OpenerClient with instance of
        :class:`~ftrack_framework_core.event.EventManager`
        '''
        super(OpenerClient, self).__init__(event_manager)