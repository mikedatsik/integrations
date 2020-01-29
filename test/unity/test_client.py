from ftrack_connect_pipeline import client
from ftrack_connect_pipeline import constants


def test_initialise(event_manager):
    client_connection = client.Client(event_manager)
    assert client_connection.ui == [constants.UI]


def test_initialise_mutiple_ui(event_manager):
    client_connection = client.Client(event_manager, ui=['test'])
    assert client_connection.ui == [constants.UI, 'test']


def test_discover_host(event_manager, host):
    assert host
    client_connection = client.Client(event_manager)
    hosts = client_connection.discover_hosts()
    assert len(hosts) >= 1


def test_discover_host_callback(event_manager, host):

    def callback(hosts):
        assert len(hosts) >= 1

    assert host

    client_connection = client.Client(event_manager)
    client_connection.on_ready(callback)

