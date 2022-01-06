# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from Qt import QtWidgets, QtCore, QtGui

from ftrack_connect_pipeline_qt.plugin.widgets import BaseOptionsWidget

from ftrack_connect_pipeline_qt.ui.utility.widget.asset_selector import AssetSelector
from ftrack_connect_pipeline_qt.ui.utility.widget import line
from ftrack_connect_pipeline_qt.ui.utility.widget.asset_grid_selector import AssetGridSelector
from ftrack_connect_pipeline_qt.utils import BaseThread


class PublishContextWidget(BaseOptionsWidget):
    ''' Main class to represent a conttext widget on a publish process. '''

    statuses_fetched = QtCore.Signal(object)

    def __init__(
            self, parent=None, session=None, data=None, name=None,
            description=None, options=None, context_id=None, asset_type_name=None
    ):
        '''initialise PublishContextWidget with *parent*, *session*, *data*,
        *name*, *description*, *options* and *context*
        '''

        super(PublishContextWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context_id=context_id,
            asset_type_name=asset_type_name
        )
        self.asset_selector.set_context(context_id, asset_type_name)

    def build(self):
        '''build function widgets.'''
        if self.context_id:
            self.set_option_result(self.context_id, key='context_id')
        self.layout().addLayout(self._build_asset_selector())
        self.statuses_fetched.connect(self.set_statuses)
        self.layout().addWidget(line.Line())
        version_and_comment = QtWidgets.QWidget()
        version_and_comment.setLayout(QtWidgets.QVBoxLayout())
        version_and_comment.layout().addWidget(QtWidgets.QLabel('Version information'))
        version_and_comment.layout().addLayout(self._build_status_selector())
        version_and_comment.layout().addLayout(self._build_comments_input())
        self.layout().addWidget(version_and_comment)

    def post_build(self):
        '''hook events'''
        super(PublishContextWidget, self).post_build()
        self.asset_selector.asset_changed.connect(self._on_asset_changed)
        self.comments_input.textChanged.connect(self._on_comment_updated)
        self.status_selector.currentIndexChanged.connect(self._on_status_changed)

    def _on_status_changed(self, status):
        '''Updates the options dictionary with provided *status* when
        currentIndexChanged of status_selector event is triggered'''
        status_id = self.status_selector.itemData(status)
        self.set_option_result(status_id, key='status_id')
        self.status_selector.on_status_changed(status_id)

    def _on_comment_updated(self):
        '''Updates the option dicctionary with current text when
        textChanged of comments_input event is triggered'''
        current_text = self.comments_input.text()
        self.set_option_result(current_text, key='comment')

    def _on_asset_changed(self, asset_name, asset_entity, is_valid):
        '''Updates the option dicctionary with provided *asset_name* when
        asset_changed of asset_selector event is triggered'''
        self.set_option_result(asset_name, key='asset_name')
        self.set_option_result(is_valid, key='is_valid_name')
        if asset_entity:
            self.set_option_result(asset_entity['id'], key='asset_id')
            self.asset_changed.emit(asset_name, asset_entity['id'], is_valid)
        else:
            self.asset_changed.emit(asset_name, None, is_valid)

    def _build_asset_selector(self):
        '''Builds the asset_selector widget'''
        self.asset_layout = QtWidgets.QVBoxLayout()
        #self.asset_layout.setContentsMargins(0, 0, 0, 0)
        self.asset_layout.setAlignment(QtCore.Qt.AlignTop)

        self.asset_selector = AssetSelector(self.session)
        self.asset_layout.addWidget(self.asset_selector)
        return self.asset_layout

    def _build_status_selector(self):
        '''Builds the status_selector widget'''
        self.status_layout = QtWidgets.QHBoxLayout()
        #self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.setAlignment(QtCore.Qt.AlignTop)

        self.asset_status_label = QtWidgets.QLabel("Status")

        self.status_selector = StatusSelector()

        self.status_layout.addWidget(self.asset_status_label)
        self.status_layout.addWidget(self.status_selector)

        self.status_layout.addStretch()

        thread = BaseThread(
            name='get_status_thread',
            target=self._get_statuses,
            callback=self.emit_statuses,
            target_args=()
        )
        thread.start()

        return self.status_layout

    def _build_comments_input(self):
        '''Builds the comments_container widget'''
        self.coments_layout = QtWidgets.QHBoxLayout()
        self.coments_layout.setContentsMargins(0, 0, 0, 0)
        self.coments_layout.setAlignment(QtCore.Qt.AlignTop)

        comment_label = QtWidgets.QLabel('Description')
        self.comments_input = QtWidgets.QLineEdit()
        self.comments_input.setPlaceholderText("Type a description...")
        self.coments_layout.addWidget(comment_label)
        self.coments_layout.addWidget(self.comments_input)

        self.set_option_result(self.comments_input.text(), key='comment')
        return self.coments_layout

    def emit_statuses(self, statuses):
        '''Emit signal to set statuses on the combobox'''
        #Emit signal to add the sttuses to the combobox
        # because here we could have problems with the threads
        self.statuses_fetched.emit(statuses)

    def set_statuses(self, statuses):
        '''Set statuses on the combo box'''
        self.status_selector.set_statuses(statuses)
        if statuses:
            self.set_option_result(statuses[0]['id'], key='status_id')
            self.status_selector.on_status_changed(statuses[0]['id'])

    def _get_statuses(self):
        '''Returns the status of the selected assetVersion'''
        context_entity = self.session.query(
                'select link, name , parent, parent.name from Context where id '
                'is "{}"'.format(self.context_id)
            ).one()

        project = self.session.query(
            'select name , parent, parent.name from Context where id is "{}"'.format(
                context_entity['link'][0]['id']
            )
        ).one()

        schema = project['project_schema']
        statuses = schema.get_statuses('AssetVersion')
        return statuses

