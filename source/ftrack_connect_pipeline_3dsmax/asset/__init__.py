# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import MaxPlus
import json
from ftrack_connect_pipeline.asset import FtrackAssetInfo, FtrackAssetBase
from ftrack_connect_pipeline_3dsmax.constants import asset as asset_const
from ftrack_connect_pipeline_3dsmax.constants.asset import modes as load_const
import ftrack_connect_pipeline_3dsmax.utils.custom_commands as max_utils


class FtrackAssetNode(FtrackAssetBase):
    '''
    Base FtrackAssetNode class.
    '''

    identity = MaxPlus.Class_ID(*asset_const.FTRACK_ASSET_CLASS_ID)

    def is_ftrack_object(self, object):
        '''
        Checks if the given object *other* has the same ClassID as the
        current identity
        '''
        if object.Object.ClassID == self.identity:
            return True

        return False

    def is_sync(self, ftrack_object):
        '''Returns bool if the current ftrack_object is sync'''
        return self._check_ftrack_object_sync(ftrack_object)

    def __init__(self, event_manager):
        '''
        Initialize FtrackAssetNode with *event_manager*.

        *event_manager* instance of
        :class:`ftrack_connect_pipeline.event.EventManager`
        '''
        super(FtrackAssetNode, self).__init__(event_manager)

        self.helper_object = MaxPlus.Factory.CreateHelperObject(
            self.identity
        )
        self.logger.debug(
            'helper_object {} has been created'.format(self.helper_object)
        )

    def init_ftrack_object(self):
        '''
        Return the ftrack_object for this class. It checks if there is
        already a matching ftrack_object in the scene, in this case, it
        updates the ftrack_object if it's not. In case there is no ftrack_object
        in the scene this function creates a new one.
        '''
        ftrack_object = self.get_ftrack_object_from_scene()
        if not ftrack_object:
            ftrack_object = self.create_new_ftrack_object()
        if ftrack_object:
            if not self.is_sync(ftrack_object):
                ftrack_object = self._update_ftrack_object(ftrack_object)

        self.ftrack_object = ftrack_object

        return self.ftrack_object

    @staticmethod
    def get_parameters_dictionary(max_obj):
        '''
        Returns a diccionary with the keys and values of the given *max_obj*
        parameters
        '''
        param_dict = {}
        for p in max_obj.ParameterBlock.Parameters:
            param_dict[p.Name] = p.Value
        return param_dict

    def get_ftrack_object_from_scene(self):
        '''
        Return the ftrack_object from the current asset_version if it exists in
        the scene.
        '''
        ftrack_asset_nodes = max_utils.get_ftrack_helpers()
        for ftrack_object in ftrack_asset_nodes:
            obj = ftrack_object.Object

            param_dict = self.get_parameters_dictionary(obj)
            node_asset_info = FtrackAssetInfo(param_dict)

            if node_asset_info.is_deprecated:
                raise DeprecationWarning("Can not read v1 ftrack asset plugin")
            if (
                    node_asset_info[asset_const.REFERENCE_OBJECT] ==
                    self.asset_info[asset_const.REFERENCE_OBJECT]
            ):

                return ftrack_object

    def _check_ftrack_object_sync(self, ftrack_object):
        '''
        Check if the current parameters of the ftrack_object match the values
        of the asset_info.
        '''
        if not ftrack_object:
            self.logger.warning("Can't check if ftrack ftrack_object is not loaded")
            return False

        synced = False
        obj = ftrack_object.Object

        param_dict = self.get_parameters_dictionary(obj)
        node_asset_info = FtrackAssetInfo(param_dict)

        if node_asset_info == self.asset_info:
            self.logger.debug("{} is synced".format(ftrack_object))
            synced = True

        return synced

    def _get_unique_ftrack_object_name(self):
        '''
        Return a unique scene name for the current ftrack_object
        '''
        ftrack_object_name = super(
            FtrackAssetNode, self
        )._get_unique_ftrack_object_name()

        return max_utils.get_unique_node_name(ftrack_object_name)

    def connect_objects(self, objects):
        '''
        Parent the given *objects* under current ftrack_object

        *objects* is List type of INode
        '''

        max_utils.deselect_all()
        for obj in objects:
            max_utils.add_node_to_selection(obj)
        self._connect_selection()
        if (
                self.asset_info[asset_const.LOAD_MODE] !=
                load_const.SCENE_XREF_MODE
        ):
            self.reload_references_from_selection()

    def get_load_mode_from_ftrack_object(self, node):
        '''Return the load mode used to import an asset.'''
        obj = node.Object
        return obj.ParameterBlock.asset_info_options.Value

    def reload_references_from_selection(self):
        '''
        Reload all the ftrack dependencies that are referenced in the current
        selection.
        '''
        for node in MaxPlus.SelectionManager.Nodes:
            if self.is_ftrack_object(node) and self.get_load_mode_from_ftrack_object(
                    node) == load_const.SCENE_XREF_MODE:
                if not max_utils.scene_XRef_imported(node):
                    self.logger.debug(u'Re-importing {0} scene xref.'.format(
                        node.Name))
                    max_utils.re_import_scene_XRef(
                        node.Object.ParameterBlock.component_path.Value,
                        node.Name
                    )

    def create_new_ftrack_object(self):
        '''
        Creates a ftrack_object with a unique name. The ftrack_object is
        type of FtrackAssetHelper.
        '''
        name = self._get_unique_ftrack_object_name()
        ftrack_object = MaxPlus.Factory.CreateNode(self.helper_object)
        ftrack_object.Name = name

        # Try to freeze the helper object and lock the transform.
        try:
            cmd = 'freeze ${0} ; setTransformLockFlags ${0} #all'.format(
                ftrack_object.Name)
            max_utils.eval_max_script(cmd)
        except Exception, e:
            self.logger.debug(
                "Could not freeze object {0}, Error: {1}".format(
                    self.asset_info['asset_name'], e
                )
            )

        return ftrack_object

    def _update_ftrack_object(self, ftrack_object):
        '''Update the parameters of the ftrack_object. And Return the
        ftrack_object updated
        '''
        print "updating ftrack object"
        try:
            cmd = 'unfreeze ${0}'.format(ftrack_object.Name)
            max_utils.eval_max_script(cmd)
        except:
            self.logger.debug(
                "Could not unfreeze object {0}".format(ftrack_object.Name))

        obj = ftrack_object.Object

        print "self.asset_info ---> {}".format(self.asset_info)

        for p in obj.ParameterBlock.Parameters:
            print "on the update p.Name: {} , p.Value: {}".format(p.Name, p.Value)
            if p.Name == asset_const.REFERENCE_OBJECT:
                p.SetValue(str(ftrack_object))
            elif p.Name == asset_const.VERSIONS:
                continue
            elif p.Name == asset_const.IS_LATEST_VERSION:
                p.SetValue(bool(self.asset_info[p.Name]))
            elif p.Name == asset_const.SESSION:
                p.SetValue(str(self.asset_info[p.Name]))
            elif p.Name == asset_const.ASSET_INFO_OPTIONS:
                decoded_value = self.asset_info[p.Name]
                p.SetValue(str(
                    json.dumps(decoded_value).encode('base64')))
            else:
                p.SetValue(self.asset_info[p.Name])
            print "after on the update p.Name: {} , p.Value: {}".format(p.Name,
                                                                  p.Value)

        try:
            cmd = 'freeze ${0}'.format(ftrack_object.Name)
            max_utils.eval_max_script(cmd)
        except Exception, e:
            self.logger.debug(
                "Could not freeze object {0}, Error: {1}".format(
                    ftrack_object.Name, e
                )
            )
        return ftrack_object

    def _get_component_id_from_helper_node(self, helper_node):
        '''
        Return component_id of the given *helperNode*.
        '''
        component_id = helper_node.Object.ParameterBlock.component_id.Value
        return component_id

    def _get_version_id_from_helper_node(self, helper_node):
        '''
        Return version_id of the given *helperNode*.
        '''
        version_id = helper_node.Object.ParameterBlock.version_id.Value
        return version_id

    def _connect_selection(self):
        '''
        Removes pre existing asset helper objects and parent the selected
        nodes to the current ftrack_object.
        '''
        version_id = self.asset_info[asset_const.VERSION_ID]
        component_id = self.asset_info[asset_const.COMPONENT_ID]
        root_node = MaxPlus.Core.GetRootNode()

        nodes_to_delete = []

        self.logger.debug(u'Removing duplicated asset helper objects')
        for node in MaxPlus.SelectionManager.Nodes:
            if self.is_ftrack_object(node) and node.Parent == root_node:
                helper_component_id = self._get_component_id_from_helper_node(node)
                if helper_component_id == component_id:
                    self.logger.debug(
                        u'Deleting imported helper ftrack_object {0}'.format(node.Name))
                    nodes_to_delete.append(node)

        # Delete helper ftrack_objects that represent the asset we are importing.
        for node in nodes_to_delete:
            MaxPlus.SelectionManager.DeSelectNode(node)
            node.Delete()

        self.logger.debug(u'Parenting objects to helper object')
        for node in MaxPlus.SelectionManager.Nodes:
            if node.Parent == root_node:
                node.Parent = self.ftrack_object
                self.logger.debug(
                    'ftrack_object {} added to ftrack ftrack_object {}'.format(
                        node, self.ftrack_object
                    )
                )

