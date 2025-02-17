# :coding: utf-8
# :copyright: Copyright (c) 2024 ftrack

import threading
from functools import wraps

import maya.cmds as cmds
import maya.utils as maya_utils
import maya.OpenMayaUI as omui

try:
    from PySide6 import QtWidgets, QtCore
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtCore
    from shiboken2 import wrapInstance


# Dock widget in Maya
def dock_maya_right(widget):
    '''Dock *widget* to the right side of Maya.'''
    widget.show()
    # TODO: To provide docking functionality, comment line above and uncomment code below
    # dock_control_name = widget.windowTitle() + '_dock'
    # if cmds.workspaceControl(dock_control_name, q=True, exists=True):
    #     cmds.deleteUI(dock_control_name)
    #
    # main_control = cmds.workspaceControl(
    #     dock_control_name,
    #     ttc=["AttributeEditor", -1],
    #     iw=300,
    #     mw=False,
    #     wp='preferred',
    #     hp='preferred',
    #     retain=False,
    #     label=widget.windowTitle(),
    # )
    #
    # dock_control_ptr = omui.MQtUtil.findControl(dock_control_name)
    # dock_control_widget = wrapInstance(
    #     int(dock_control_ptr), QtWidgets.QWidget
    # )
    # dock_control_widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    #
    # dock_control_widget.layout().addWidget(widget)
    #
    # widget.show()
    # widget.setFocus()
    #
    # cmds.evalDeferred(
    #     lambda *args: cmds.workspaceControl(main_control, e=True, rs=True)
    # )


def run_in_main_thread(f):
    '''Make sure a function runs in the main Maya thread.'''

    @wraps(f)
    def decorated(*args, **kwargs):
        if threading.currentThread().name != 'MainThread':
            return maya_utils.executeInMainThreadWithResult(f, *args, **kwargs)
        else:
            return f(*args, **kwargs)

    return decorated
