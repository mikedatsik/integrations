import os
import re
import copy
from hiero.exporters.FnSubmission import Submission

import hiero.core.util
from hiero.exporters.FnTranscodeExporter import TranscodeExporter, TranscodePreset
from hiero.exporters.FnTranscodeExporterUI import TranscodeExporterUI
from hiero.exporters.FnExternalRender import NukeRenderTask

from ftrack_base import FtrackBasePreset, FtrackBase, FtrackBaseProcessor


class FtrackNukeRenderExporter(TranscodeExporter, FtrackBaseProcessor):

    def __init__(self, initDict):
        NukeRenderTask.__init__(self, initDict)
        FtrackBaseProcessor.__init__(self, initDict)

    def createTranscodeScript(self):
        # This code is taken from TranscodeExporter.__init__
        # in order to output the nuke file in the right place we need to override this.

        self._audioFile = None

        # Figure out the script location
        path = self.resolvedExportPath()
        dirname, filename = os.path.split(path)
        root, ext = os.path.splitext(filename)

        percentmatch = re.search('%\d+d', root)
        if percentmatch:
            percentpad = percentmatch.group()
            root = root.replace(percentpad, '')

        self._root = dirname + '/' + root.rstrip('#').rstrip('.')

        scriptExtension = '.nknc' if hiero.core.isNC() else '.nk'
        self._scriptfile = str(self._root + scriptExtension)

        self.logger.info('TranscodeExporter writing script to %s', self._scriptfile)

        self._renderTask = None
        if self._submission is not None:
            # Pass the frame range through to the submission.  This is useful for rendering through the frame
            # server, otherwise it would have to evaluate the script to determine it.
            start, end = self.outputRange()
            submissionDict = copy.copy(self._init_dict)
            submissionDict['startFrame'] = start
            submissionDict['endFrame'] = end

            # Create a job on our submission to do the actual rendering.
            self._renderTask = self._submission.addJob(Submission.kNukeRender, submissionDict, self._scriptfile)
            # ensure sub tasks do not create folders
            self._renderTask._makePath = FtrackBaseProcessor._makePath(self)

    def updateItem(self, originalItem, localtime):
        # We need to create the project structure right before spawning any job so we have access
        # to the ftrack structure and location.
        FtrackBaseProcessor.updateItem(self, originalItem, localtime)
        self.createTranscodeScript()

    def finishTask(self):
        FtrackBaseProcessor.finishTask(self)
        TranscodeExporter.finishTask(self)

    def _makePath(self):
        # disable making file paths
        FtrackBaseProcessor._makePath(self)


class FtrackNukeRenderExporterPreset(TranscodePreset, FtrackBasePreset):
    def __init__(self, name, properties):
        TranscodePreset.__init__(self, name, properties)
        FtrackBasePreset.__init__(self, name, properties)
        self._parentType = FtrackNukeRenderExporter

        # Update preset with loaded data
        self.properties().update(properties)

    def set_ftrack_properties(self, properties):
        FtrackBasePreset.set_ftrack_properties(self, properties)
        properties = self.properties()
        properties.setdefault('ftrack', {})

        # add placeholders for default ftrack defaults
        self.properties()['ftrack']['task_type'] = 'Editing'
        self.properties()['ftrack']['asset_type_code'] = 'img'
        self.properties()['ftrack']['component_name'] = 'main'
        self.properties()['ftrack']['component_pattern'] = '.####.{ext}'

    def addUserResolveEntries(self, resolver):
        FtrackBasePreset.addFtrackResolveEntries(self, resolver)


class FtrackNukeRenderExporterUI(TranscodeExporterUI, FtrackBase):
    def __init__(self, preset):
        TranscodeExporterUI.__init__(self, preset)
        FtrackBase.__init__(self, preset)

        self._displayName = 'Ftrack Nuke Render'
        self._taskType = FtrackNukeRenderExporter


hiero.core.taskRegistry.registerTask(FtrackNukeRenderExporterPreset, FtrackNukeRenderExporter)
hiero.ui.taskUIRegistry.registerTaskUI(FtrackNukeRenderExporterPreset, FtrackNukeRenderExporterUI)
