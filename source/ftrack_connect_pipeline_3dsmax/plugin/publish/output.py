# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
from ftrack_connect_pipeline_qt import plugin as pluginWidget
from ftrack_connect_pipeline_3dsmax.plugin import (
    BaseMaxPlugin, BaseMaxPluginWidget
)


class PublisherOutputMaxPlugin(plugin.PublisherOutputPlugin, BaseMaxPlugin):
    ''' Class representing an Output Plugin
    .. note::

        _required_output a Dictionary
    '''


class PublisherOutputMaxWidget(
    pluginWidget.PublisherOutputWidget, BaseMaxPluginWidget
):
    ''' Class representing an Output Widget
        .. note::

            _required_output a Dictionary
    '''
