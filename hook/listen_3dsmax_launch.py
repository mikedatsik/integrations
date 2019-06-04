# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import logging
import os

import ftrack_api
import ftrack_connect.application

logger = logging.getLogger('ftrack_connect_pipeline_3dsmax.listen_3dsmax_launch')

plugin_base_dir = os.path.normpath(
    os.path.join(
        os.path.abspath(
            os.path.dirname(__file__)
        ),
        '..'
    )
)

max_connect_plugins_path = os.path.join(
    plugin_base_dir, 'resource', 'plug_ins'
)

max_script_path = os.path.join(
    plugin_base_dir, 'resource', 'scripts'
)

application_hook = os.path.join(
    plugin_base_dir, 'resource', 'application_hook'
)

python_dependencies = os.path.join(
    plugin_base_dir, 'dependencies'
)

max_startup_script = os.path.join(max_script_path, 'startup', 'initftrack.py')


def on_application_launch(event):
    '''Handle application launch and add environment to *event*.'''

    logger.debug('Adding 3dsmax pipeline environments.')

    # Add dependencies in pythonpath
    ftrack_connect.application.appendPath(
        python_dependencies,
        'PYTHONPATH',
        event['data']['options']['env']
    )

    # 3dsmax scripts
    ftrack_connect.application.appendPath(
        max_script_path,
        'PYTHONPATH',
        event['data']['options']['env']
    )

    ftrack_connect.application.appendPath(
        max_script_path,
        '3DS_MAX_SCRIPT_PATH',
        event['data']['options']['env']
    )

    # 3dsmax plugins
    ftrack_connect.application.appendPath(
        max_connect_plugins_path,
        '3DS_MAX_PLUG_IN_PATH',
        event['data']['options']['env']
    )

    # Pipeline plugins
    ftrack_connect.application.appendPath(
        application_hook,
        'FTRACK_EVENT_PLUGIN_PATH',
        event['data']['options']['env']
    )

    # max_startup_script = os.path.join(max_script_path, 'test.py')
    event['data']['command'].extend(['-U', 'PythonHost', max_startup_script])
    # event['data']['command'] = event['data']['command'][:1] + ['-U', 'PythonHost', max_startup_script]


def register(session):
    '''Subscribe to application launch events on *registry*.'''
    if not isinstance(session, ftrack_api.session.Session):
        return

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.launch and data.application.identifier=3ds_max*',
        on_application_launch
    )
