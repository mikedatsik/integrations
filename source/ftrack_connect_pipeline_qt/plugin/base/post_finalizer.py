# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline.constants import plugin
from ftrack_connect_pipeline_qt.plugin import BasePluginWidget


class BasePostFinalizerWidget(BasePluginWidget):
    plugin_type = plugin._PLUGIN_POST_FINALIZER_TYPE
