import weakref
from PySide2.QtGui import QVector3D, QColor, QQuaternion
from PySide2 import QtCore

class Entity(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.children = []
        self.parent = None
        self.name = "Entity"
        self.position = QVector3D(0, 0, 0)
        self.rotation = QQuaternion(0, 0, 0, 0)
        self.color = QColor.fromRgb(255, 255, 255)

    # Sets the parent of this entity. Handles removal from the previous parent and parent's children arrays.
    def setParent(self, parent):
        # Remove this entity from previous parent's children
        if self.parent != None and self.parent() != None:
            self.parent().children.remove(self)
        # Handle the new parent
        if parent == None:
            self.parent = None
        else:
            self.parent = weakref.ref(parent)
            parent.children.append(self)

    # Returns the parent Entity    
    def getParent(self):
        if self.parent == None:
            return None
        else:
            return self.parent()

    def toDict(self):
        v = {}
        v["name"] = self.name
        v["position"] = [self.position.x(), self.position.y(), self.position.z()]
        r = self.rotation.toVector4D()
        v["rotation"] = [r.x(), r.y(), r.z(), r.w()]
        v["color"] = [self.color.toRgb().red(), self.color.toRgb().green(), self.color.toRgb().blue()]
        v["children"] = [x.toDict() for x in self.children]
        v["identifier"] = "Entity"
        return v

    def fromDict(d):
        i = d["identifier"]
        entity = None
        if i == "Entity":
            entity = Entity()
        elif i == "Sphere":
            entity = SphereEntity()
        elif i == "Cube":
            entity = CubeEntity()
        elif i == "Mesh":
            entity = MeshEntity(None)

        entity.name = d["name"]
        entity.position = QVector3D(d["position"][0], d["position"][1], d["position"][2])
        entity.rotation = QQuaternion(d["rotation"][0], d["rotation"][1], d["rotation"][2], d["rotation"][3])
        entity.color = QColor(d["color"][0], d["color"][1], d["color"][2])
        
        if i == "Entity":
            pass
        elif i == "Sphere":
            entity.radius = d["radius"]
        elif i == "Cube":
            entity.dimensions = QVector3D(d["dimensions"][0], d["dimensions"][1], d["dimensions"][2])
        elif i == "Mesh":
            entity.meshPath = d["meshPath"]

        for c in d["children"]:
            child = Entity.fromDict(c)
            child.setParent(entity)

        return entity

class SphereEntity(Entity):
    def __init__(self):
        super().__init__()
        self.radius = 1
        self.name = "Sphere"

    def toDict(self):
        v = Entity.toDict(self)
        v["radius"] = self.radius
        v["identifier"] = "Sphere"
        return v

class CubeEntity(Entity):
    def __init__(self):
        super().__init__()
        self.dimensions = QVector3D(1, 1, 1)
        self.name = "Cube"

    def toDict(self):
        v = Entity.toDict(self)
        v["dimensions"] = [self.dimensions.x(), self.dimensions.y(), self.dimensions.z()]
        v["identifier"] = "Cube"
        return v

class MeshEntity(Entity):
    def __init__(self, meshPath):
        super().__init__()
        self.name = "Mesh"
        self.meshPath = meshPath

    def toDict(self):
        v = Entity.toDict(self)
        v["identifier"] = "Mesh"
        v["meshPath"] = self.meshPath
        return v