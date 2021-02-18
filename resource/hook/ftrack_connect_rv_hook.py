# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import getpass
import sys
import pprint
import logging
import json
import re

import ftrack

import platform

cwd = os.path.dirname(__file__)

sources = os.path.abspath(os.path.join(cwd, '..', 'dependencies'))

sys.path.append(sources)

import ftrack_api
import ftrack_application_launcher
import ftrack_connect_rv

RV_INSTALLATION_PATH = os.getenv(
    'RV_INSTALLATION_PATH', '/usr/local/rv'
)


class ApplicationLauncher(ftrack_application_launcher.ApplicationLauncher):
    '''Discover and launch rv.'''

    def _get_application_environment(self, application, context=None):
        '''Override to modify environment before launch.'''

        # Make sure to call super to retrieve original environment
        # which contains the selection and ftrack API.
        environment = super(
            ApplicationLauncher, self
        )._get_application_environment(application, context)

        environment = ftrack_application_launcher.appendPath(
            sources,
            'PYTHONPATH',
            environment
        )

        return environment


class LaunchRvAction(ftrack_application_launcher.ApplicationLaunchAction):
    '''Adobe plugins discover and launch action.'''
    context = ['Task', 'AssetVersion']

    identifier = 'ftrack-connect-launch-rv'

    def __init__(self, session,  application_store, launcher):
        '''Initialise action with *applicationStore* and *launcher*.

        *applicationStore* should be an instance of
        :class:`ftrack_connect.application.ApplicationStore`.

        *launcher* should be an instance of
        :class:`ftrack_connect.application.ApplicationLauncher`.

        '''
        super(LaunchRvAction, self).__init__(
            session=session,
            application_store=application_store,
            launcher=launcher,
            priority=0
        )

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    def _createPlaylistFromSelection(self, selection):
        '''Return new selection with temporary playlist from *selection*.'''

        # If selection is only one entity we don't need to create
        # a playlist.
        if len(selection) == 1:
            return selection

        playlist = []
        for entity in selection:
            playlist.append({
                'id': entity['entityId'],
                'type': entity['entityType']
            })

        playlist = ftrack.createTempData(json.dumps(playlist))

        selection = [{
            'entityType': 'tempdata',
            'entityId': playlist.getId()
        }]

        return selection

    def _discover(self, event):
        '''Return discovered applications.'''
        items = []
        applications = self.applicationStore.applications
        applications = sorted(
            applications, key=lambda application: application['label']
        )

        for application in applications:
            applicationIdentifier = application['identifier']
            label = application['label']
            items.append({
                'actionIdentifier': self.identifier,
                'label': label,
                'variant': application.get('variant', None),
                'description': application.get('description', None),
                'icon': application.get('icon', 'default'),
                'applicationIdentifier': applicationIdentifier,
                'host': platform.node()
            })

        return {
            'items': items
        }

    def _launch(self, event):
        '''Handle *event*.

        event['data'] should contain:

            *applicationIdentifier* to identify which application to start.

        '''
        applicationIdentifier = (
            event['data']['applicationIdentifier']
        )

        context = event['data'].copy()

        # Rewrite original selection to a playlist.
        context['selection'] = self._createPlaylistFromSelection(
            context['selection']
        )

        return self.launcher.launch(
            applicationIdentifier, context
        )

    def get_version_information(self, event):
        '''Return version information.'''
        return dict(
            name='ftrack connect rv',
            version=ftrack_connect_rv.__version__
        )


class ApplicationStore(ftrack_application_launcher.ApplicationStore):

    def _discover_applications(self):
        '''Return a list of applications that can be launched from this host.

        An application should be of the form:

            dict(
                'identifier': 'name_version',
                'label': 'Name',
                'variant': 'version',
                'description': 'description',
                'path': 'Absolute path to the file',
                'version': 'Version of the application',
                'icon': 'URL or name of predefined icon'
            )

        '''
        applications = []

        if sys.platform == 'darwin':
            prefix = ['/', 'Applications']
            applications.extend(self._searchFilesystem(
                expression=prefix + ['RV.\d+.app'],
                label='Review with RV',
                variant='{version}',
                applicationIdentifier='rv_{version}_with_review',
                icon='rv',
                launchArguments=[
                    '--args', '-flags', 'ModeManagerPreload=ftrack'
                ]
            ))

        elif sys.platform == 'win32':
            prefix = ['C:\\', 'Program Files.*']
            applications.extend(self._searchFilesystem(
                expression=prefix + [
                    '[Tweak|Shotgun]', 'RV.\d.+', 'bin', 'rv.exe'
                ],
                label='Review with RV',
                variant='{version}',
                applicationIdentifier='rv_{version}_with_review',
                icon='rv',
                launchArguments=[
                    '-flags', 'ModeManagerPreload=ftrack'
                ],
                versionExpression=re.compile(
                    r'(?P<version>\d+.\d+.\d+)'
                )
            ))

        elif sys.platform == 'linux2':
            separator = os.path.sep
            prefix = RV_INSTALLATION_PATH
            if not os.path.exists(RV_INSTALLATION_PATH):
                self.logger.debug(
                    'No folder found for '
                    '$RV_INSTALLATION_PATH at : {0}'.format(
                        RV_INSTALLATION_PATH
                    )
                )

            else:
                # Check for leading slashes
                if RV_INSTALLATION_PATH.startswith(separator):
                    # Strip it off if does exist
                    prefix = prefix[1:]

                # Split the path in its components.
                prefix = prefix.split(separator)
                if RV_INSTALLATION_PATH.startswith(separator):
                    # Add leading slash back
                    prefix.insert(0, separator)

                applications.extend(self._searchFilesystem(
                    expression=prefix + [
                        'rv-Linux-x86-64-\d.+', 'bin', 'rv$'
                    ],
                    label='Review with RV',
                    variant='{version}',
                    applicationIdentifier='rv_{version}_with_review',
                    icon='rv',
                    launchArguments=[
                        '-flags', 'ModeManagerPreload=ftrack'
                    ],
                    versionExpression=re.compile(
                        r'(?P<version>\d+(\.\d+)+)'
                    )
                ))

        self.logger.debug(
            'Discovered applications:\n{0}'.format(
                pprint.pformat(applications)
            )
        )

        return applications


def register(session, **kw):
    '''Register hooks.'''

    logger = logging.getLogger(
        'ftrack_plugin:ftrack_connect_rv_hook.register'
    )

    # Validate that registry is ftrack.EVENT_HANDLERS. If not, assume that
    # register is being called from a new or incompatible API and
    # return without doing anything.
    if not isinstance(session, ftrack_api.session.Session):
        return

    # Create store containing applications.
    application_store = ApplicationStore(session=session)

    # Create a launcher with the store containing applications.
    launcher = ApplicationLauncher(
        application_store
    )

    # Create action and register to respond to discover and launch actions.
    action = LaunchRvAction(session, application_store, launcher)
    action.register()
