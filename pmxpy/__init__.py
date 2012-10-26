#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.gui.codeeditor.editor import CodeEditor

from pmxpy.ipython import IPythonDock
from pmxpy.addons import PepCheckerSideBarAddon

def registerPlugin(manager):
    manager.registerDocker(IPythonDock)
    manager.registerAddon(CodeEditor, PepCheckerSideBarAddon)
