# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import threading
import sys
import os

from PySide import QtCore

import ftrack_api


def asynchronous(method):
    '''Decorator to make a method asynchronous using its own thread.'''

    def wrapper(*args, **kwargs):
        '''Thread wrapped method.'''

        def exceptHookWrapper(*args, **kwargs):
            '''Wrapp method and pass exceptions to global excepthook.

            This is needed in threads because of
            https://sourceforge.net/tracker/?func=detail&atid=105470&aid=1230540&group_id=5470
            '''
            try:
                method(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                sys.excepthook(*sys.exc_info())

        thread = threading.Thread(
            target=exceptHookWrapper,
            args=args,
            kwargs=kwargs
        )
        thread.start()

    return wrapper


class Worker(QtCore.QThread):
    '''Perform work in a background thread.'''

    def __init__(self, function, args=None, kwargs=None, parent=None):
        '''Execute *function* in separate thread.

        *args* should be a list of positional arguments and *kwargs* a
        mapping of keyword arguments to pass to the function on execution.

        Store function call as self.result. If an exception occurs
        store as self.error.

        Example::

            try:
                worker = Worker(theQuestion, [42])
                worker.start()

                while worker.isRunning():
                    app = QtGui.QApplication.instance()
                    app.processEvents()

                if worker.error:
                    raise worker.error[1], None, worker.error[2]

            except Exception as error:
                traceback.print_exc()
                QtGui.QMessageBox.critical(
                    None,
                    'Error',
                    'An unhandled error occurred:'
                    '\\n{0}'.format(error)
                )

        '''
        super(Worker, self).__init__(parent=parent)
        self.function = function
        self.args = args or []
        self.kwargs = kwargs or {}
        self.result = None
        self.error = None

    def run(self):
        '''Execute function and store result.'''
        try:
            self.result = self.function(*self.args, **self.kwargs)
        except Exception:
            self.error = sys.exc_info()


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
        _invoker,
        InvokeEvent(fn, *args, **kwargs)
    )


def get_ftrack_entity():
    '''Return current ftrack entity.'''
    session = ftrack_api.Session()
    ftrack_entity = session.get(
        'Context', os.environ['FTRACK_CONTEXT_ID']
    )
    return ftrack_entity
