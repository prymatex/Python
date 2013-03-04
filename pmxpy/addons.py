#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from prymatex.qt import QtGui, QtCore
from prymatex import resources

from prymatex.gui.codeeditor.addons import CodeEditorAddon

from pmxpy.checker import CheckerThread, pyflakesChecker

class PythonCheckerAddon(CodeEditorAddon):
    def __init__(self, parent):
        CodeEditorAddon.__init__(self, parent)
        self.setObjectName(self.__class__.__name__)
        self.activated = self.enabled = False
        self.checkerThread = CheckerThread(self)
        self.checkerThread.errorFound.connect(self.on_checkerThread_errorFound)
        self.errors = {}

    def initialize(self, editor):
        CodeEditorAddon.initialize(self, editor)
        self.editor.registerTextCharFormatBuilder("line.warning", self.textCharFormat_warning_builder)
        self.editor.registerTextCharFormatBuilder("line.critical", self.textCharFormat_critical_builder)
        
        #Conect signals
        self.editor.document().contentsChange.connect(self.on_document_contentsChange)
        self.editor.syntaxChanged.connect(self.on_editor_syntaxChanged)
        
    def on_checkerThread_errorFound(self, number, offset, text):
        block = self.editor.document().findBlockByLineNumber(number)
        cursor = self.editor.newCursorAtPosition(block.position() + offset, block.position() + block.length())
        self.errors[cursor] = text
        self.editor.setExtraSelectionCursors("line.warning", self.errors.keys())

    def on_document_contentsChange(self, position, removed, added):
        if self.activated and self.enabled:
            print position, removed, added

    def on_editor_syntaxChanged(self, syntax):
        self.enabled = syntax.scopeName == "source.python"
        if self.activated and self.enabled:
            self.checkAllText()

    def checkAllText(self):
        lines = ['%s\n' % line for line in self.editor.toPlainText().splitlines()]
        self.checkerThread.checkAll(self.editor.filePath, lines)
        
            
    def textCharFormat_warning_builder(self):
        format = QtGui.QTextCharFormat()
        format.setFontUnderline(True)
        format.setUnderlineColor(QtCore.Qt.yellow)
        format.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
        format.setBackground(QtCore.Qt.transparent)
        format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        return format
        
    def textCharFormat_critical_builder(self):
        format = QtGui.QTextCharFormat()
        format.setFontUnderline(True)
        format.setUnderlineColor(QtCore.Qt.red)
        format.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
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

        def on_actionChecker_testEnabled(editor):
            instance = editor.findChild(cls, cls.__name__)
            return instance.enabled

        baseMenu = "Python"
        menuEntry = {
            'name': 'python',
            'text': 'Python',
            'items': [
                {
                    'name': 'checker',
                    'text': 'Checker',
                    'callback': on_actionChecker_toggled,
                    'checkable': True,
                    'testChecked': on_actionChecker_testChecked,
                    'testEnabled': on_actionChecker_testEnabled
                }
            ]
        }
        return { baseMenu: menuEntry }
