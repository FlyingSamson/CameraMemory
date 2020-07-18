from . import CameraMemory


def getMetaData():
    return {}


def register(app):
    return {"extension": CameraMemory.CameraMemory()}
