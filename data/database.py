import pickle
import json
import os
from data.entity import Entity
from PySide2 import QtCore
from PySide2.QtGui import QVector3D, QColor, QQuaternion

class Database(QtCore.QObject):

    onUndoSignal = QtCore.Signal()
    onRedoSignal = QtCore.Signal()
    
    onFpsCameraSignal = QtCore.Signal()
    onOrbitCameraSignal = QtCore.Signal()

    onEntitySelectedSignal = QtCore.Signal()
    onEntityDestroyedSignal = QtCore.Signal(Entity)
    onEntityCreatedSignal = QtCore.Signal(Entity)
    onEntityRenamedSignal = QtCore.Signal(Entity, str)
    onEntityMovedSignal = QtCore.Signal(Entity, QVector3D)
    onEntityRotatedSignal = QtCore.Signal(Entity, QQuaternion)
    onEntityColorChangedSignal = QtCore.Signal(Entity, QColor)
    onEntityCubeDimensionsChangedSignal = QtCore.Signal(Entity, QVector3D)
    onEntitySphereDimensionsChangedSignal = QtCore.Signal(Entity, float)

    onHistoryChange = QtCore.Signal()


    def __init__(self):
        super(Database, self).__init__()

        # Try to load data from cache (as to resume from a shutdown)
        root = None
        if os.path.isfile("cache.bin"):
            f = open("cache.bin", "r")
            try:
                j = json.load(f)
                root = Entity.fromDict(j)
            except:
                pass
            f.close()
        
        if root == None:
            root = Entity()
            root.name = "root"

        self.root = root
        self.selectedEntity = None
        self.history = []

    def fpsCamera(self):
        self.onFpsCameraSignal.emit()

    def orbitCamera(self):
        self.onOrbitCameraSignal.emit()

    def entitySelected(self, newlySelectedEntity):
        self.selectedEntity = newlySelectedEntity
        print("Selecting: ", self.selectedEntity.name)
        self.onEntitySelectedSignal.emit()

    def entityDestroyed(self, entityToDestroy):
        print("Destroying: ", entityToDestroy.name)
        entityToDestroy.setParent(None)
        if entityToDestroy == self.selectedEntity:
            self.selectedEntity = None
        self.onEntityDestroyedSignal.emit(entityToDestroy)
        self.backup()

    def entityCreated(self, createdEntity):
        print("Creating: ", createdEntity.name)
        if self.selectedEntity != None:
            createdEntity.setParent(self.selectedEntity)
        else:
            createdEntity.setParent(self.root)
        self.onEntityCreatedSignal.emit(createdEntity)
        self.backup()

    def entityRenamed(self, renamedEntity, newName):
        print("Renaming entity: ", renamedEntity.name, " -> ", newName)
        renamedEntity.name = newName
        self.onEntityRenamedSignal.emit(renamedEntity, newName)
        self.backup()

    def entityMoved(self, movedEntity, newPosition):
        print("Moving entity: (", movedEntity.name, ") ", movedEntity.position, " -> ", newPosition)
        movedEntity.position = newPosition
        self.onEntityMovedSignal.emit(movedEntity, newPosition)
        self.backup()

    def entityRotated(self, rotatedEntity, newRotation):
        print("Rotating entity: (", rotatedEntity.name, ") ", rotatedEntity.rotation, " -> ", newRotation)
        rotatedEntity.rotation = newRotation
        self.onEntityRotatedSignal.emit(rotatedEntity, newRotation)
        self.backup()    

    def entityColorChanged(self, changedEntity, newColor):
        print("Changing entity color: (", changedEntity.name, ") ", changedEntity.color, " -> ", newColor)
        changedEntity.color = newColor
        self.onEntityColorChangedSignal.emit(changedEntity, newColor)
        self.backup()

    def entityCubeDimensionsChanged(self, changedEntity, newDimensions):
        print("Changing cube dimensions: (", changedEntity.name, ") ", changedEntity.dimensions, " -> ", newDimensions)
        changedEntity.dimensions = newDimensions
        self.onEntityCubeDimensionsChangedSignal.emit(changedEntity, newDimensions)
        self.backup()

    def entitySphereRadiusChanged(self, changedEntity, newRadius):
        print("Changigng sphere radius: (", changedEntity.name, ") ", changedEntity.radius, " -> ", newRadius)
        changedEntity.radius = newRadius
        self.onEntitySphereDimensionsChangedSignal.emit(changedEntity, newRadius)
        self.backup()

    def undo(self):
        j = self.history.pop()
        print(j)
        print("UNDO")
        self.onUndoSignal.emit()
        self.onHistoryChange.emit()

    def backup(self):
        print("backup")
        f = open("cache.bin", "w")
        d = json.dumps(self.root.toDict(), indent=2)
        f.write(d)
        f.close()
        self.history.append(d)
        self.onHistoryChange.emit()