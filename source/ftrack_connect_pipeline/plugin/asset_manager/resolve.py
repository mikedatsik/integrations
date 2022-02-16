# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline.asset import FtrackAssetBase
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline.plugin import base


class AssetManagerResolvePlugin(base.BaseActionPlugin):
    '''
    Class representing a Asset Manager Resolve Plugin Inherits from
    :class:`~ftrack_connect_pipeline.plugin.base.BaseActionPlugin`
    '''

    return_type = dict
    '''Type of object that should be returned'''
    plugin_type = constants.PLUGIN_AM_RESOLVE_TYPE
    '''Plugin type of the current plugin'''
    _required_output = []

    def __init__(self, session):
        '''
        Initialise AssetManagerActionPlugin with instance of
        :class:`ftrack_api.session.Session`
        '''
        super(AssetManagerResolvePlugin, self).__init__(session)
