# :coding: utf-8
# :copyright: Copyright (c) 2024 ftrack

import bpy
from ftrack_utils.paths import get_temp_path
from ftrack_framework_core.plugin import BasePlugin
from ftrack_framework_core.exceptions.plugin import PluginExecutionError


class BlenderSaveToTempPlugin(BasePlugin):
    name = 'blender_save_to_temp_finalizer'

    def run(self, store):
        '''
        Makes sure that the current opened scene is saved to a temporary file so
        prevents it to be overridden.
        '''

        try:
            # Save file to a temp file
            save_path = get_temp_path(filename_extension='.blend')
            # Save Blender scene to this path
            bpy.ops.wm.save_as_mainfile(filepath=save_path)
            self.logger.debug(f"Blender scene saved to temp path: {save_path}")
        except Exception as error:
            raise PluginExecutionError(
                message=f"Error attempting to save the current scene to a "
                f"temporal path: {error}"
            )

