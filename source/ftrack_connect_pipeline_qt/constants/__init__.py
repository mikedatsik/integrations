# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack
from ftrack_connect_pipeline import constants

#: Default ui type for ftrack_connect_pipeline_qt
UI_TYPE = 'qt'
#: Default host type for ftrack_connect_pipeline_qt
HOST_TYPE = constants.HOST_TYPE

#: UI Not set value for UI overrides
NOT_SET = 'widget_not_set'

#: Base name for events
_BASE_ = 'ftrack.pipeline'

MAIN_FRAMEWORK_WIDGET = 'main_framework_widget'

# OPENER_WIDGET = 'opener'
# INFO_WIDGET = 'info'
# TASKS_WIDGET = 'tasks'
# CHANGE_CONTEXT_WIDGET = 'change_context'
# LOADER_WIDGET = 'loader'
# ASSEMBLER_WIDGET = 'assembler'
# SAVE_WIDGET = 'save'
# ASSET_MANAGER_WIDGET = 'asset_manager'
# PUBLISHER_WIDGET = 'publisher'
# LOG_VIEWER_WIDGET = 'log_viewer'
# DOC_WIDGET = 'doc'

# Avoid circular dependencies.
from ftrack_connect_pipeline_qt.constants.icons import *
