#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.gui.codeeditor.editor import CodeEditor

from pmxpy.ipython import IPythonDock
from pmxpy.addons import PythonCheckerAddon

def registerPlugin(manager, descriptor):
    manager.registerComponent(IPythonDock)
    manager.registerComponent(PythonCheckerAddon, CodeEditor)
