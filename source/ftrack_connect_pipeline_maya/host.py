import functools
import logging

import maya.cmds as mc
import maya.mel as mm

from ftrack_connect_pipeline import constants

logger = logging.getLogger(
    __name__
)


def get_ftrack_menu(menu_name = 'ftrack_pipeline'):
    gMainWindow = mm.eval('$temp1=$gMainWindow')

    if mc.menu(
            menu_name,
            exists=True,
            parent=gMainWindow,
            label=menu_name
    ):
        menu = menu_name

    else:
        menu = mc.menu(
            menu_name,
            parent=gMainWindow,
            tearOff=False,
            label=menu_name
        )

    return menu


def mark_menu(hostid, event):
    client_hostid = event['data']['pipeline']['hostid']
    menu = get_ftrack_menu()
    if client_hostid == hostid:
        logger.info('client connected')
        mc.menu(menu, e=True, l='ftrack_pipeline (connected)')
        # TODO: Mark somehow the menu to be connected
    else:
        logger.info('client disconnected')
        mc.menu(menu, e=True, l='ftrack_pipeline')
        # TODO: remove marked menu


def notify_connected_client(session, hostid):
    event_handler = functools.partial(mark_menu, hostid)

    session.event_hub.subscribe(
        'topic={}'.format(
            constants.PIPELINE_CONNECT_CLIENT
        ),
        event_handler
    )



