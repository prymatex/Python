#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from prymatex.qt import QtGui, QtCore

from prymatex.gui.codeeditor.addons import CodeEditorAddon

from pmxpy.checker import CheckerThread
from pmxpy.tools import pyflakesChecker

class PythonCheckerAddon(CodeEditorAddon):

    def __init__(self, parent):
        CodeEditorAddon.__init__(self, parent)
        self.setObjectName(self.__class__.__name__)
        self.activated = self.enabled = False
        self.checkerThread = CheckerThread(self)
        self.checkerThread.errorFound.connect(self.on_checkerThread_errorFound)
        self.errors = {}
        self.pythonSelector = self.application.supportManager.selectorFactory("source.python")

    def initialize(self, editor):
        CodeEditorAddon.initialize(self, editor)
        self.editor.registerTextCharFormatBuilder("line.warning", self.textCharFormat_warning_builder)
        self.editor.registerTextCharFormatBuilder("line.critical", self.textCharFormat_critical_builder)

        #Conect signals
        self.editor.document().contentsChange.connect(self.on_document_contentsChange)
        self.editor.syntaxChanged.connect(self.on_editor_syntaxChanged)

    def on_checkerThread_errorFound(self, number, offset, text):
        block = self.editor.document().findBlockByNumber(number - 1)
        errorStart = block.position() + offset
        errorEnd = errorStart + block.length() - offset
        cursor = self.editor.newCursorAtPosition(errorStart, errorEnd)
        self.errors.setdefault(block, []).append((cursor, text))
        print(text)
        # Solo muestro el primero si tiene muchos errores
        frmt = "line.warning" if text.startswith("W") else "line.critical"
        self.editor.extendExtraSelectionCursors(frmt, [ cursor ])

    def on_document_contentsChange(self, position, removed, added):
        if self.activated and self.enabled:
            print(position, removed, added)

    def on_editor_syntaxChanged(self, syntax):
        self.enabled = self.pythonSelector.does_match(self.editor.basicScope().scope)
        if self.activated and self.enabled:
            self.checkAllText()

    def checkAllText(self):
        plainText = self.editor.toPlainText()
        lines = ['%s\n' % line for line in plainText.splitlines()]
        self.checkerThread.checkAll(self.editor.filePath, lines)
        pyflakesChecker(plainText.encode("utf8","ignore"), self.editor.filePath)

    def textCharFormat_warning_builder(self):
        frmt = QtGui.QTextCharFormat()
        frmt.setFontUnderline(True)
        frmt.setUnderlineColor(QtCore.Qt.yellow)
        frmt.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)
        frmt.setBackground(QtCore.Qt.transparent)
        frmt.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        return frmt

    #QTextCharFormat::NoUnderline
    #QTextCharFormat::SingleUnderline
    #QTextCharFormat::DashUnderline
    #QTextCharFormat::DotLine
    #QTextCharFormat::DashDotLine
    #QTextCharFormat::DashDotDotLine
    #QTextCharFormat::WaveUnderline
    #QTextCharFormat::SpellCheckUnderline

    def textCharFormat_critical_builder(self):
        frmt = QtGui.QTextCharFormat()
        frmt.setFontUnderline(True)
        frmt.setUnderlineColor(QtCore.Qt.red)
        frmt.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)
        frmt.setBackground(QtCore.Qt.transparent)
        frmt.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        return frmt
    
    def on_actionChecker_toggled(self, checked):
        self.activated = checked
        if self.enabled and self.activated:
            self.checkAllText()

    @classmethod
    def contributeToMainMenu(cls):

        menuEntry = {
            'name': 'python',
            'text': 'P&ython',
            'testVisible': lambda checker: checker.pythonSelector.does_match(checker.editor.basicScope().scope),
            'items': [
                {
                    'name': 'checkers',
                    'text': 'Checkers',
                    'testEnabled': lambda checker: checker.enabled,
                    'items': [
                        {   'text': 'Pep8',
                            'checkable': True,
                            'callback': cls.on_actionChecker_toggled,
                            'testChecked': lambda checker: checker.activated,
                        },
                        {   'text': 'Pyflakes',
                            'checkable': True,
                        },
                        {'text': 'Fix errors'}]
                }
            ]
        }
        return { 'python': menuEntry }
