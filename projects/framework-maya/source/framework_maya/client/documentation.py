# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack
import os

import framework_maya
from framework_qt.client import documentation


class MayaQtDocumentationClientWidget(
    documentation.QtDocumentationClientWidget
):
    '''Maya documentation client'''

    documentation_url = (
        "https://help.ftrack-studio.backlight.co/hc/en-us/articles/13129843823767"
    )
