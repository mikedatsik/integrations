# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack

import ftrack_api

import nuke

from ftrack_framework_nuke import plugin
from ftrack_framework_nuke.constants import asset as asset_const


class NukeCameraLoaderImporterPlugin(plugin.NukeLoaderImporterPlugin):
    '''Nuke camera loader plugin'''

    plugin_name = 'nuke_camera_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        '''Load collected camera(s) supplied with *data* into Nuke'''

        results = {}

        paths_to_import = []
        for collector in data:
            paths_to_import.append(
                collector['result'].get(asset_const.COMPONENT_PATH)
            )

        for component_path in paths_to_import:
            self.logger.debug('Importing path {}'.format(component_path))
            import_result = nuke.createNode(
                'Camera3', 'file {}'.format(component_path)
            )
            results[component_path] = import_result.name()

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NukeCameraLoaderImporterPlugin(api_object)
    plugin.register()