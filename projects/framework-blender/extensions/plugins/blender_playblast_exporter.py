# :coding: utf-8
# :copyright: Copyright (c) 2024 ftrack

import bpy

from ftrack_utils.paths import get_temp_path

from ftrack_framework_core.plugin import BasePlugin


class BlenderPlayblastExporterPlugin(BasePlugin):
    name = 'blender_playblast_exporter'

    def run(self, store):
        '''
        Create a playblast from the selected camera given in the *store*.
        Save it to a temp file and this one will be published as reviewable.
        '''
        component_name = self.options.get('component')

        # Set the output file path
        save_path = get_temp_path(filename_extension='.mp4')

        scene = bpy.context.scene
        rd = scene.render

        self.logger.debug(f'Setting frames as SF:{scene.frame_start}|EF:{scene.frame_end}|FPS:{rd.fps}')

        # Set the viewport resolution
        rd.resolution_x = 1920
        rd.resolution_y = 1080

        # Set the output format
        rd.image_settings.file_format = "FFMPEG"
        # Set output format
        rd.ffmpeg.format = "MPEG4"
        # Set the codec
        rd.ffmpeg.codec = "H264"

        # Render the viewport and save the result
        bpy.context.scene.render.filepath = save_path
        bpy.ops.render.render(animation=True, use_viewport=True, write_still=True)
        self.logger.debug(f'Rendering playblast to {save_path}')

        store['components'][component_name]['exported_path'] = save_path