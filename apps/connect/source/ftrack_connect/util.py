# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import os
from queue import SimpleQueue, Empty
import subprocess
import sys
import threading

import requests

from ftrack_connect.qt import QtCore


def open_directory(path):
    '''Open a filesystem directory from *path* in the OS file browser.

    If *path* is a file, the parent directory will be opened. Depending on OS
    support the file will be pre-selected.

    .. note::

        This function does not support file sequence expressions. The path must
        be either an existing file or directory that is valid on the current
        platform.

    '''
    if os.path.isfile(path):
        directory = os.path.dirname(path)
    else:
        directory = path

    if sys.platform == 'win32':
        # In order to support directories with spaces, the start command
        # requires two quoted args, the first is the shell title, and
        # the second is the directory to open in. Using string formatting
        # here avoids the auto-escaping that python introduces, which
        # seems to fail...
        subprocess.Popen('start "" "{0}"'.format(directory), shell=True)

    elif sys.platform == 'darwin':
        if os.path.isfile(path):
            # File exists and can be opened with a selection.
            subprocess.Popen(['open', '-R', path])

        else:
            subprocess.Popen(['open', directory])

    else:
        subprocess.Popen(['xdg-open', directory])


# Invoke function in main UI thread.
# Taken from:
# http://stackoverflow.com/questions/10991991/pyside-easier-way-of-updating-gui-from-another-thread/12127115#12127115


class InvokeEvent(QtCore.QEvent):
    '''Event.'''

    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, fn, *args, **kwargs):
        '''Invoke *fn* in main thread.'''
        QtCore.QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class Invoker(QtCore.QObject):
    '''Invoker.'''

    def event(self, event):
        '''Call function on *event*.'''
        event.fn(*event.args, **event.kwargs)

        return True


_invoker = Invoker()


def invoke_in_main_thread(fn, *args, **kwargs):
    '''Invoke function *fn* with arguments.'''
    QtCore.QCoreApplication.postEvent(
        _invoker, InvokeEvent(fn, *args, **kwargs)
    )

class UrlLatencyChecker:
    MAX_TIMEOUT = 10

    def __init__(self, urls: list[str]):
        self.urls = urls
    
    @staticmethod
    def _send_request(url: str):
        resp = requests.head(url)
        resp.raise_for_status()
        resp.close()
    
    def _check(cls, url: str, q: SimpleQueue):
        cls._send_request(url)

        q.put_nowait(url)

    def run(self) -> str:
        q = SimpleQueue()

        for url in self.urls:
            t = threading.Thread(target=self._check, args=(url, q), daemon=True)
            t.start()
        
        try:
            return q.get(timeout=self.MAX_TIMEOUT)
        except Empty:
            return self.urls[0]
