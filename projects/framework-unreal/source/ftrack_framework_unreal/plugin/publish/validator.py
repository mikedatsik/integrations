# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack

from ftrack_framework_core import plugin

from ftrack_framework_qt import plugin as pluginWidget

from ftrack_framework_unreal.plugin import (
    UnrealBasePlugin,
    UnrealBasePluginWidget,
)


class UnrealPublisherValidatorPlugin(
    plugin.PublisherValidatorPlugin, UnrealBasePlugin
):
    '''Class representing a Validator Plugin

    .. note::

        _required_output a Boolean
    '''


class UnrealPublisherValidatorPluginWidget(
    pluginWidget.PublisherValidatorPluginWidget, UnrealBasePluginWidget
):
    '''Class representing a Validator widget

    .. note::

        _required_output a Boolean
    '''