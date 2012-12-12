#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from prymatex.qt import QtGui, QtCore
from prymatex import resources

from prymatex.gui.codeeditor.sidebar import SideBarWidgetAddon
from pmxpy.checker import CheckerThread

class CheckerSideBarAddon(QtGui.QWidget, SideBarWidgetAddon):
    ALIGNMENT = QtCore.Qt.AlignLeft
    WIDTH = 10
    
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.warningImage = resources.getImage("SP_MessageBoxWarning", self.WIDTH)
        self.criticalImage = resources.getImage("SP_MessageBoxCritical", self.WIDTH)
        self.checkerThread = CheckerThread(self)
        self.checkerThread.errorFound.connect(self.on_checkerThread_errorFound)
        self.errors = {}
        self.setFixedWidth(self.WIDTH)
        
    def initialize(self, editor):
        SideBarWidgetAddon.initialize(self, editor)
        self.background = self.editor.colours['gutter'] if 'gutter' in self.editor.colours else self.editor.colours['background']
        self.editor.registerTextCharFormatBuilder("line.warning", self.textCharFormat_warning_builder)
        self.editor.registerTextCharFormatBuilder("line.critical", self.textCharFormat_critical_builder)
        
        #Conect signals
        self.editor.themeChanged.connect(self.on_editor_updateColours)
        self.editor.document().contentsChange.connect(self.on_document_contentsChange)
        self.editor.syntaxReady.connect(self.on_editor_syntaxReady)
        
    def on_checkerThread_errorFound(self, number, offset, text):
        self.errors[number - 1] = (offset, text)

    def on_editor_updateColours(self):
        self.background = self.editor.colours['gutter'] if 'gutter' in self.editor.colours else self.editor.colours['background']
        self.repaint(self.rect())

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
        def on_actionShowErrors_toggled(editor, checked):
            instance = editor.addonByClass(cls)
            instance.setVisible(checked)

        def on_actionShowErrors_testChecked(editor):
            instance = editor.addonByClass(cls)
            return instance.isVisible()
        
        baseMenu = ("View", cls.ALIGNMENT == QtCore.Qt.AlignRight and "Right Gutter" or "Left Gutter")
        menuEntry = {'text': "Python checker",
            'callback': on_actionShowErrors_toggled,
            'checkable': True,
            'testChecked': on_actionShowErrors_testChecked }
        return { baseMenu: menuEntry} 

    def paintEvent(self, event):
        font_metrics = self.editor.fontMetrics()
        page_bottom = self.editor.viewport().height()
       
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), self.background)

        block = self.editor.firstVisibleBlock()
        viewport_offset = self.editor.contentOffset()
        
        while block.isValid():
            # The top left position of the block in the document
            position = self.editor.blockBoundingGeometry(block).topLeft() + viewport_offset
            # Check if the position of the block is out side of the visible area
            if position.y() > page_bottom:
                break

            if block.isVisible() and block.blockNumber() in self.errors:
                painter.drawPixmap(0,
                    round(position.y()) + font_metrics.ascent() + font_metrics.descent() - self.warningImage.height(),
                    self.warningImage)
            block = block.next()
            
        painter.end()
        QtGui.QWidget.paintEvent(self, event)
