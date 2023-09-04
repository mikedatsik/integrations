# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack

# Valid Categories
#: Step Category.
STEP = 'step'
#: Stage Category.
STAGE = 'stage'
#: Plugin Category.
PLUGIN = 'plugin'

CATEGORIES = [STEP, STAGE, PLUGIN]

# Common steps.
#: Contexts step group.
CONTEXTS = 'contexts'
#: Finalizers step group.
FINALIZERS = 'finalizers'
#: Components step group.
COMPONENTS = 'components'

# TODO: this should be used in the definition_object, so a client can override
#  it with a new definition that contains other steps. Or better, should be
#  read from the schema directly (So the definition_objects provides it reading
#  from the schema).
STEP_GROUPS = [CONTEXTS, COMPONENTS, FINALIZERS]

# Common steps types.
#: Contexts step type.
CONTEXT = 'context'
#: Finalizers step type.
FINALIZER = 'finalizer'
#: Components step type.
COMPONENT = 'component'

# Component stages.
#: Collector component stage name.
COLLECTOR = 'collector'
#: Validator component stage name.
VALIDATOR = 'validator'
#: Output component stage name.
EXPORTER = 'exporter'
#: Importer component stage name.
IMPORTER = 'importer'
#: Post_import component stage name.
POST_IMPORTER = 'post_importer'

# Common definition types.
SCHEMA = 'schema'
#: Opener client and its definition.
OPENER = 'opener'
#: Loader client and its definition used with assembler
LOADER = 'loader'
#: Publisher client and its definition.
PUBLISHER = 'publisher'
# Asset manager
ASSET_MANAGER = 'asset_manager'
# Resolver
RESOLVER = 'resolver'
# Log viewer dialog
LOG_VIEWER = 'log_viewer'

DEFINITION_TYPES = [OPENER, LOADER, PUBLISHER, ASSET_MANAGER, RESOLVER]