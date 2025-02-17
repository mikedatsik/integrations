# :coding: utf-8
# :copyright: Copyright (c) 2024 ftrack

from ftrack_utils.paths import get_temp_path
from ftrack_framework_core.plugin import BasePlugin
from ftrack_framework_core.exceptions.plugin import PluginExecutionError

from pymxs import runtime as rt


class MaxSaveToTempPlugin(BasePlugin):
    name = 'max_save_to_temp_finalizer'

    def run(self, store):
        '''
        Makes sure that the current opened scene is saved to a temp file so
        prevents it to be overriden.
        '''
        scene_type = '.max'

        try:
            # Save file to a temp file
            save_path = get_temp_path(filename_extension=scene_type)
            # Save Max scene to this path
            rt.saveMaxFile(save_path, useNewFile=True)

            self.logger.debug(f"Max scene saved to temp path: {save_path}")
        except Exception as error:
            raise PluginExecutionError(
                message=f"Error attempting to save the current scene to a "
                f"temporal path: {error}"
            )
