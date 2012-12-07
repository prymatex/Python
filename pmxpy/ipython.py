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
        self.kernelManager, self.connection = self.buildKernelManager()
        self.setupConsole()

    def setupConsole(self):
        try:
            from IPython.frontend.qt.console.ipython_widget import IPythonWidget
            self.console = IPythonWidget()
            self.console.kernel_manager = self.kernelManager
            self.console.set_default_style(colors="linux")
        except ImportError:
            # Gracefuly fail if iPython is not available
            from traceback import format_exc
            self.console = QtGui.QPlainTextEdit()
            self.console.setReadOnly(True)
            tb = format_exc()
            self.console.appendPlainText("IPython console disabled because of\n%s\nPlese install ipython >= 0.11" % tb)
        self.setWidget(self.console)

    def buildKernelManager(self):
        kernelManager = None
        try:
            from IPython.frontend.qt.kernelmanager import QtKernelManager
            kernelManager = QtKernelManager()
            kernelManager.start_kernel()
            kernelManager.start_channels()
            if hasattr(kernelManager, "connection_file"):
                ipconnection = kernelManager.connection_file
            else:
                shell_port = kernelManager.shell_address[1]
                iopub_port = kernelManager.sub_address[1]
                stdin_port = kernelManager.stdin_address[1]
                hb_port = kernelManager.hb_address[1]
                ipconnection = "--shell={0} --iopub={1} --stdin={2} --hb={3}".format(shell_port, iopub_port, stdin_port, hb_port)
        except ImportError as e:
            self.logger.warn("Warning: %s" % e)
            ipconnection = kernelManager = None
        return kernelManager, ipconnection
        
    def environmentVariables(self):
        env = {}
        if self.connection:
            env["PMX_IPYTHON_CONNECTION"] = self.connection
            env["PMX_IPYTHON_KERNEL"] = self.connection
        return env