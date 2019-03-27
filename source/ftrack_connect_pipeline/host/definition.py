# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack


import logging
import ftrack_api
import json

from QtExt import QtCore

from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline import schema
from ftrack_connect_pipeline.event import EventManager
logger = logging.getLogger(__name__)


class BaseDefinitionManager(object):

    def result(self, *args, **kwargs):
        '''Return the result definitions.'''
        return self.__registry

    def __init__(self, session, schema_type, validator):
        '''Initialise the class with ftrack *session* and *context_type*'''
        super(BaseDefinitionManager, self).__init__()

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.__registry = {}
        self.session = session
        self.event_manager = EventManager(self.session)
        self._validator = validator
        self._schema_type = schema_type
        self.register(schema_type)

    def validate(self, data):
        '''validate definitions against schema, coming from *data*.'''
        try:
            self._validator(data)
        except Exception as error:
            self.logger.warn(error)
            return False

        return True

    def on_register_definition(self, event):
        '''Register definition coming from *event* and store them.'''
        raw_result = event['data']
        result = None
        try:
            result = json.loads(raw_result)
        except Exception as error:
            self.logger.warning(
                'Failed to read definition {}, error :{} for {}'.format(
                    raw_result, error, self._schema_type
                )
            )

        if not result or not self.validate(result):
            return

        name = result['name']
        if name in self.__registry:
            self.logger.warning('{} already registered!'.format(name))
            return

        self.logger.info('Registering {}'.format(result['name']))
        self.__registry[name] = result

    def register(self, schema_type):
        '''register package'''

        event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_REGISTER_TOPIC,
            data={
                'pipeline': {
                    'type': str(schema_type)
                }
            }
        )

        self.event_manager.publish(
            event,
            self.on_register_definition,
            remote=True
        )


class PackageDefinitionManager(BaseDefinitionManager):
    '''Package schema manager class.'''

    def __init__(self, session):
        '''Initialise the class with ftrack *session* and *context_type*'''
        super(PackageDefinitionManager, self).__init__(session, 'package', schema.validate_package)


class LoaderDefinitionManager(BaseDefinitionManager):

    @property
    def packages(self):
        '''return available packages definitions.'''
        return self.package_manager.result()

    def __init__(self, package_manager):
        '''Initialise the class with ftrack *session* and *context_type*'''
        super(LoaderDefinitionManager, self).__init__(package_manager.session, 'loader', schema.validate_loader)
        self.package_manager = package_manager

    def validate(self, data):
        schema_validation = super(LoaderDefinitionManager, self).validate(data)
        # TODO validate consistency of components against package definition also discover plugins
        return schema_validation


class PublisherDefinitionManager(BaseDefinitionManager):

    @property
    def packages(self):
        '''return available packages definitions.'''
        return self.package_manager.result()

    def __init__(self, package_manager):
        '''Initialise the class with ftrack *session* and *context_type*'''
        super(PublisherDefinitionManager, self).__init__(package_manager.session, 'publisher', schema.validate_publisher)
        self.package_manager = package_manager

    def validate(self, data):
        schema_validation = super(PublisherDefinitionManager, self).validate(data)
        package_validation = data['package'] in self.packages #  check to package in use is registered

        # TODO validate consistency of components against package definition also discover plugins
        return all([schema_validation, package_validation])


class DefintionManager(QtCore.QObject):
    '''class wrapper to contain all the definition managers.'''

    def __init__(self, session, hostid):
        self.session = session
        self.packages = PackageDefinitionManager(session)
        self.loaders = LoaderDefinitionManager(self.packages)
        self.publishers = PublisherDefinitionManager(self.packages)

        self.session.event_hub.subscribe(
            'topic={} and data.pipeline.type=publisher and data.pipeline.hostid={}'.format(constants.PIPELINE_REGISTER_DEFINITION_TOPIC, hostid),
            self.publishers.result
        )

        self.session.event_hub.subscribe(
            'topic={} and data.pipeline.type=loader and data.pipeline.hostid={}'.format(constants.PIPELINE_REGISTER_DEFINITION_TOPIC, hostid),
            self.loaders.result
        )

