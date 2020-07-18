# Copyright (c) 2020 FlyingSamson.
# CameraMemory is released under the terms of the AGPLv3 or higher.

from UM.Application import Application
from UM.Logger import Logger
from UM.Math.Matrix import Matrix
from UM.Qt.QtApplication import QtApplication
from UM.Extension import Extension

from PyQt5 import QtCore
from PyQt5.QtCore import QEvent, QObject

import os
import json
import platform
from numpy import array, float32


class CameraMemory(Extension, QObject):

  def __init__(self):
    Extension.__init__(self)
    QObject.__init__(self)
    self._scene = Application.getInstance().getController().getScene()
    self._CTRL = QtCore.Qt.ControlModifier if platform.system() == "Darwin" \
                                        else QtCore.Qt.ControlModifier
    self._SAVE_MODIFIER = self._CTRL | QtCore.Qt.AltModifier
    self._RESTORE_MODIFIER = self._CTRL
    self._cameraTrafos = [None] * 10
    self._readTrafosFromJson()

    QtApplication.getInstance().installEventFilter(self)

  def __del__(self):
    self._saveTrafosToJson()

  def _saveCamera(self, idx):
    camera = self._scene.getActiveCamera()
    if not camera or not camera.isEnabled():
      Logger.log("d", "No camera available")
      return
    self._cameraTrafos[idx] = camera.getLocalTransformation()
    # update json file
    self._saveTrafosToJson()

  def _restoreCamera(self, idx):
    camera = self._scene.getActiveCamera()
    if not camera or not camera.isEnabled():
      Logger.log("d", "No camera available")
      return
    if self._cameraTrafos[idx] is not None:
      camera.setTransformation(self._cameraTrafos[idx])
    else:
      Logger.log("d", "No camera position for idx " + str(idx))

  def _saveTrafosToJson(self):
    Logger.log("d", "Saving trafos to json")
    dict = {}
    dict["cameras"] = []
    for trafoIdx, trafo in enumerate(self._cameraTrafos):
      dict["cameras"].append({
        "CameraId": trafoIdx,
        "Trafo": "None" if trafo is None else trafo.getData().__repr__()
      })
    try:
      with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "memory.json"),
                'w', encoding="utf-8") as f:
        json.dump(dict, f, indent=2)
    except Exception as e:
      Logger.log("e", "Exception writing camera memory to json file %s", e)

  def _readTrafosFromJson(self):
    Logger.log("d", "Reading trafos from json")
    try:
      with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "memory.json"),
                'r', encoding="utf-8") as f:
        trafos = json.load(f)["cameras"]
        for trafo in trafos:
          trafoData = eval(trafo["Trafo"])
          self._cameraTrafos[trafo["CameraId"]] = None if trafoData is None else Matrix(trafoData)
    except FileNotFoundError:
      Logger.log("d", "Json file does not (yet) exist")
    except Exception as e:
      Logger.log("e", "Exception reading camera memory from json file %s", e)

  def _parseNumberKey(self, key):
    numberKey = None
    if key == QtCore.Qt.Key_0:
      numberKey = 0
    elif key == QtCore.Qt.Key_1:
      numberKey = 1
    elif key == QtCore.Qt.Key_2:
        numberKey = 2
    elif key == QtCore.Qt.Key_3:
      numberKey = 3
    elif key == QtCore.Qt.Key_4:
        numberKey = 4
    elif key == QtCore.Qt.Key_5:
      numberKey = 5
    elif key == QtCore.Qt.Key_6:
        numberKey = 6
    elif key == QtCore.Qt.Key_7:
      numberKey = 7
    elif key == QtCore.Qt.Key_8:
        numberKey = 8
    elif key == QtCore.Qt.Key_9:
        numberKey = 9
    return numberKey

  def eventFilter(self, obj, event):
    if event.type() == QEvent.KeyPress:
      numberKey = self._parseNumberKey(event.key())

      if numberKey is None:
        return False

      modifiers = event.modifiers()

      if modifiers == self._SAVE_MODIFIER:
        Logger.log("d", "Saving camera at idx " + str(numberKey))
        self._saveCamera(numberKey)
        return True
      elif modifiers == self._RESTORE_MODIFIER:
        Logger.log("d", "Restoring camera at idx " + str(numberKey))
        self._restoreCamera(numberKey)
        return True

    return False
