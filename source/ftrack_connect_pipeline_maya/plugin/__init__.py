# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack
import maya

from ftrack_connect_pipeline import plugin
from ftrack_connect_pipeline_qt import plugin as pluginWidget
from ftrack_connect_pipeline_maya import constants as maya_constants


class BaseMayaPlugin(plugin.BasePlugin):
    host_type = maya_constants.HOST_TYPE

    def _run(self, event):
        super_fn = super(BaseMayaPlugin, self)._run
        result = maya.utils.executeInMainThreadWithResult(super_fn, event)
        return result


class BaseMayaPluginWidget(BaseMayaPlugin, pluginWidget.BasePluginWidget):
    type = 'widget'
    ui_type = maya_constants.UI_TYPE


from ftrack_connect_pipeline_maya.plugin.load import *
from ftrack_connect_pipeline_maya.plugin.publish import *
from ftrack_connect_pipeline_maya.plugin.asset_manager import *
