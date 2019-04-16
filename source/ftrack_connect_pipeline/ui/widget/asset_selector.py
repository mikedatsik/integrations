import logging
from qtpy import QtWidgets, QtCore


class AssetComboBox(QtWidgets.QComboBox):
    context_changed = QtCore.Signal(object)

    def __init__(self, session, asset_type, parent=None):
        super(AssetComboBox, self).__init__(parent=parent)
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.setEditable(True)

        self.session = session
        self.asset_type = asset_type
        self.context_changed.connect(self._on_context_changed)

    def _on_context_changed(self, context):
        self.clear()
        assets = self.session.query(
            'select name, versions.task.id , type.id '
            'from Asset where versions.task.id is {} and type.id is {}'.format(
                context['id'], self.asset_type['id'])
        ).all()
        self.logger.info('assets: {}'.format(assets))
        for asset in assets:
            self.addItem(asset['name'], asset['id'])


class AssetSelector(QtWidgets.QWidget):

    def __init__(self, session, asset_type, parent=None):
        super(AssetSelector, self).__init__(parent=parent)
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)
        self.session = session

        self.asset_type = self.session.query(
            'AssetType where short is "{}"'.format(asset_type)
        ).one()

        self.logger.info('asset type:{}'.format(self.asset_type))

        self.asset_combobox = AssetComboBox(self.session, self.asset_type)
        self.layout().addWidget(self.asset_combobox)

    def set_context(self, context):
        self.asset_combobox.context_changed.emit(context)
