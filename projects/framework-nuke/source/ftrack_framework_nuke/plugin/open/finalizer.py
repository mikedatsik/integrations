# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_framework_core import plugin
from ftrack_framework_qt import plugin as pluginWidget
from ftrack_framework_nuke.plugin import (
    NukeBasePlugin,
    NukeBasePluginWidget,
)


class NukeOpenerFinalizerPlugin(plugin.OpenerFinalizerPlugin, NukeBasePlugin):
    '''Class representing a Finalizer Plugin

    .. note::

        _required_output is a dictionary containing the 'context_id',
        'asset_name', 'asset_type_name', 'comment' and 'status_id' of the
        current asset
    '''


class NukeOpenerFinalizerPluginWidget(
    pluginWidget.OpenerFinalizerPluginWidget, NukeBasePluginWidget
):
    '''Class representing a Finalizer Widget

    .. note::

        _required_output is a dictionary containing the 'context_id',
        'asset_name', 'asset_type_name', 'comment' and 'status_id' of the
        current asset
    '''