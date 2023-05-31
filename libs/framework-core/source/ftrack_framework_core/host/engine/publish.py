# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_framework_core.host.engine import BaseEngine


class PublisherEngine(BaseEngine):
    engine_type = 'publisher'

    def __init__(self, event_manager, host_types, host_id, asset_type_name):
        super(PublisherEngine, self).__init__(
            event_manager, host_types, host_id, asset_type_name
        )