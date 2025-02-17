# :coding: utf-8
# :copyright: Copyright (c) 2024 ftrack

import os
import ftrack_api
import logging
import functools

from ftrack_utils.version import get_connect_plugin_version

# The name of the integration, should match name in launcher.
NAME = 'framework-max'


logger = logging.getLogger(__name__)

cwd = os.path.dirname(__file__)
connect_plugin_path = os.path.abspath(os.path.join(cwd, '..'))

# Read version number from __version__.py
__version__ = get_connect_plugin_version(connect_plugin_path)

python_dependencies = os.path.join(connect_plugin_path, 'dependencies')


def on_discover_integration(session, event):
    data = {
        'integration': {
            'name': NAME,
            'version': __version__,
        }
    }

    return data


def on_launch_integration(session, event):
    '''Handle application launch and add environment to *event*.'''

    launch_data = {'integration': event['data']['integration']}

    discover_data = on_discover_integration(session, event)
    for key in discover_data['integration']:
        launch_data['integration'][key] = discover_data['integration'][key]

    integration_version = event['data']['application']['version'].version[0]
    logger.info('Launching integration v{}'.format(integration_version))

    if not launch_data['integration'].get('env'):
        launch_data['integration']['env'] = {}

    bootstrap_path = os.path.join(connect_plugin_path, 'resource', 'bootstrap')

    logger.info('Adding {} to PYTHONPATH'.format(bootstrap_path))
    launch_data['integration']['env'][
        'PYTHONPATH.prepend'
    ] = os.path.pathsep.join([python_dependencies, bootstrap_path])

    launch_data['integration']['env'][
        'ADSK_3DSMAX_STARTUPSCRIPTS_ADDON_DIR'
    ] = bootstrap_path

    launch_data['integration']['env']['FTRACK_MAX_VERSION'] = str(
        integration_version
    )

    ##########################################################################
    # The virtual environment specific environment variable VIRTUAL_ENV
    # is passed to the spawned process (that launches 3dsMax or any other app).
    # 3ds Max "understands" this variable and incorporates it into its own
    # environment. This is a problem when running ftrack connect from a virtual
    # environment which has other libraries/dependencies than 3ds Max.
    # This leads to problems with certain libraries, specifically PySide not being
    # able to locate the proper dlls of the host DCC.
    # For now, we unset the variable.
    # TODO: we should probably make this configurable so the venv CAN be inherited if desired.
    launch_data['integration']['env']['VIRTUAL_ENV.unset'] = ""
    ##########################################################################

    selection = event['data'].get('context', {}).get('selection', [])

    if selection:
        task = session.get('Context', selection[0]['entityId'])
        launch_data['integration']['env']['FTRACK_CONTEXTID.set'] = task['id']

    return launch_data


def register(session):
    '''Subscribe to application launch events on *registry*.'''
    if not isinstance(session, ftrack_api.session.Session):
        return

    handle_discovery_event = functools.partial(
        on_discover_integration, session
    )

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.discover and '
        'data.application.identifier=max*'
        ' and data.application.version >= 2025',
        handle_discovery_event,
        priority=40,
    )

    handle_launch_event = functools.partial(on_launch_integration, session)

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.launch and '
        'data.application.identifier=max*'
        ' and data.application.version >= 2025',
        handle_launch_event,
        priority=40,
    )

    logger.info(
        'Registered {} integration v{} discovery and launch.'.format(
            NAME, __version__
        )
    )
