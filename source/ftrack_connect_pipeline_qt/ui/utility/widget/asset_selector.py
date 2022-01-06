# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack
import logging

from Qt import QtWidgets, QtCore, QtGui

from ftrack_connect_pipeline_qt.utils import BaseThread
from ftrack_connect_pipeline_qt.ui.utility.widget.thumbnail import AssetVersion
from ftrack_connect_pipeline_qt.utils import set_property

class AssetListItem(QtWidgets.QWidget):
    ''' Widget representing an asset within the '''
    def __init__(self, asset, session):
        super(AssetListItem, self).__init__()
    
        self.asset = asset
        self.session = session
        self.pre_build()
        self.build()
        self.post_build()
    
    def pre_build(self):
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(3)
    
    def build(self):
        self.thumbnail_widget = AssetVersion(self.session)
        self.thumbnail_widget.setScaledContents(True)
        self.thumbnail_widget.setMinimumSize(46, 32)
        self.thumbnail_widget.setMaximumSize(46, 32)
        self.layout().addWidget(self.thumbnail_widget)
        self.thumbnail_widget.load(self.asset['latest_version']['id'])

        self.asset_name = QtWidgets.QLabel(self.asset['name'])
        self.layout().addWidget(self.asset_name )

        self.create_label = QtWidgets.QLabel('- create')
        self.create_label.setObjectName("gray")
        self.layout().addWidget(self.create_label)

        self.version_label = QtWidgets.QLabel('Version {}'.format(
            self.asset['latest_version']['version']+1))
        self.version_label.setObjectName("purple")
        self.layout().addWidget(self.version_label)

        self.layout().addStretch()
        
    def post_build(self):
        pass
        
class AssetList(QtWidgets.QListWidget):
    ''' Widget presenting list of existing assets '''
    assets_query_done = QtCore.Signal()
    assets_added = QtCore.Signal()

    def __init__(self, session, parent=None):
        super(AssetList, self).__init__(parent=parent)
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self.session = session
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSpacing(1)
        self.assets = []

    def _query_assets_from_context(self, context_id, asset_type_name):
        ''' (Run in background thread) Fetch assets from current context '''
        asset_type_entity = self.session.query(
            'select name from AssetType where short is "{}"'.format(asset_type_name)
        ).first()
        assets = self.session.query(
            'select name, versions.task.id , type.id, id, latest_version,'
            'latest_version.version '
            'from Asset where versions.task.id is {} and type.id is {}'.format(
                context_id, asset_type_entity['id'])
        ).all()
        return assets

    def _store_assets(self, assets):
        ''' Async, store assets and add through signal'''
        self.assets = assets
        # Add data placeholder for new asset input
        self.assets_query_done.emit()
        
    def refresh(self):
        ''' Add fetched assets to list '''
        self.clear()
        for asset_entity in self.assets:
            widget = AssetListItem(
                asset_entity,
                self.session,
            )
            list_item = QtWidgets.QListWidgetItem(self)
            list_item.setSizeHint(QtCore.QSize(widget.sizeHint().width(), widget.sizeHint().height()+5))
            self.addItem(list_item)
            self.setItemWidget(list_item, widget)
        self.assets_added.emit()

    def on_context_changed(self, context_id, asset_type_name):
        self.clear()

        thread = BaseThread(
            name='get_assets_thread',
            target=self._query_assets_from_context,
            callback=self._store_assets,
            target_args=(context_id, asset_type_name)
        )
        thread.start()

class NewAssetNameInput(QtWidgets.QLineEdit):
    ''' Widget holding new asset name input '''
    clicked = QtCore.Signal()
    def __init__(self):
        super(NewAssetNameInput, self).__init__()

    def mousePressEvent(self, event):
        '''Override mouse press to emit signal'''
        self.clicked.emit()

class NewAssetInput(QtWidgets.QFrame):
    ''' Widget holding new asset inputs '''
    clicked = QtCore.Signal()
    def __init__(self, validator, placeholder_name):
        super(NewAssetInput, self).__init__()

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(1)

        self.button = QtWidgets.QPushButton('NEW')
        self.button.setFixedSize(46, 32)
        self.button.setMaximumSize(46, 32)
        self.button.clicked.connect(self.input_clicked)

        self.layout().addWidget(self.button)

        self.name = NewAssetNameInput()
        self.name.setPlaceholderText(placeholder_name)
        self.name.setValidator(validator)
        self.name.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum
        )
        self.name.clicked.connect(self.input_clicked)
        self.layout().addWidget(self.name, 1000)

        self.version_label = QtWidgets.QLabel('- Version 1')
        self.version_label.setObjectName("purple")
        self.layout().addWidget(self.version_label)

    def mousePressEvent(self, event):
        '''Override mouse press to emit signal.'''
        self.input_clicked()

    def input_clicked(self):
        self.clicked.emit()

class AssetListAndInput(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AssetListAndInput, self).__init__(parent=parent)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def add_asset_list(self, asset_list):
        self.asset_list = asset_list
        self.layout().addWidget(asset_list)

    def resizeEvent(self, event):
        self._size_changed()

    def _size_changed(self):
        self.asset_list.setFixedSize(self.size().width()-1,
            self.asset_list.sizeHintForRow(0) * self.asset_list.count() +
            2 * self.asset_list.frameWidth())

