# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline_qt.plugin import base


class PublisherOutputWidget(base.BaseOutputWidget):
    plugin_type = constants.PLUGIN_PUBLISHER_OUTPUT_TYPE
