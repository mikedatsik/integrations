# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin

class EnvContextPlugin(plugin.LoaderContextPlugin):
    plugin_name = 'context.load'

    def run(self, context=None, data=None, options=None):
        output = self.output
        output.update(options)
        return output


def register(api_object, **kw):
    plugin = EnvContextPlugin(api_object)
    plugin.register()
