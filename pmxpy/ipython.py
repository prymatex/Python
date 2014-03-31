#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from prymatex.qt import QtGui, QtCore

from prymatex.core import PrymatexDock

from prymatex import resources

def event_loop(kernel):
    kernel.timer = QtCore.QTimer()
    kernel.timer.timeout.connect(kernel.do_one_iteration)
    kernel.timer.start(1000 * kernel._poll_interval)

def default_kernel_app():
    from IPython.zmq.ipkernel import IPKernelApp
    app = IPKernelApp.instance()
    app.initialize(['python', '--pylab=qt'])
    app.kernel.eventloop = event_loop
    return app

def default_kernel_manager(kernel_app):
    from IPython.lib.kernel import find_connection_file
    from IPython.frontend.qt.kernelmanager import QtKernelManager
    connection = find_connection_file(kernel_app.connection_file)
    kernelManager = QtKernelManager(connection_file=connection)
    kernelManager.load_connection_file()
    kernelManager.start_channels()
    #atexit.register(kernelManager.cleanup_connection_file)
    return kernelManager, connection

def console_widget(kernel_manager):
    from IPython.frontend.qt.console.ipython_widget import IPythonWidget
    console = IPythonWidget(gui_completion='droplist')
    console.kernel_manager = kernel_manager
    console.set_default_style(colors="linux")
    return console

class IPythonDock(PrymatexDock, QtGui.QDockWidget):
    SHORTCUT = "Shift+F4"
    ICON = resources.getIcon("applications-utilities")
    PREFERED_AREA = QtCore.Qt.BottomDockWidgetArea
    
    def __init__(self, **kwargs):
        super(PrymatexDock, self).__init__(**kwargs)
        self.setWindowTitle("IPython")
        self.setObjectName("IPythonDock")
        try:
            self.kernelApp = default_kernel_app()
            self.kernelManager, self.connection = default_kernel_manager(self.kernelApp)
            self.console = console_widget(self.kernelManager)
        except:
            # Gracefuly fail if iPython is not available
            from traceback import format_exc
            self.console = QtGui.QPlainTextEdit()
            self.console.setReadOnly(True)
            tb = format_exc()
            self.console.appendPlainText("IPython console disabled because of\n%s\nPlese install ipython >= 0.11" % tb)
        self.setWidget(self.console)
        
        self.kernelApp.shell.user_ns.update({"prymatex": self })
        
        self.kernelApp.start()
        
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
