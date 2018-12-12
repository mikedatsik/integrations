import os
import functools
import logging

import ftrack_api
from ftrack_connect_framework import constants

logger = logging.getLogger(__name__)


def publish_result(session, data=None, options=None):
    asset_name = options['asset_name']
    context = session.get('Context', options['context_id'])
    asset_parent = context['parent']
    asset_type = session.query('AssetType where short is "{}"'.format(options['asset_type'])).first()
    location = session.pick_location()

    asset = session.query(
        'Asset where name is "{}" and type.short is "{}" and parent.id is "{}"'.format(
            asset_name, options['asset_type'], asset_parent['id'])
    ).first()

    if not asset:
        asset = session.create('Asset', {
            'name': asset_name,
            'type': asset_type,
            'parent': asset_parent
        })

    asset_version = session.create('AssetVersion', {
        'asset': asset,
        'task': context,
    })

    session.commit()

    for path in data:
        asset_version.create_component(
            path[1], data={'name': os.path.basename(path[0])}, location=location
        )
    session.commit()

    logger.debug("publishing: {} to {} as {}".format(data, context, asset_type))
    return True


def register_publisher(session,event):
    return publish_result(session, **event['data'])


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register_assets is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    topic = constants.PUBLISHERS_PLUGIN_TOPIC.format('result')
    logger.info('discovering :{}'.format(topic))

    event_handler = functools.partial(
        register_publisher, api_object
    )

    api_object.event_hub.subscribe(
        'topic={}'.format(topic),
        event_handler
    )
