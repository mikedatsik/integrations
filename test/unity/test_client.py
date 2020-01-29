import functools
from ftrack_connect_pipeline import client
from ftrack_connect_pipeline import constants


def test_initialise(event_manager):
    client_connection = client.Client(event_manager)
    assert client_connection.ui == [constants.UI]


def test_initialise_mutiple_ui(event_manager):
    client_connection = client.Client(event_manager, ui=['test'])
    assert client_connection.ui == [constants.UI, 'test']


def test_discover_host(host, event_manager):

    client_connection = client.Client(event_manager)
    hosts = client_connection.discover_hosts()
    assert len(hosts) == 1


def test_discover_host_callback(host, event_manager):

    def callback(hosts):
        assert len(hosts) == 1

    client_connection = client.Client(event_manager)
    client_connection.on_ready(callback)
    assert client_connection.hosts


def test_run_host_callback(host, event_manager, temporary_image):

    def callback(hosts):
        host = hosts[0]

        task = host.session.query(
            'select name from Task where project.name is "pipelinetest"'
        ).first()

        schema = task['project']['project_schema']
        task_status = schema.get_statuses('Task')[0]

        publisher = host.definitions['publishers'][0]
        print 'publisher', publisher

        publisher['contexts']['plugins'][0]['options']['context_id'] = task['id']
        publisher['contexts']['plugins'][0]['options']['asset_name'] = 'PipelineAsset'
        publisher['contexts']['plugins'][0]['options']['comment'] = 'A new hope'
        publisher['contexts']['plugins'][0]['options']['status_id'] = task_status['id']
        publisher['components'][0]['stages'][0]['plugins'][0]['options']['path'] = temporary_image
        host.run(publisher)

    client_connection = client.Client(event_manager)
    client_connection.on_ready(callback)


