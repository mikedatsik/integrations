# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_framework_core import plugin
from ftrack_framework_qt import plugin as pluginWidget
from ftrack_framework_maya.plugin import (
    MayaBasePlugin,
    MayaBasePluginWidget,
)


class MayaPublisherCollectorPlugin(
    plugin.PublisherCollectorPlugin, MayaBasePlugin
):
    '''Class representing a Collector Plugin

    .. note::

        _required_output a List
    '''


class MayaPublisherCollectorPluginWidget(
    pluginWidget.PublisherCollectorPluginWidget, MayaBasePluginWidget
):
    '''Class representing a Collector Widget

    .. note::

        _required_output a List
    '''