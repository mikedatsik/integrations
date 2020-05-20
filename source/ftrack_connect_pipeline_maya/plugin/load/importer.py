# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
from ftrack_connect_pipeline_qt import plugin as pluginWidget
from ftrack_connect_pipeline_maya.plugin import (
    BaseMayaPlugin, BaseMayaPluginWidget
)

from ftrack_connect_pipeline_maya.utils import custom_commands as maya_utils
from ftrack_connect_pipeline_maya.utils import ftrack_asset_node
from ftrack_connect_pipeline_maya import constants

class LoaderImporterMayaPlugin(plugin.LoaderImporterPlugin, BaseMayaPlugin):
    ''' Class representing a Collector Plugin

    .. note::

        _required_output a List
    '''
    asset_node_type = ftrack_asset_node.FtrackAssetNode
    asset_info_type = ftrack_asset_node.FtrackAssetNode

    def _run(self, event):

        self.old_data = maya_utils.get_current_scene_objects()
        self.logger.debug('Got current objects from scene')

        context = event['data']['settings']['context']
        self.logger.debug('Current context : {}'.format(context))

        data = event['data']['settings']['data']
        self.logger.debug('Current data : {}'.format(data))

        options = event['data']['settings']['options']
        self.logger.debug('Current options : {}'.format(options))

        super_result = super(LoaderImporterMayaPlugin, self)._run(event)

        # TODO: Temp. remove this once options ticket is in place, this has to
        #  be assigned from the ui
        options['load_mode'] = 'open'

        asset_load_mode = options.get('load_mode')

        if asset_load_mode and asset_load_mode == constants.OPEN_MODE:
            return super_result

        self.new_data = maya_utils.get_current_scene_objects()
        self.logger.debug(
            'Got all the objects in the scene after import'
        )

        self.link_to_ftrack_node(context, data, options)

        return super_result

    def link_to_ftrack_node(self, context, data, options):
        diff = self.new_data.difference(self.old_data)
        if not diff:
            self.logger.debug('No differences found in the scene')
            return

        self.logger.debug(
            'Checked differences between nodes before and after'
            ' inport : {}'.format(diff)
        )

        ftrack_node_class = self.get_asset_node(context, data, options)

        ftrack_node = ftrack_node_class.init_node()

        ftrack_node_class.connect_objects(diff)



class ImporterMayaWidget(pluginWidget.LoaderImporterWidget, BaseMayaPluginWidget):
    ''' Class representing a Collector Widget

    .. note::

        _required_output a List
    '''

