# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack
import os

import ftrack_framework_houdini
from ftrack_framework_qt.client import documentation


class HoudiniQtDocumentationClientWidget(
    documentation.QtDocumentationClientWidget
):
    '''Houdini documentation client'''

    documentation_url = "https://help.ftrack-studio.backlight.co/hc/en-us/articles/13129964555543"