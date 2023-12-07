# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack

from ftrack_framework_plugin import BasePlugin


class StoreAssetContextPlugin(BasePlugin):
    name = 'store_asset_context'

    def ui_hook(self, payload):
        '''
        if payload['context_type'] is 'asset': return all Assets on the given
        payload['context_id'] with asset type payload['asset_type_name']

        if payload['context_type'] is 'asset_version': return all
        AssetVersion entities available on the given
        payload['asset_id'] on task payload['context_id']
        '''

        context_id = payload['context_id']
        # Determine if we have a task or not
        context = self.session.query(
            'select link from Context where id is {}'.format(context_id)
        ).one()
        project = self.session.query(
            'select project_schema from Project where id is "{}"'.format(
                context['link'][0]['id']
            )
        ).one()
        statuses = project['project_schema'].get_statuses('AssetVersion')
        # If it's a fake asset, context will be None so return empty list.
        if not context:
            return []

        asset_type_entity = self.session.query(
            'select name from AssetType where short is "{}"'.format(
                payload['asset_type_name']
            )
        ).one()

        if context.entity_type == 'Task':
            asset_versions = self.session.query(
                'select asset.name, asset_id, id, date, version, '
                'is_latest_version, thumbnail_url, user.first_name, '
                'user.last_name, date, status.name from AssetVersion where '
                'is_latest_version is True and task_id is {} and asset.type.id is {}'.format(
                    context_id, asset_type_entity['id']
                )
            ).all()
        else:
            asset_versions = self.session.query(
                'select asset.name, asset_id, id, date, version, '
                'is_latest_version, thumbnail_url, user.first_name, '
                'user.last_name, date, status.name from AssetVersion where '
                'is_latest_version is True and parent.id is {} and asset.type.id is {}'.format(
                    context_id, asset_type_entity['id']
                )
            ).all()

        result = dict()
        result['statuses'] = []
        for status in statuses:
            result['statuses'].append(
                {
                    'id': status['id'],
                    'name': status['name'],
                    'color': status['color'],
                }
            )
        with self.session.auto_populating(False):
            result['assets'] = {}
            for asset_version in asset_versions:
                if asset_version['asset_id'] not in list(
                    result['assets'].keys()
                ):
                    result['assets'][asset_version['asset_id']] = {
                        'name': asset_version['asset']['name'],
                        'versions': [],
                    }

                result['assets'][asset_version['asset_id']]['versions'].append(
                    {
                        'id': asset_version['id'],
                        'date': asset_version['date'].strftime(
                            '%y-%m-%d %H:%M'
                        ),
                        'version': asset_version['version'],
                        'is_latest_version': asset_version[
                            'is_latest_version'
                        ],
                        'thumbnail': asset_version['thumbnail_url']['url'],
                        'server_url': self.session.server_url,
                        'user_first_name': asset_version['user']['first_name'],
                        'user_last_name': asset_version['user']['last_name'],
                        'status': asset_version['status']['name'],
                    }
                )
        return result

    def run(self, store):
        '''
        Store values of the :obj:`self.options`
        'context_id', 'asset_name', 'comment', 'status_id' keys in the
        given *store*
        '''
        keys = [
            'context_id',
            'asset_name',
            'comment',
            'status_id',
            'asset_version_id',
            'asset_type_name',
        ]
        for k in keys:
            if self.options.get(k):
                store[k] = self.options.get(k)