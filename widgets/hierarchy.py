import weakref
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QSizePolicy, QPushButton, QFileDialog
from PySide2.QtCore import Qt, Slot
from data.entity import CubeEntity, SphereEntity, MeshEntity

class HierarchyItem(QTreeWidgetItem):
    def __init__(self, entity):
        super().__init__()
        self.entity = weakref.ref(entity)
        self.setText(0, entity.name)

        for c in entity.children:
            child = HierarchyItem(c)
            self.addChild(child)

class Hierarchy(QWidget):
    def __init__(self, database, parent=None):
        super(Hierarchy, self).__init__(parent)
        self.setFixedWidth(300)
        self.database = database

        self.cameraToFpsButton = QPushButton("Change camera to FPS")
        self.cameraToOrbitButton = QPushButton("Change camera to orbit")
        self.cameraToOrbitButton.hide()
        self.cameraToFpsButton.clicked.connect(self.database.onFpsCameraSignal)
        self.cameraToOrbitButton.clicked.connect(self.database.onOrbitCameraSignal)

        redoUndoLayout = QHBoxLayout()
        undoButton = QPushButton("Undo")
        redoButton = QPushButton("Redo")
        redoUndoLayout.addWidget(undoButton)
        redoUndoLayout.addWidget(redoButton)
        undoButton.clicked.connect(database.undo)
        #redoButton.clicked.connect(database.redo)
        policy = undoButton.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        undoButton.setSizePolicy(policy)
        policy = redoButton.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        redoButton.setSizePolicy(policy)
        self.undoButton = undoButton
        self.redoButton = redoButton
        self._checkRedoUndoButtonVisibility()

        newCubeButton = QPushButton("Cube")
        newSphereButton = QPushButton("Sphere")
        newMeshButton = QPushButton("Mesh")
        removeButton = QPushButton("Remove")
        topLayout = QHBoxLayout()
        topLayout.addWidget(newCubeButton)
        topLayout.addWidget(newSphereButton)
        topLayout.addWidget(newMeshButton)
        topLayout.addWidget(removeButton)
        # Connect buttons
        removeButton.clicked.connect(self.entityDestroyed)
        newCubeButton.clicked.connect(self.cubeCreated)
        newSphereButton.clicked.connect(self.sphereCreated)
        newMeshButton.clicked.connect(self.meshCreated)

        # Keep the layout unchanged when the remove button isn't visible (which it often won't be as we won't always have an entity selected...)
        policy = removeButton.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        removeButton.setSizePolicy(policy)
        removeButton.hide()
        self.removeButton = removeButton

        # The main tree of the view, showing all entities in the rendered scene
        tree = QTreeWidget()
        tree.itemClicked.connect(self.itemClicked)
        self.tree = tree
        self.refreshHierarchy()

        #
        layout = QVBoxLayout(alignment=Qt.AlignTop)
        layout.addWidget(self.cameraToFpsButton)
        layout.addWidget(self.cameraToOrbitButton)
        layout.addLayout(topLayout)
        layout.addWidget(tree)
        layout.addLayout(redoUndoLayout)
        #layout.addWidget(label)
        self.setLayout(layout)

        database.onEntitySelectedSignal.connect(self.onEntitySelected)
        database.onEntityDestroyedSignal.connect(self.onEntityDestroyed)
        database.onEntityCreatedSignal.connect(self.onEntityCreated)
        database.onEntityRenamedSignal.connect(self.onEntityRenamed)

        database.onHistoryChange.connect(self._checkRedoUndoButtonVisibility)

        database.onFpsCameraSignal.connect(self.onFpsCamera)
        database.onOrbitCameraSignal.connect(self.onOrbitCamera)

    def onFpsCamera(self):
        self.cameraToFpsButton.hide()
        self.cameraToOrbitButton.show()
    
    def onOrbitCamera(self):
        self.cameraToFpsButton.show()
        self.cameraToOrbitButton.hide()

    def itemClicked(self, it, _):
        entity = it.entity()
        if entity != None:
            #print(entity.name)
            self.database.entitySelected(entity)

    def _checkRedoUndoButtonVisibility(self):
        if(len(self.database.history) > 0):
            self.undoButton.show()
        else:
            self.undoButton.hide()

    def entityDestroyed(self):
        self.database.entityDestroyed(self.database.selectedEntity)

    def cubeCreated(self):
        entity = CubeEntity()
        self.database.entityCreated(entity)

    def sphereCreated(self):
        entity = SphereEntity()
        self.database.entityCreated(entity)

    def meshCreated(self):
        fileName = QFileDialog.getOpenFileName(self, "Load Mesh", "", "Stl files (*.stl)")
        entity = MeshEntity(fileName[0])
        self.database.entityCreated(entity)


    def handleRemoveButtonHideState(self):
        if self.database.selectedEntity != None and self.database.selectedEntity.getParent() != None:
            self.removeButton.show()
        else:
            self.removeButton.hide()

    def refreshHierarchy(self):
        self.tree.clear()
        root = HierarchyItem(self.database.root)
        self.tree.addTopLevelItem(root)
        self.tree.expandAll()
        self.tree.setHeaderLabels(["Hierarchy"])
        #self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def onEntitySelected(self):
        self.handleRemoveButtonHideState()

    def onEntityDestroyed(self, entity):
        self.refreshHierarchy()
        self.handleRemoveButtonHideState()

    def onEntityCreated(self, entity):
        self.refreshHierarchy()

    def onEntityRenamed(self, _, __):
        self.refreshHierarchy()