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
        format = "line.warning" if text.startswith("W") else "line.critical"
        self.editor.extendExtraSelectionCursors(format, [ cursor ])

    def on_document_contentsChange(self, position, removed, added):
        if self.activated and self.enabled:
            print(position, removed, added)

    def on_editor_syntaxChanged(self, syntax):
        pass
        #self.enabled = self.pythonSelector.does_match(syntax.selector)
        #if self.activated and self.enabled:
        #    self.checkAllText()

    def checkAllText(self):
        plainText = self.editor.toPlainText()
        lines = ['%s\n' % line for line in plainText.splitlines()]
        self.checkerThread.checkAll(self.editor.filePath, lines)
        pyflakesChecker(plainText.encode("utf8","ignore"), self.editor.filePath)

    def textCharFormat_warning_builder(self):
        format = QtGui.QTextCharFormat()
        format.setFontUnderline(True)
        format.setUnderlineColor(QtCore.Qt.yellow)
        format.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)
        format.setBackground(QtCore.Qt.transparent)
        format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        return format

    #QTextCharFormat::NoUnderline
    #QTextCharFormat::SingleUnderline
    #QTextCharFormat::DashUnderline
    #QTextCharFormat::DotLine
    #QTextCharFormat::DashDotLine
    #QTextCharFormat::DashDotDotLine
    #QTextCharFormat::WaveUnderline
    #QTextCharFormat::SpellCheckUnderline

    def textCharFormat_critical_builder(self):
        format = QtGui.QTextCharFormat()
        format.setFontUnderline(True)
        format.setUnderlineColor(QtCore.Qt.red)
        format.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)
        format.setBackground(QtCore.Qt.transparent)
        format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        return format

    @classmethod
    def contributeToMainMenu(cls):
        def on_actionChecker_toggled(editor, checked):
            instance = editor.findChild(cls, cls.__name__)
            instance.activated = checked
            if instance.enabled and instance.activated:
                instance.checkAllText()

        def on_actionChecker_testChecked(editor):
            instance = editor.findChild(cls, cls.__name__)
            return instance is not None and instance.activated

        def on_actionCheckers_testEnabled(editor):
            instance = editor.findChild(cls, cls.__name__)
            return instance.enabled

        menuEntry = {
            'name': 'python',
            'text': 'P&ython',
            'items': [
                {
                    'name': 'checkers',
                    'text': 'Checkers',
                    'testEnabled': on_actionCheckers_testEnabled,
                    'items': [
                        {   'text': 'Pep8',
                            'checkable': True,
                            'callback': on_actionChecker_toggled,
                            'testChecked': on_actionChecker_testChecked,
                        },
                        {   'text': 'Pyflakes',
                            'checkable': True,
                        },
                        {'text': 'Fix errors'}]
                }
            ]
        }
        return { 'python': menuEntry }
