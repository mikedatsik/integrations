# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_framework_core.plugin import BasePlugin, BasePluginValidation
from ftrack_framework_core.constants import plugin


class BasePostImporterPluginValidation(BasePluginValidation):
    '''
    Post Import Plugin Validation class inherits from
    :class:`~ftrack_framework_core.plugin.BasePluginValidation`
    '''

    def __init__(
        self, plugin_name, required_output, return_type, return_value
    ):
        super(BasePostImporterPluginValidation, self).__init__(
            plugin_name, required_output, return_type, return_value
        )


class BasePostImporterPlugin(BasePlugin):
    '''
    Base Post Import Plugin Class inherits from
    :class:`~ftrack_framework_core.plugin.BasePlugin`
    '''

    return_type = dict
    '''Required return type'''
    plugin_type = plugin._PLUGIN_POST_IMPORTER_TYPE
    '''Type of the plugin'''
    _required_output = {}
    '''Required return exporters'''

    def __init__(self, session):
        super(BasePostImporterPlugin, self).__init__(session)
        self.validator = BasePostImporterPluginValidation(
            self.plugin_name,
            self._required_output,
            self.return_type,
            self.return_value,
        )

    def run(self, context_data=None, data=None, options=None):
        raise NotImplementedError('Missing run method.')