import hiero.core
import hiero.ui
from QtExt import QtCore, QtWidgets
from hiero.ui.FnTagFilterWidget import TagFilterWidget

from ftrack_connect_nuke_studio.ui.create_project import ProjectTreeDialog
from .ftrack_base import FtrackBase
from hiero.exporters.FnShotProcessorUI import ShotProcessorUI


class FtrackShotProcessorUI(ShotProcessorUI, FtrackBase):

    def __init__(self, preset):
        FtrackBase.__init__(self)
        ShotProcessorUI.__init__(
            self,
            preset,
        )

        self.projectTreeDialog = None

    def displayName(self):
        return "Ftrack"

    def toolTip(self):
        return "Process as Shots generates output on a per shot basis."
            
    def createProcessorSettingsWidget(self, exportItems):
        widgets = []

        self.logger.info('building processor widget')

        for path, preset in self._preset.properties()['exportTemplate']:
            if not preset:
                continue
            
            task_ui = hiero.ui.taskUIRegistry.getNewTaskUIForPreset(preset)

            if not task_ui:
                continue

            task_ui.setProject(self._project)
            task_ui.setTags(self._tags)

            taskUIWidget = QtWidgets.QWidget()
            task_ui.setTaskItemType(self.getTaskItemType())
            task_ui.initializeAndPopulateUI(taskUIWidget, self._exportTemplate)
            widgets.append((taskUIWidget, preset.name()))

            if self._editMode == hiero.ui.IProcessorUI.ReadOnly:
                task_ui.setEnabled(False)
        
            try:
                task_ui.propertiesChanged.connect(self.onExportStructureModified,
                                            type=QtCore.Qt.UniqueConnection)
            except:
                # Signal already connected.
                pass

        return widgets
            

    def _checkExistingVersions(self, exportItems):
        """ Iterate over all the track items which are set to be exported, and check if they have previously
        been exported with the same version as the setting in the current preset.  If yes, show a message box
        asking the user if they would like to increment the version, or overwrite it. """

        for item in exportItems:
            self.logger.info('_checkExistingVersions of:{0}'.format(item.name()))

        return ShotProcessorUI._checkExistingVersions(
            self,
            exportItems,
        )

    def populateUI(self, *args, **kwargs):
        self.logger.info('Populating UI')
        if self.hiero_version_touple >= (10, 5, 1):
            (widget, taskUIWidget, exportItems) = args
            _widget = widget
        else:
            (widget, exportItems, editMode) = args
            _widget= widget
    
        self._exportItems = exportItems
        self._editMode = hiero.ui.IProcessorUI.ReadOnly if self._preset.readOnly() else hiero.ui.IProcessorUI.Full

        self._taskUILayout = QtWidgets.QVBoxLayout(widget)
        self._taskUILayout.setContentsMargins(10, 0, 0, 0)

        self._tabWidget = QtWidgets.QTabWidget()
        self.handles = self.createHandleWidgets()
        self._tabWidget.addTab(self.handles, 'Tracks && Handles')

        self._taskUILayout.addWidget(self._tabWidget)
        self._tags = self.findTagsForItems(exportItems)
        self._editMode = hiero.ui.IProcessorUI.ReadOnly if self._preset.readOnly() else hiero.ui.IProcessorUI.Full

        ftags = []
        sequence = None
        for item in exportItems:
            hiero_item = item.item()
            if not isinstance(hiero_item, hiero.core.TrackItem):
                continue

            tags = hiero_item.tags()
            tags = [tag for tag in tags if tag.metadata().hasKey(
                'ftrack.type'
            )]
            ftags.append((hiero_item, tags))
            sequence = hiero_item.sequence()

        self.projectTreeDialog = ProjectTreeDialog(
            data=ftags, parent=_widget, sequence=sequence
        )

        self._tabWidget.insertTab(0, self.projectTreeDialog, 'ftrack')

        self.projectTreeDialog.export_project_button.hide()
        self.projectTreeDialog.close_button.hide()

        settings_widgets = self.createProcessorSettingsWidget(exportItems)
        for setting_widget, setting_name in settings_widgets:
            self._tabWidget.addTab(setting_widget, setting_name)

        # include_tags = [tag for tag, objecttype in self._tags if tag.name() in self._preset.properties()["includeTags"]]
        # exclude_tags = [tag for tag, objecttype in self._tags if tag.name() in self._preset.properties()["excludeTags"]]
        # tagsWidget = TagFilterWidget([tag for tag, objecttype in self._tags if objecttype in (hiero.core.TrackItem, )], include_tags, exclude_tags)
        # tagsWidget.setToolTip("Filter shot selection based on Shot Tags.\n+ Only include shots with these tags.\n- Exclude any shots with these tags.")
        # self._tabWidget.addTab(tagsWidget, 'tags')
        # tagsWidget.tagSelectionChanged.connect(self._tagsSelectionChanged)

    # DEBUG OVERRIDES
    def isTranscodeExport(self):
        result = super(FtrackShotProcessorUI, self).isTranscodeExport()
        self.logger.info('isTranscodeExport: {0}'.format(result))
        return result

    def findCompItems(self, items):
        comp_items =  super(FtrackShotProcessorUI, self).findCompItems(items)
        self.logger.info('Comp Items {0}'.format(comp_items))
        yield comp_items

    def validate(self,exportItems):
        is_valid = super(FtrackShotProcessorUI, self).validate(exportItems)
        self.logger.info('{0} are valid: {1}'.format(exportItems, is_valid))
        return is_valid

    def checkUnrenderedComps(self, exportItems):
        result = super(FtrackShotProcessorUI, self).checkUnrenderedComps(exportItems)
        self.logger.info('{0} Unrendered Comps: {1}'.format(exportItems, result))
        return result

    # def setTaskContent(self, preset):
    #     """ Get the UI for a task preset and add it in the 'Content' tab. """
    #     self.logger.info('setTaskContent with: {0}'.format(preset))
    #     return ShotProcessorUI.setTaskContent(
    #         self,
    #         preset,
    #     )

    # def refreshContent(self):
    #     self.logger.info('refreshContent')
    #     return ShotProcessorUI.refreshContent(
    #         self,
    #     )        
