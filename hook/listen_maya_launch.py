# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import os
import ftrack
import ftrack_api
import ftrack_connect.application
import logging

logger = logging.getLogger('ftrack_connect_framework.listen_maya_launch')

plugin_base_dir = os.path.normpath(
    os.path.join(
        os.path.abspath(
            os.path.dirname(__file__)
        ),
        '..'
    )
)

application_hook = os.path.join(
    plugin_base_dir, 'resource', 'application_hook'
)


maya_script_path = os.path.join(
    plugin_base_dir, 'resource', 'maya_plugin'
)

python_dependencies = os.path.join(
    plugin_base_dir, 'dependencies'
)


def on_application_launch(event):
    '''Handle application launch and add environment to *event*.'''

    ftrack_connect.application.appendPath(
        python_dependencies,
        'PYTHONPATH',
        event['data']['options']['env']
    )

    ftrack_connect.application.appendPath(
        maya_script_path,
        'PYTHONPATH',
        event['data']['options']['env']
    )

    ftrack_connect.application.appendPath(
        application_hook,
        'FTRACK_EVENT_PLUGIN_PATH',
        event['data']['options']['env']
    )

    event['data']['options']['env']['FTRACK_CONTEXT_ID'] = (
        event['data']['options']['env']['FTRACK_TASKID']
    )


def register(registry):
    '''Subscribe to application launch events on *registry*.'''
    if registry is not ftrack.EVENT_HANDLERS:
        return

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.connect.application.launch and data.application.identifier=maya*',
        on_application_launch
    )
