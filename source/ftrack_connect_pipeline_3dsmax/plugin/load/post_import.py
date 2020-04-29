# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
from ftrack_connect_pipeline_qt import plugin as pluginWidget
from ftrack_connect_pipeline_3dsmax.plugin import (
    BaseMaxPlugin, BaseMaxPluginWidget
)


class LoaderPostImportMaxPlugin(plugin.LoaderPostImportPlugin, BaseMaxPlugin):
    ''' Class representing a Collector Plugin

    .. note::

        _required_output a List
    '''


class LoaderPostImportMaxWidget(
    pluginWidget.LoaderPostImportWidget, BaseMaxPluginWidget
):
    ''' Class representing a Collector Widget

    .. note::

        _required_output a List
    '''
