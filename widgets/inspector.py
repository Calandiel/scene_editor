import sys
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QColorDialog
from PySide2.QtGui import QVector3D, QColor, QQuaternion
from PySide2.QtCore import Qt
from PySide2.QtGui import QDoubleValidator
from utilities import indexVector3D, indexQuaternion, writeVector3D, writeQuaternion, copyVector3D, copyColor, copyQuaternion, writeColor
from data.entity import CubeEntity, SphereEntity

class VectorFieldSpinBox(QDoubleSpinBox):
    def __init__(self, coord=0):
        super().__init__()
        self.coord = coord

class Inspector(QWidget):
    def __init__(self, database, parent=None):
        super(Inspector, self).__init__(parent)

        self.database = database
        self.setFixedWidth(450)
        
        label = QLabel("Inspector", alignment=Qt.AlignCenter)
        
        layout = QVBoxLayout(alignment=Qt.AlignTop)
        layout.addWidget(label)

        # Entity name
        nameWidget = QWidget()
        nameWidget.hide() # Hide by default
        layout.addWidget(nameWidget)
        nameLayout = QHBoxLayout(alignment=Qt.AlignLeft)
        nameWidget.setLayout(nameLayout)
        label = QLabel("Name: ", alignment=Qt.AlignLeft)
        textInput = QLineEdit()
        nameLayout.addWidget(label)
        nameLayout.addWidget(textInput)
        self.nameWidget = nameWidget
        self.nameWidgetText = textInput

        self.nameWidgetText.textEdited.connect(self.nameEdited)
        # Entity position
        (positionWidget, positionWidgetTexts) = self._createVectorEditor("Translation: ", editedCallback=self.positionEdited)
        layout.addWidget(positionWidget)
        self.positionWidget = positionWidget
        self.positionWidgetTexts = positionWidgetTexts
        # Entity rotation
        (rotationWidget, rotationWidgetTexts) = self._createVectorEditor("Quaternion: ", size=4, editedCallback=self.rotationEdited)
        layout.addWidget(rotationWidget)
        self.rotationWidget = rotationWidget
        self.rotationWidgetTexts = rotationWidgetTexts
        # Entity color
        (colorWidget, colorWidgetTexts) = self._createVectorEditor("Color: ", minv=0, maxv=255, editedCallback=self.colorEdited, increment=1)
        layout.addWidget(colorWidget)
        self.colorWidget = colorWidget
        self.colorWidgetTexts = colorWidgetTexts
        # Cube dimensions
        (cubeWidget, cubeWidgetTexts) = self._createVectorEditor("Dimensions: ", minv=0, editedCallback=self.cubeDimensionsEdited)
        layout.addWidget(cubeWidget)
        self.cubeWidget = cubeWidget
        self.cubeWidgetTexts = cubeWidgetTexts
        # Sphere radius
        (sphereWidget, sphereWidgetTexts) = self._createVectorEditor("Radius: ", minv=0, size=1, editedCallback=self.sphereRadiusEdited)
        layout.addWidget(sphereWidget)
        self.sphereWidget = sphereWidget
        self.sphereWidgetTexts = sphereWidgetTexts
        

        self.setLayout(layout)

        self.database.onEntitySelectedSignal.connect(self.onEntitySelected)
        self.database.onEntityDestroyedSignal.connect(self.onEntityDestroyed)
        self.database.onEntityRenamedSignal.connect(self.onEntityRenamed)

        self.database.onUndoSignal.connect(self.refreshInspector)
        self.database.onRedoSignal.connect(self.refreshInspector)


    def _createVectorEditor(self, name, minv=None, maxv=None, size=3, editedCallback=None, increment=0.01):
        widget = QWidget()
        widget.hide()
        layout = QHBoxLayout(alignment=Qt.AlignLeft)
        widget.setLayout(layout)
        label = QLabel(name, alignment=Qt.AlignLeft)

        inputs = [VectorFieldSpinBox(x) for x in range(size)]
        layout.addWidget(label)


        for i in inputs:
            i.setSingleStep(increment)
            layout.addWidget(i)
            if minv == None:
                i.setMinimum(-sys.float_info.max)
            else:
                i.setMinimum(minv)
            if maxv == None:
                i.setMaximum(sys.float_info.max)
            else:
                i.setMaximum(maxv)

        if editedCallback != None:
            lambdas = (lambda v, i=i: editedCallback(i, v) for i in range(size))
            for i, l in zip(inputs, lambdas):
                i.valueChanged.connect(l)

        return (widget, inputs)


    def nameEdited(self, text):
        #print("Edit: ", text)
        self.database.entityRenamed(self.database.selectedEntity, text)

    def positionEdited(self, i, val):
        newPosition = copyVector3D(self.database.selectedEntity.position)
        writeVector3D(newPosition, i, val)
        if newPosition != self.database.selectedEntity.position:
            self.database.entityMoved(self.database.selectedEntity, newPosition)

    def rotationEdited(self, i, val):
        newRotation = copyQuaternion(self.database.selectedEntity.rotation)
        writeQuaternion(newRotation, i, val)
        if newRotation != self.database.selectedEntity.rotation:
            self.database.entityRotated(self.database.selectedEntity, newRotation)

    def colorEdited(self, i, val):
        newColor = copyColor(self.database.selectedEntity.color)
        writeColor(newColor, i, val)
        if newColor != self.database.selectedEntity.color:
            self.database.entityColorChanged(self.database.selectedEntity, newColor)

    def cubeDimensionsEdited(self, i, val):
        newDimensions = copyVector3D(self.database.selectedEntity.dimensions)
        writeVector3D(newDimensions, i, val)
        if newDimensions != self.database.selectedEntity.dimensions:
            self.database.entityCubeDimensionsChanged(self.database.selectedEntity, newDimensions)

    def sphereRadiusEdited(self, _, val):
        #val = float(self.sphereWidgetTexts[0].cleanText())
        if val != self.database.selectedEntity.radius:
            self.database.entitySphereRadiusChanged(self.database.selectedEntity, val)


    def onEntitySelected(self):
        self.refreshInspector()

    def onEntityDestroyed(self, _):
        self.refreshInspector()

    def onEntityRenamed(self, _, __):
        self.refreshInspector()


    def refreshInspector(self):
        if self.database.selectedEntity != None and self.database.selectedEntity.parent != None:
            self.nameWidget.show()
            self.nameWidgetText.setText(self.database.selectedEntity.name)

            # Show widgets
            self.positionWidget.show()
            self.rotationWidget.show()
            self.colorWidget.show()

            # Update widget information
            for i, t in enumerate(self.positionWidgetTexts):
                t.value = indexVector3D(self.database.selectedEntity.position, i)
            for i, t in enumerate(self.rotationWidgetTexts):
                t.value = indexQuaternion(self.database.selectedEntity.rotation, i)
            for i, t in enumerate(self.colorWidgetTexts):
                t.value = self.database.selectedEntity.color.getRgb()[i]

            if isinstance(self.database.selectedEntity, CubeEntity):
                self.cubeWidget.show()
                for i, t in enumerate(self.cubeWidgetTexts):
                    t.value = indexVector3D(self.database.selectedEntity.dimensions, i)
                for i, t in enumerate(self.cubeWidgetTexts):
                    t.setValue(t.value)
            else:
                self.cubeWidget.hide()
            if isinstance(self.database.selectedEntity, SphereEntity):
                self.sphereWidget.show()
                for i, t in enumerate(self.sphereWidgetTexts):
                    t.value = self.database.selectedEntity.radius
                for t in self.sphereWidgetTexts:
                    t.setValue(t.value)
            else:
                self.sphereWidget.hide()

            # setValue emits a signal when the new value differs from old. To avoid it here (as to guard against infinite recursion), we call it *after* setting the value manually
            for t in self.positionWidgetTexts:
                t.setValue(t.value)
            for t in self.rotationWidgetTexts:
                t.setValue(t.value)
            for t in self.colorWidgetTexts:
                t.setValue(t.value)
        else:
            self.nameWidget.hide()
            self.positionWidget.hide()
            self.rotationWidget.hide()
            self.colorWidget.hide()
            self.cubeWidget.hide()
            self.sphereWidget.hide()