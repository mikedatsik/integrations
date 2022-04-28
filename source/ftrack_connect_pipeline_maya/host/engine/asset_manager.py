# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import time
import maya
import maya.cmds as cmds

from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline.host.engine import AssetManagerEngine
from ftrack_connect_pipeline.asset.asset_info import FtrackAssetInfo
from ftrack_connect_pipeline_maya.utils import custom_commands as maya_utils
from ftrack_connect_pipeline_maya.constants import asset as asset_const
from ftrack_connect_pipeline_maya.asset import MayaFtrackObjectManager
from ftrack_connect_pipeline_maya.asset.dcc_object import MayaDccObject as DccObject


class MayaAssetManagerEngine(AssetManagerEngine):
    engine_type = 'asset_manager'

    @property
    def ftrack_object_manager(self):
        '''
        Returns If the asset is loaded
        '''
        if not isinstance(self._ftrack_object_manager, MayaFtrackObjectManager):
            self._ftrack_object_manager = MayaFtrackObjectManager(self.event_manager)
        return self._ftrack_object_manager

    def __init__(
        self, event_manager, host_types, host_id, asset_type_name=None
    ):
        '''Initialise AssetManagerEngine with *event_manager*, *host*, *hostid*
        and *asset_type_name*'''
        super(MayaAssetManagerEngine, self).__init__(
            event_manager, host_types, host_id, asset_type_name=asset_type_name
        )

    @maya_utils.run_in_main_thread
    def discover_assets(self, assets=None, options=None, plugin=None):
        '''
        Discover all the assets in the scene:
        Returns status and result
        '''
        start_time = time.time()
        status = constants.UNKNOWN_STATUS
        result = []
        message = None

        result_data = {
            'plugin_name': None,
            'plugin_type': constants.PLUGIN_AM_ACTION_TYPE,
            'method': 'discover_assets',
            'status': status,
            'result': result,
            'execution_time': 0,
            'message': message,
        }

        ftrack_asset_nodes = maya_utils.get_ftrack_nodes()
        ftrack_asset_info_list = []

        if ftrack_asset_nodes:
            for node_name in ftrack_asset_nodes:
                dcc_object = DccObject(node_name)
                param_dict = dcc_object.parameters_dictionary()
                node_asset_info = FtrackAssetInfo(param_dict)
                ftrack_asset_info_list.append(node_asset_info)

            if not ftrack_asset_info_list:
                status = constants.ERROR_STATUS
            else:
                status = constants.SUCCESS_STATUS
        else:
            self.logger.debug("No assets in the scene")
            status = constants.SUCCESS_STATUS

        result = ftrack_asset_info_list

        end_time = time.time()
        total_time = end_time - start_time

        result_data['status'] = status
        result_data['result'] = result
        result_data['execution_time'] = total_time

        self._notify_client(plugin, result_data)

        return status, result

    @maya_utils.run_in_main_thread
    def select_asset(self, asset_info, options=None, plugin=None):
        '''
        Selects the given *asset_info* from the scene.
        *options* can contain clear_selection to clear the selection before
        select the given *asset_info*.
        Returns status and result
        '''
        start_time = time.time()
        status = constants.UNKNOWN_STATUS
        result = []
        message = None

        plugin_type = constants.PLUGIN_AM_ACTION_TYPE
        plugin_name = None
        if plugin:
            plugin_type = '{}.{}'.format('asset_manager', plugin['type'])
            plugin_name = plugin.get('name')

        result_data = {
            'plugin_name': plugin_name,
            'plugin_type': plugin_type,
            'method': 'select_asset',
            'status': status,
            'result': result,
            'execution_time': 0,
            'message': message,
        }

        self.ftrack_object_manager.asset_info = asset_info
        dcc_object = DccObject()
        dcc_object.from_asset_info_id(asset_info[asset_const.ASSET_INFO_ID])
        self.ftrack_object_manager.dcc_object = dcc_object

        if options.get('clear_selection'):
            cmds.select(cl=True)

        nodes = cmds.listConnections(
            '{}.{}'.format(
                self.ftrack_object_manager.dcc_object, asset_const.ASSET_LINK
            )
        )
        for node in nodes:
            try:
                cmds.select(node, add=True)
                result.append(str(node))
                status = constants.SUCCESS_STATUS
            except Exception as error:
                message = str(
                    'Could not select the node {}, error: {}'.format(
                        str(node), error
                    )
                )
                self.logger.error(message)
                status = constants.ERROR_STATUS

            bool_status = constants.status_bool_mapping[status]
            if not bool_status:
                end_time = time.time()
                total_time = end_time - start_time

                result_data['status'] = status
                result_data['result'] = result
                result_data['execution_time'] = total_time
                result_data['message'] = message

                self._notify_client(plugin, result_data)
                return status, result

        end_time = time.time()
        total_time = end_time - start_time

        result_data['status'] = status
        result_data['result'] = result
        result_data['execution_time'] = total_time

        self._notify_client(plugin, result_data)

        return status, result

    @maya_utils.run_in_main_thread
    def select_assets(self, asset_infos, options=None, plugin=None):
        result = None
        for asset_info in asset_infos:
            result = self.select_asset(
                asset_info, options=options, plugin=options
            )
        return result

    @maya_utils.run_in_main_thread
    def remove_asset(
        self, asset_info, options=None, plugin=None, keep_ftrack_node=False
    ):
        '''
        Removes the given *asset_info* from the scene.
        Returns status and result
        '''
        start_time = time.time()
        status = constants.UNKNOWN_STATUS
        result = []
        message = None

        plugin_type = constants.PLUGIN_AM_ACTION_TYPE
        plugin_name = None
        if plugin:
            plugin_type = '{}.{}'.format('asset_manager', plugin['type'])
            plugin_name = plugin.get('name')

        result_data = {
            'plugin_name': plugin_name,
            'plugin_type': plugin_type,
            'method': 'remove_asset'
            if not keep_ftrack_node
            else 'unload_asset',
            'status': status,
            'result': result,
            'execution_time': 0,
            'message': message,
        }

        self.ftrack_object_manager.asset_info = asset_info
        dcc_object = DccObject()
        dcc_object.from_asset_info_id(asset_info[asset_const.ASSET_INFO_ID])
        self.ftrack_object_manager.dcc_object = dcc_object

        reference_node = False
        nodes = (
            cmds.listConnections(
                '{}.{}'.format(
                    self.ftrack_object_manager.dcc_object, asset_const.ASSET_LINK
                )
            )
            or []
        )
        for node in nodes:
            if cmds.nodeType(node) == 'reference':
                reference_node = maya_utils.getReferenceNode(node)
                if reference_node:
                    break

        if reference_node:
            self.logger.debug("Removing reference: {}".format(reference_node))
            try:
                maya_utils.remove_reference_node(reference_node)
                result.append(str(reference_node))
                status = constants.SUCCESS_STATUS
            except Exception as error:
                message = str(
                    'Could not remove the reference node {}, error: {}'.format(
                        str(reference_node), error
                    )
                )
                self.logger.error(message)
                status = constants.ERROR_STATUS

            bool_status = constants.status_bool_mapping[status]
            if not bool_status:
                end_time = time.time()
                total_time = end_time - start_time

                result_data['status'] = status
                result_data['result'] = result
                result_data['execution_time'] = total_time
                result_data['message'] = message

                self._notify_client(plugin, result_data)
                return status, result
        else:
            for node in nodes:
                self.logger.debug("Removing object: {}".format(node))
                try:
                    if cmds.objExists(node):
                        cmds.delete(node)
                        result.append(str(node))
                        status = constants.SUCCESS_STATUS
                except Exception as error:
                    message = str(
                        'Node: {0} could not be deleted, error: {1}'.format(
                            node, error
                        )
                    )
                    self.logger.error(message)
                    status = constants.ERROR_STATUS

                bool_status = constants.status_bool_mapping[status]
                if not bool_status:
                    end_time = time.time()
                    total_time = end_time - start_time

                    result_data['status'] = status
                    result_data['result'] = result
                    result_data['execution_time'] = total_time
                    result_data['message'] = message

                    self._notify_client(plugin, result_data)
                    return status, result

        if (
            cmds.objExists(self.ftrack_object_manager.dcc_object)
            and keep_ftrack_node is False
        ):
            try:
                cmds.delete(self.ftrack_object_manager.dcc_object)
                result.append(str(self.ftrack_object_manager.dcc_object))
                status = constants.SUCCESS_STATUS
            except Exception as error:
                message = str(
                    'Could not delete the dcc_object, error: {}'.format(
                        error
                    )
                )
                self.logger.error(message)
                status = constants.ERROR_STATUS

            bool_status = constants.status_bool_mapping[status]
            if not bool_status:
                end_time = time.time()
                total_time = end_time - start_time

                result_data['status'] = status
                result_data['result'] = result
                result_data['execution_time'] = total_time
                result_data['message'] = message

                self._notify_client(plugin, result_data)

                return status, result

        end_time = time.time()
        total_time = end_time - start_time

        result_data['status'] = status
        result_data['result'] = result
        result_data['execution_time'] = total_time

        self._notify_client(plugin, result_data)

        return status, result
