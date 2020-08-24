# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from Qt import QtWidgets, QtCore, QtGui
from ftrack_connect_pipeline.asset import asset_info

class VersionDelegate(QtWidgets.QItemDelegate):
    change_version = QtCore.Signal(object, object)

    def __init__(self, parent=None):
        super(VersionDelegate, self).__init__(parent=parent)

    def createEditor(self, parent, option, index):

        #Have to initialize the ftrack info again as when quering from the
        # model even if the DATA_ROLE has the FtrackAssetInfo dictionary,
        # it returns a generic diccionary.
        item = asset_info.FtrackAssetInfo(index.model().data(index, index.model().DATA_ROLE))

        #TODO: we have two options: I have added the versions key on the
        # asset_info that if a session is provided it returns you the versions.
        # The other option is call the client to get the ftrack_asset_versions
        # and this publish an event to the host which will run the engine
        # function to query the versions

        versions_collection = item['versions']

        combo = QtWidgets.QComboBox(parent)
        for asset_version in versions_collection:
            combo.addItem(str(asset_version['version']), asset_version['id'])

        return combo

    def setEditorData(self, editor, index):
        editor_data = str(index.model().data(index, QtCore.Qt.EditRole))
        idx = editor.findText(editor_data)
        editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        if not index.isValid():
            return False
        self.change_version.emit(index, editor.itemData(editor.currentIndex()))
        #TODO: if the model doesn't get updated, we should  call the model.set
        # data after changing the version, so the client can tell the widget to
        # set the data after the change_version_callback is called.
        # model.setData(
        #     index, editor.itemData(editor.currentIndex()), QtCore.Qt.EditRole
        # )

