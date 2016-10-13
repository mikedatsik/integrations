import functools

import ftrack_connect_pipeline.util
import ftrack_connect_pipeline.ui.publish_dialog


def open_publish_dialog(publish_asset):
    '''Open publish dialog for *publish_asset*.'''
    dialog = ftrack_connect_pipeline.ui.publish_dialog.PublishDialog(
        label=publish_asset.label,
        description=publish_asset.description,
        publish_asset=publish_asset
    )
    dialog.exec_()


class Asset(object):
    '''Manage assets.'''

    def __init__(self, identifier, publish_asset=None, import_asset=None):
        '''Instantiate with manager for publish and import.'''
        self.publish_asset = publish_asset
        self.import_asset = import_asset
        self.identifier = identifier

    def discover_publish(self, event):
        '''Discover publish camera.'''
        item = {
            'items': [{
                'label': self.publish_asset.label,
                'icon': self.publish_asset.icon,
                'actionIdentifier': self.identifier
            }]
        }

        return item

    def launch_publish(self, event):
        '''Callback method for publish action.'''
        ftrack_connect_pipeline.util.invoke_in_main_thread(
            functools.partial(open_publish_dialog, self.publish_asset)
        )

        return {
            'success': True,
            'message': 'Custom publish action started successfully!'
        }

    def register(self, session):
        '''Register listeners on *session*.'''
        self._session = session

        self._session.event_hub.subscribe(
            'topic=ftrack.action.discover',
            self.discover_publish
        )

        self._session.event_hub.subscribe(
            'topic=ftrack.action.launch and data.actionIdentifier={0}'.format(
                self.identifier
            ),
            self.launch_publish
        )


class ImportAsset(object):
    '''Manage import of an asset.'''

    def discover(self, event):
        '''Discover import camera.'''
        raise NotImplementedError()

    def get_options(self, component):
        '''Return import options from *component*.'''
        return []

    def import_asset(self, component, options):
        '''Import *component* based on *options*.'''
        raise NotImplementedError()


class PublishAsset(object):
    '''Manage publish of an asset.'''

    def __init__(self, label, description, icon=None):
        '''Instantiate publish asset with *label* and *description*.'''
        self.label = label
        self.description = description
        self.icon = icon

    def discover(self, event):
        '''Discover import camera.'''
        raise NotImplementedError()

    def prepare_publish(self):
        '''Return context for publishing.'''
        return dict()

    def get_publish_items(self, publish_data):
        '''Return list of items that can be published.'''
        return []

    def get_item_options(self, publish_data, key):
        '''Return options for publishable item with *key*.'''
        return []

    def get_options(self, publish_data):
        '''Return general options for.'''
        from ftrack_connect_pipeline.ui.widget.field import asset_selector
        asset_selector = asset_selector.AssetSelector(
            ftrack_connect_pipeline.util.get_ftrack_entity()
        )

        return [{
            'widget': asset_selector,
            'type': 'qt_widget',
            'name': 'asset'
        }]

    def update_with_options(
        self, publish_data, item_options, general_options, selected_items
    ):
        '''Update *publish_data* with *item_options* and *general_options*.'''
        publish_data['options'] = general_options
        publish_data['item_options'] = item_options
        publish_data['selected_items'] = selected_items
        print '!! DATA', publish_data

    def publish(self, publish_data):
        '''Publish or raise exception if not valid.'''
        raise NotImplementedError()

    def get_scene_selection(self):
        '''Return a list of names for scene selection.'''
        raise NotImplementedError()
