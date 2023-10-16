# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack

from ftrack_framework_photoshop import bootstrap_integration, run_integration

# Initialise the Photoshop Framework Python standalone part.
bootstrap_integration(
    panel_launchers=[
        {
            "name": "publish",
            "label": "PUBLISHER",
            "dialog_name": "framework_publisher_dialog",
            "image": "publish",
        }
    ],
    extension_packages=[
        'ftrack_framework_common_engines',
        'ftrack_framework_common_plugins',
        'ftrack_framework_common_schemas',
        'ftrack_framework_common_tool_configs',
        'ftrack_framework_common_widgets',
    ],
)

# Run until Photoshop is closed.
run_integration()