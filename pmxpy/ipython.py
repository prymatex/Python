#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from prymatex.qt import QtGui, QtCore

from prymatex.core import PMXBaseDock

from prymatex import resources
from prymatex.utils.i18n import ugettext as _

class IPythonDock(QtGui.QDockWidget, PMXBaseDock):
    SHORTCUT = "Shift+F4"
    ICON = resources.getIcon("applications-utilities")
    PREFERED_AREA = QtCore.Qt.BottomDockWidgetArea
    
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        PMXBaseDock.__init__(self)
        self.setWindowTitle(_("IPython"))
        self.setObjectName(_("IPythonDock"))
        self.kernelApp = self.buildKernelApp()
        self.kernelManager, self.connection = self.buildKernelManager(self.kernelApp)
        self.setupConsole(self.kernelManager)
        
    def _event_loop(self, kernel):
        kernel.timer = QtCore.QTimer()
        kernel.timer.timeout.connect(kernel.do_one_iteration)
        kernel.timer.start(1000 * kernel._poll_interval)

    def buildKernelApp(self):
        from IPython.zmq.ipkernel import IPKernelApp
        app = IPKernelApp.instance()
        app.initialize(['python', '--pylab=qt'])
        app.kernel.eventloop = self._event_loop
        return app
    
    def buildKernelManager(self, kernel):
        connection = kernelManager = None
        try:
            from IPython.lib.kernel import find_connection_file
            from IPython.frontend.qt.kernelmanager import QtKernelManager
            connection = find_connection_file(kernel.connection_file)
            kernelManager = QtKernelManager(connection_file=connection)
            kernelManager.load_connection_file()
            kernelManager.start_channels()
            atexit.register(kernelManager.cleanup_connection_file)
        except:
            pass
        return kernelManager, connection
    
    def setupConsole(self, manager):
        try:
            from IPython.frontend.qt.console.rich_ipython_widget import RichIPythonWidget
            from IPython.utils.traitlets import TraitError
            try: # Ipython v0.13
                self.console = RichIPythonWidget(gui_completion='droplist')
            except TraitError:  # IPython v0.12
                self.console = RichIPythonWidget(gui_completion=True)
            self.console.kernel_manager = manager
            self.console.set_default_style(colors="linux")
        except ImportError:
            # Gracefuly fail if iPython is not available
            from traceback import format_exc
            self.console = QtGui.QPlainTextEdit()
            self.console.setReadOnly(True)
            tb = format_exc()
            self.console.appendPlainText("IPython console disabled because of\n%s\nPlese install ipython >= 0.11" % tb)
        self.setWidget(self.console)
    
    def environmentVariables(self):
        env = {}
        if self.connection:
            env["PMX_IPYTHON_CONNECTION"] = self.connection
            env["PMX_IPYTHON_KERNEL"] = self.connection
        return env
        
    @classmethod
    def contributeToMainMenu(cls):
        menuEntry = {
            'name': 'python',
            'text': 'P&ython',
            'items': [
                {
                    'name': 'ipython',
                    'text': 'IPython',
                    'items': [
                        {'text': 'Option1' },
                        {'text': 'Option2' },
                        {'text': 'Option3'}]
                }
            ]
        }
        return { 'python': menuEntry }
