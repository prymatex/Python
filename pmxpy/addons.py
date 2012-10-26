#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from prymatex.qt import QtGui, QtCore

from prymatex.gui.codeeditor.sidebar import SideBarWidgetAddon

class PepCheckerSideBarAddon(QtGui.QWidget, SideBarWidgetAddon):
    ALIGNMENT = QtCore.Qt.AlignLeft
    
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setFixedWidth(10)
        
    def initialize(self, editor):
        SideBarWidgetAddon.initialize(self, editor)
        self.background = self.editor.colours['selection']
        self.editor.themeChanged.connect(self.updateColours)
        
    def updateColours(self):
        self.background = self.editor.colours['selection']
        self.repaint(self.rect())

    @classmethod
    def contributeToMainMenu(cls):
        def on_actionShowErrors_toggled(editor, checked):
            instance = editor.addonByClass(cls)
            instance.setVisible(checked)

        def on_actionShowErrors_testChecked(editor):
            instance = editor.addonByClass(cls)
            return instance.isVisible()
        
        baseMenu = ("View", cls.ALIGNMENT == QtCore.Qt.AlignRight and "Right Gutter" or "Left Gutter")
        menuEntry = {'text': "Pep Checker",
            'callback': on_actionShowErrors_toggled,
            'shortcut': 'Alt+F10',
            'checkable': True,
            'testChecked': on_actionShowErrors_testChecked }
        return { baseMenu: menuEntry} 

    def paintEvent(self, event):
        font_metrics = QtGui.QFontMetrics(self.editor.font)
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

            block = block.next()

        painter.end()
        QtGui.QWidget.paintEvent(self, event)
