# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os

import maya.cmds as cmd
import maya

from ftrack_connect_pipeline_3dsmax import plugin


class ImportMaxPlugin(plugin.ImportMaxPlugin):
    plugin_name = '3dsmax_load'

    def run(self, context=None, data=None, options=None):

        accepted_formats = options.get('accepts', [])

        def call(component_path):
            self.logger.debug('Calling importer options: data {}'.format(data))
            # TODO(spetterborg) Find out how to import in Max
            # Old plugin relies on a third part Alembic. Hope we can avoid.
            cmd.file(component_path, i=True)
            return True

        component_list = data['component_list']
        location = self.session.pick_location()
        results = []
        for component_id in component_list:
            component = self.session.get('Component', component_id)

            component_path = location.get_filesystem_path(component)
            if accepted_formats and not os.path.splitext(component_path)[-1] in accepted_formats:
                self.logger.warning('{} not among accepted formats {}'.format(
                    component_path, accepted_formats
                ))
                continue
            result = maya.utils.executeInMainThreadWithResult(call, component_path)
            results.append(result)

        return results


def register(api_object, **kw):
    plugin = ImportMaxPlugin(api_object)
    plugin.register()
