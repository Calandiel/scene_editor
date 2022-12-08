from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide2.QtCore import Qt, QUrl
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DRender import Qt3DRender
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtGui import QVector3D, QColor
from data.entity import CubeEntity, SphereEntity, MeshEntity

class Viewable:
    def __init__(self, transform, mesh, material, entity3D):
        self.transform = transform
        self.mesh = mesh
        self.material = material
        self.entity = entity3D

class View(QWidget):
    def __init__(self, database, parent=None):
        super(View, self).__init__(parent)
        self.database = database
        self.entityMap = {}

        view = Qt3DExtras.Qt3DWindow()
        root = Qt3DCore.QEntity()
        view.setRootEntity(root)
        container = QWidget.createWindowContainer(view)
        container.setMinimumSize(300, 300)
        container.setMaximumSize(view.screen().size())

        #Qt3DRender.QPickingSettings.AllPicks
        #self.picker = Qt3DRender.QObjectPicker(root)
        #self.picker.clicked.connect(self.clicked)
        #self.picker.released.connect(self.clicked)

        layout = QVBoxLayout(self)
        layout.addWidget(container)

        self.view = view # Remember to keep the rendering context alive
        self.root = root
        self._configureCamera()
        self._loadEntity(database.root)

        # Setting up the camera controls and stuff
        self.onOrbitCamera()

        self.database.onEntityCreatedSignal.connect(self.onEntityCreated)
        self.database.onEntityDestroyedSignal.connect(self.onEntityDestroyed)
        self.database.onEntityMovedSignal.connect(self.onEntityMoved)
        self.database.onEntityRotatedSignal.connect(self.onEntityRotated)
        self.database.onEntityColorChangedSignal.connect(self.onEntityColorChanged)
        self.database.onEntityCubeDimensionsChangedSignal.connect(self.onEntityCubeDimensionsChanged)
        self.database.onEntitySphereDimensionsChangedSignal.connect(self.onEntitySphereRadiusChanged)

        self.database.onFpsCameraSignal.connect(self.onFpsCamera)
        self.database.onOrbitCameraSignal.connect(self.onOrbitCamera)

        self.database.onUndoSignal.connect(self.onUndoRedo)
        self.database.onRedoSignal.connect(self.onUndoRedo)

    def onFpsCamera(self):
        self.view.camController = Qt3DExtras.QFirstPersonCameraController(self.root)
        self.view.camController.setLinearSpeed(25)
        self.view.camController.setLookSpeed(150)
        self.view.camController.setCamera(self.view.camera())

    def onOrbitCamera(self):
        self.view.camController = Qt3DExtras.QOrbitCameraController(self.root)
        self.view.camController.setLinearSpeed(25)
        self.view.camController.setLookSpeed(150)
        self.view.camController.setCamera(self.view.camera())

    #def clicked(self, e):
    #    print("Picked: ", type(e))

    def _loadEntity(self, e):
        for c in e.children:
            self.onEntityCreated(c)
            self._loadEntity(c)

    def _clear(self):
        self.entityMap = {}
        pass

    def onUndoRedo(self):
        self._clear()
        self._loadEntity(self.database.root)
        pass

    def _configureCamera(self):
        self.view.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        self.view.camera().setPosition(QVector3D(10, 10, 10))
        self.view.camera().setViewCenter(QVector3D(0, 0, 0))


    def onEntityCreated(self, newEntity):
        parent = self.root
        if newEntity.parent != None and newEntity.parent() in self.entityMap:
            parent = self.entityMap[newEntity.parent()].entity

        #print(parent)
        entity = Qt3DCore.QEntity(parent)
        material = Qt3DExtras.QPhongMaterial()
        material.setDiffuse(newEntity.color)
        material.setAmbient(QColor(0.5, 0.5, 0.5))
        transform = Qt3DCore.QTransform()
        transform.setTranslation(newEntity.position)
        transform.setRotation(newEntity.rotation)
        mesh = None

        if isinstance(newEntity, SphereEntity):
            #print("Sphere")
            mesh = Qt3DExtras.QSphereMesh()
            mesh.setRadius(newEntity.radius)
        elif isinstance(newEntity, CubeEntity):
            #print("Cube")
            mesh = Qt3DExtras.QCuboidMesh()
            mesh.setXExtent(newEntity.dimensions.x())
            mesh.setYExtent(newEntity.dimensions.y())
            mesh.setZExtent(newEntity.dimensions.z())
        elif isinstance(newEntity, MeshEntity):
            mesh = Qt3DRender.QMesh()
            mesh.setSource(QUrl("file:" + newEntity.meshPath))
        else:
            #print("Entity")
            pass

        entity.addComponent(mesh)
        entity.addComponent(transform)
        entity.addComponent(material)
        #entity.addComponent(self.picker)
        self.entityMap[newEntity] = Viewable(transform, mesh, material, entity)

    def onEntityDestroyed(self, destroyedEntity):
        self.entityMap.pop(destroyedEntity, None)
        for c in destroyedEntity.children:
            self.onEntityDestroyed(c)

    def onEntityMoved(self, movedEntity, newPosition):
        transform = self.entityMap[movedEntity].transform
        transform.setTranslation(newPosition)

    def onEntityRotated(self, rotatedEntity, newRotation):
        transform = self.entityMap[rotatedEntity].transform
        transform.setRotation(newRotation)

    def onEntityColorChanged(self, changedEntity, newColor):
        self.entityMap[changedEntity].material.setDiffuse(newColor)

    def onEntityCubeDimensionsChanged(self, changedEntity, newDimensions):
        mesh = self.entityMap[changedEntity].mesh
        mesh.setXExtent(newDimensions.x())
        mesh.setYExtent(newDimensions.y())
        mesh.setZExtent(newDimensions.z())

    def onEntitySphereRadiusChanged(self, changedEntity, newRadius):
        mesh = self.entityMap[changedEntity].mesh
        mesh.setRadius(newRadius)