class AssetSelector(QtWidgets.QWidget):
    valid_asset_name = QtCore.QRegExp('[A-Za-z0-9_]+')
    asset_changed = QtCore.Signal(object, object, object)
    update_widget = QtCore.Signal(object)

    def __init__(self, session, is_loader=False, parent=None):
        super(AssetSelector, self).__init__(parent=parent)
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self.is_loader = is_loader
        self.session = session

        self.validator = QtGui.QRegExpValidator(self.valid_asset_name)
        self.placeholder_name = "Asset Name..."

        self.pre_build()
        self.build()
        self.post_build()

    def pre_build(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

    def build(self):
        self.select_existing_label = QtWidgets.QLabel()
        self.select_existing_label.setObjectName('gray')
        self.select_existing_label.setWordWrap(True)
        self.layout().addWidget(self.select_existing_label)

        self.list_and_input = AssetListAndInput()

        self.asset_list = AssetList(self.session)
        self.list_and_input.add_asset_list(self.asset_list)

        # Create new asset
        self.new_asset_input = NewAssetInput(self.validator, self.placeholder_name)
        self.list_and_input.layout().addWidget(self.new_asset_input)

        self.layout().addWidget(self.list_and_input)

    def post_build(self):
        self.asset_list.itemChanged.connect(
            self._current_asset_changed
        )
        self.asset_list.assets_query_done.connect(self._refresh)
        self.asset_list.assets_added.connect(self._pre_select_asset)
        self.asset_list.itemActivated.connect(self._list_selection_updated)
        self.asset_list.itemSelectionChanged.connect(self._list_selection_updated)
        self.new_asset_input.clicked.connect(self._update_widget)
        self.new_asset_input.name.textChanged.connect(self._new_asset_changed)
        self.update_widget.connect(self._update_widget)

    def _refresh(self):
        ''' Add assets queried in separate thread to list.'''
        self.asset_list.refresh()

    def _pre_select_asset(self):
        ''' Assets have been loaded, select most suitable asset to start with '''
        if self.asset_list.count() > 0:
            self.select_existing_label.setText('We found {} assets already '
                'published on this task. Choose which one to version up or create '
                'a new asset'.format(self.asset_list.count()))

            self.asset_list.setCurrentRow(0)
            self.select_existing_label.show()
            self.asset_list.show()
        else:
            self.select_existing_label.hide()
            self.asset_list.hide()
        self.list_and_input._size_changed()

    def _list_selection_updated(self):
        selected_index = self.asset_list.currentRow()
        if selected_index == -1:
            # Deselected, give focus to new asset input
            self.update_widget.emit(None)
        else:
            self.update_widget.emit(self.asset_list.assets[selected_index])

    def _current_asset_changed(self, item):
        ''' An existing asset has been selected. '''
        selected_index = self.asset_list.currentRow()
        if selected_index > -1:
            # A proper asset were selected
            asset_entity = self.asset_list.assets[selected_index]
            asset_name = asset_entity['name']
            is_valid_name = self.validate_name(asset_name)
            self.asset_changed.emit(asset_name, asset_entity, is_valid_name)
            self.update_widget.emit(asset_entity)
        else:
            # All items de-selected
            self.update_widget.emit(None)

    def _update_widget(self, selected_asset=None):
        ''' Synchronize state of list with new asset input. '''
        self.asset_list.ensurePolished()
        if selected_asset is not None:
            # Bring focus to list, remove focus from new asset input
            set_property(self.new_asset_input, 'status', '')
        else:
            # Deselect all assets in list, bring focus to new asset input
            self.asset_list.setCurrentRow(-1)
            set_property(self.new_asset_input, 'status', 'focused')
        self.new_asset_input.button.setEnabled(selected_asset is not None)

    def set_context(self, context_id, asset_type_name):
        self.logger.debug('setting context to :{}'.format(context_id))
        self.asset_list.on_context_changed(context_id, asset_type_name)
        self.new_asset_input.name.setText(asset_type_name)
        #self.propose_new_asset_placeholder_name(context_id)

    def _get_context_entity(self, context_id):
        context_entity = self.session.query(
            'select name from Context where id is "{}"'.format(context_id)
        ).first()
        return context_entity

    def propose_new_asset_placeholder_name(self, context_id):
        thread = BaseThread(
            name='get_assets_thread',
            target=self._get_context_entity,
            callback=self._set_placeholder_name,
            target_args=[context_id]
        )
        thread.start()

    def _set_placeholder_name(self, context_entity):
        if context_entity.get("name"):
            self.placeholder_name = context_entity.get("name").replace(" ", "_")
        self.new_asset_input.name.setPlaceholderText(self.placeholder_name)

    def _new_asset_changed(self):
        asset_name = self.new_asset_input.name.text()
        is_valid_name = self.validate_name(asset_name)
        self.asset_changed.emit(asset_name, None, is_valid_name)

    def validate_name(self, asset_name):
        is_valid_bool = True
        # Already an asset by that name
        if self.asset_list.assets:
            for asset_entity in self.asset_list.assets:
                if asset_entity['name'].lower() == asset_name.lower():
                    is_valid_bool = False
                    break
        if is_valid_bool and self.validator:
            is_valid = self.validator.validate(asset_name, 0)
            if is_valid[0] != QtGui.QValidator.Acceptable:
                is_valid_bool = False
            else:
                is_valid_bool = True
        if is_valid_bool:
            set_property(self.new_asset_input.name, 'input', '')
        else:
            set_property(self.new_asset_input.name, 'input', 'invalid')
        return is_valid_bool
