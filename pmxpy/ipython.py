#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from prymatex.qt import QtGui, QtCore

from prymatex import resources
from prymatex.core.plugin.dock import PMXBaseDock
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
        self.setupConsole()

    def setupConsole(self):
        try:
            from IPython.frontend.qt.console.ipython_widget import IPythonWidget
            self.console = IPythonWidget()
            self.console.kernel_manager = self.application.kernelManager
            self.console.set_default_style(colors="linux")
        except ImportError:
            # Gracefuly fail if iPython is not available
            from traceback import format_exc
            self.console = QtGui.QPlainTextEdit()
            self.console.setReadOnly(True)
            tb = format_exc()
            self.console.appendPlainText("IPython console disabled because of\n%s\nPlese install ipython >= 0.11" % tb)
        self.setWidget(self.console)
