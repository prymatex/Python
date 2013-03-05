#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from prymatex.qt import QtCore

from .tools import Pep8Checker, StandardReport, StyleGuide

class CheckerThread(QtCore.QThread, StandardReport):
    errorFound = QtCore.pyqtSignal(int, int, str)
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        
        self.pep8style = StyleGuide(parse_argv=False, config_file=False)
        StandardReport.__init__(self, self.pep8style.options)
        self.selected = []

    def error(self, line_number, offset, text, check):
        if line_number not in self.selected:
            return
        self.errorFound.emit(line_number, offset, text)
        #return StandardReport.error(self, line_number, offset, text, check)

    def checkAll(self, filePath, lines):
        self._cancel = False
        self.filePath = filePath
        self.lines = lines
        self.selected = range(len(lines))
        #Start!
        self.start()

    def run(self):
        self.checker = Pep8Checker(self.filePath, lines = self.lines, report = self)
        self.checker.check_all()

    def cancel(self):
        self._cancel = True
