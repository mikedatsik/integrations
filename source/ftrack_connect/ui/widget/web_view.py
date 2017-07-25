# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from QtExt import QtGui, QtCore, QtWidgets, QtNetwork

try:
    from QtExt import QtWebKitWidgets as QtWebWidgets
    HAS_WEBKIT=True
except ImportError:
    from QtExt import QtWebEngineWidgets as QtWebWidgets
    HAS_WEBKIT=False
    # Create some aliases for old QtWebKit classes.
    QtWebWidgets.QWebPage = QtWebWidgets.QWebEnginePage
    QtWebWidgets.QWebView = QtWebWidgets.QWebEngineView


# TODO: Investigate why this import exists and remove it.
try:
    import hiero.core
except ImportError:
    pass

import ftrack

from ftrack_connect.connector import PersistentCookieJar, HelpFunctions


class Ui_WebView(object):
    '''Webview UI.'''

    def setupUi(self, WebView):
        '''Setup UI for *WebView*.'''
        WebView.setObjectName('WebView')
        WebView.resize(688, 555)
        self.horizontalLayout = QtWidgets.QHBoxLayout(WebView)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.WebViewView = QtWebWidgets.QWebView(WebView)
        font = QtGui.QFont()
        font.setFamily('Anonymous Pro')
        self.WebViewView.setFont(font)
        self.WebViewView.setUrl(QtCore.QUrl('about:blank'))
        self.WebViewView.setObjectName('WebViewView')
        self.horizontalLayout.addWidget(self.WebViewView)

        self.retranslateUi(WebView)
        QtCore.QMetaObject.connectSlotsByName(WebView)

    def retranslateUi(self, WebView):
        '''Translate text for *WebView*.'''
        WebView.setWindowTitle(
            QtWidgets.QApplication.translate(
                'WebView', 'Form', None, QtWidgets.QApplication.UnicodeUTF8
            )
        )


# TODO: Remove this widget and refactor Maya plugin to use WebView.
class WebViewWidget(QtWidgets.QWidget):
    '''Webview widget class.'''

    def __init__(self, parent, task=None):
        '''Instansiate web view widget.'''
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_WebView()
        self.ui.setupUi(self)

        self.webPage = QtWebWidgets.QWebPage()

        self.persCookieJar = PersistentCookieJar(self)
        self.persCookieJar.load()

        proxy = HelpFunctions.getFtrackQNetworkProxy()
        if proxy:
            if HAS_WEBKIT:
                self.webPage.networkAccessManager().setProxy(proxy)
            else:
                # TODO: This is a global per QApplication setting.
                # Changing it might not be a good idea?
                # QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
                pass

        self.ui.WebViewView.setPage(self.webPage)

    def sslErrorHandler(self, reply, errorList):
        '''Handle ssl error.'''
        reply.ignoreSslErrors()

    def setUrl(self, url):
        '''Set web view url to *url*.'''
        self.ui.WebViewView.load(QtCore.QUrl(url))


class WebView(QtWidgets.QFrame):
    '''Display information about selected entity.'''

    def __init__(self, parent=None, url=None):
        '''Initialise WebView with *parent* and *url*'''
        super(WebView, self).__init__(parent)
        self.setMinimumHeight(400)
        self.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Expanding
            )
        )

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self._webView = QtWebWidgets.QWebView()
        layout.addWidget(self._webView)

        self.set_url(url)

    def set_url(self, url):
        '''Load *url* and display result in web view.'''
        self._webView.load(QtCore.QUrl(url))

    def get_url(self):
        '''Return current url.'''
        url = self._webView.url().toString()
        if url in ('about:blank', ):
            return None

        return url

    def evaluateJavascript(self, javascript):
        '''Evaluate a Javascript script on the webpage's main frame.
        This method was moved from the QWebFrame class in QtWebkit
        to the QWebPage class in QtWebEngine.
        We wrap it here for convenience.
        '''
        if HAS_WEBKIT:
            self._webView.page().mainFrame().evaluateJavaScript(javascript)
        else:
            self._webView.page().evaluateJavaScript(javascript)
