#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.gui.codeeditor.editor import CodeEditor

from pmxpy.ipython import IPythonDock
from pmxpy.addons import CheckerSideBarAddon

def registerPlugin(manager):
    manager.registerComponent(IPythonDock)
    #manager.registerAddon(CodeEditor, CheckerSideBarAddon)