class LoadContextWidget(BaseOptionsWidget):
    '''Main class to represent a context widget on a load process'''

    def __init__(
            self, parent=None, session=None, data=None, name=None,
            description=None, options=None, context_id=None, asset_type_name=None
    ):
        '''initialise PublishContextWidget with *parent*, *session*, *data*,
        *name*, *description*, *options*
        '''

        super(LoadContextWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context_id=context_id,
            asset_type_name=asset_type_name
        )

        self.asset_grid_selector.set_context(context_id, asset_type_name)

    def pre_build(self):
        super(LoadContextWidget, self).pre_build()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.layout().addLayout(self.main_layout)
        self.layout().setContentsMargins(15, 1, 1, 1)

    def build(self):
        '''build function widgets.'''
        if self.context_id:
            self.set_option_result(self.context_id, key='context_id')

        self._build_asset_grid_selector()

    def post_build(self):
        '''hook events'''
        super(LoadContextWidget, self).post_build()
        # self.asset_grid_selector.assets_query_done.connect(self._pre_select_asset)
        self.asset_grid_selector.asset_changed.connect(self._on_asset_changed)

    def _on_asset_changed(self, asset_name, asset_entity, asset_version_id, version_num):
        '''Updates the option dicctionary with provided *asset_name* when
        asset_changed of asset_selector event is triggered'''
        self.set_option_result(asset_name, key='asset_name')
        self.set_option_result(asset_entity['id'], key='asset_id')
        self.set_option_result(version_num, key='version_number')
        self.set_option_result(asset_version_id, key='version_id')
        self.asset_changed.emit(asset_name, asset_entity['id'], True)
        self.asset_version_changed.emit(asset_version_id)

    def _build_asset_grid_selector(self):
        label = QtWidgets.QLabel("Choose which asset and version to open")
        self.asset_grid_selector = AssetGridSelector(self.session)

        self.main_layout.addWidget(label)
        self.main_layout.addWidget(self.asset_grid_selector)


class StatusSelector(QtWidgets.QComboBox):
    _status_colors = {}
    def __init__(self):
        super(StatusSelector, self).__init__()
        self.setEditable(False)
        self.setMinimumWidth(150)

    def set_statuses(self, statuses):
        '''Set statuses on the combo box'''
        #We are now in the main thread
        for index, status in enumerate(statuses):
            self.addItem(status['name'].upper(), status['id'])
            self._status_colors[status['id']] = status['color']

    def on_status_changed(self, status_id):
        ''' Update my style to reflect status color. '''
        self.setStyleSheet('''
            QComboBox {
                border: 1px solid %s;
                border-radius: 10px;
                color: %s;
            }
        '''%(self._status_colors.get(status_id) or '#303030',
             self._status_colors.get(status_id) or '#303030'))