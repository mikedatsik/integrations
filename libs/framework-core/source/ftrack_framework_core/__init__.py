# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack.

from ._version import __version__

from ftrack_framework_core import constants
from ftrack_framework_core.configure_logging import configure_logging

configure_logging(__name__)
from ftrack_framework_core.constants.asset import *
