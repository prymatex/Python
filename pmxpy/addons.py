#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from prymatex.qt import QtGui, QtCore
from prymatex import resources

from prymatex.gui.codeeditor.addons import CodeEditorAddon

from pmxpy.checker import CheckerThread

class PythonCheckerAddon(CodeEditorAddon):
    def __init__(self, parent):
        CodeEditorAddon.__init__(self, parent)
        self.checkerThread = CheckerThread(self)
        self.checkerThread.errorFound.connect(self.on_checkerThread_errorFound)
        self.errors = {}
        
    def initialize(self, editor):
        CodeEditorAddon.initialize(self, editor)
        self.editor.registerTextCharFormatBuilder("line.warning", self.textCharFormat_warning_builder)
        self.editor.registerTextCharFormatBuilder("line.critical", self.textCharFormat_critical_builder)
        
        #Conect signals
        #self.editor.document().contentsChange.connect(self.on_document_contentsChange)
        #self.editor.syntaxReady.connect(self.on_editor_syntaxReady)
        
    def on_checkerThread_errorFound(self, number, offset, text):
        self.errors[number - 1] = (offset, text)

    def on_document_contentsChange(self, position, removed, added):
        print position, removed, added
        
    def on_editor_syntaxReady(self):
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
            if instance is not None:
                instance.setVisible(checked)

        def on_actionChecker_testChecked(editor):
            instance = editor.findChild(cls, cls.__name__)
            return instance is not None and instance.isVisible()

        def on_actionChecker_testEnabled(editor):
            print editor.syntax().scopeName
            return editor.syntax().scopeName == "source.python"

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
