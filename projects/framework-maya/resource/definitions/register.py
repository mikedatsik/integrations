# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack

import os
import logging
import ftrack_api
import functools
from ftrack_framework_core import constants, configure_logging
from ftrack_framework_core.definition import BaseDefinition

logger = logging.getLogger('ftrack_framework_maya_definition.register')


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that _register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    definition = BaseDefinition(api_object)
    definition.register()