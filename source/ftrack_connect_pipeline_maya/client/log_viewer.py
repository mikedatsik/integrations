# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from Qt import QtWidgets, QtCore

from ftrack_connect_pipeline_qt.client import log_viewer

from ftrack_connect_pipeline_maya.utils.custom_commands import get_maya_window


class MayaLogViewerDialog(log_viewer.QtLogViewerClient):
    '''Maya log viewer dialog'''

    def __init__(self, event_manager, unused_asset_list_model, parent=None):
        super(MayaLogViewerDialog, self).__init__(
            event_manager, parent=(parent or get_maya_window())
        )

        # Make sure we stays on top of Maya
        self.setWindowFlags(QtCore.Qt.Tool)
