import sys
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QColorDialog
from PySide2.QtGui import QVector3D, QColor, QQuaternion
from PySide2.QtCore import Qt
from PySide2.QtGui import QDoubleValidator
from utilities import indexVector3D, indexQuaternion
from data.entity import CubeEntity, SphereEntity

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

        inputs = [QDoubleSpinBox() for x in range(size)]
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
                i.valueChanged.connect(editedCallback)

        return (widget, inputs)


    def nameEdited(self, text):
        #print("Edit: ", text)
        self.database.entityRenamed(self.database.selectedEntity, text)

    def positionEdited(self, _):
        vals = [float(x.cleanText()) for x in self.positionWidgetTexts]
        newPosition = QVector3D(vals[0], vals[1], vals[2])
        if newPosition != self.database.selectedEntity.position:
            #print("Position edited!")
            self.database.entityMoved(self.database.selectedEntity, newPosition)

    def rotationEdited(self, _):
        vals = [float(x.cleanText()) for x in self.rotationWidgetTexts]
        newRotation = QQuaternion(vals[0], vals[1], vals[2], vals[3])
        if newRotation != self.database.selectedEntity.rotation:
            #print("Position edited!")
            self.database.entityRotated(self.database.selectedEntity, newRotation)

    def colorEdited(self, _):
        vals = [int(float(x.cleanText())) for x in self.colorWidgetTexts]
        newColor = QColor(vals[0], vals[1], vals[2])
        if newColor != self.database.selectedEntity.color:
            #print(newColor, self.database.selectedEntity.color)
            self.database.entityColorChanged(self.database.selectedEntity, newColor)

    def cubeDimensionsEdited(self, _):
        vals = [float(x.cleanText()) for x in self.cubeWidgetTexts]
        newDimensions = QVector3D(vals[0], vals[1], vals[2])
        if newDimensions != self.database.selectedEntity.dimensions:
            self.database.entityCubeDimensionsChanged(self.database.selectedEntity, newDimensions)

    def sphereRadiusEdited(self, _):
        val = float(self.sphereWidgetTexts[0].cleanText())
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

            # setValue emits a signal when the new value differs from old. To avoid it here (as to guard against infinite recursion), we call it *after* setting the value manually
            for t in self.positionWidgetTexts:
                t.setValue(t.value)
            for t in self.rotationWidgetTexts:
                t.setValue(t.value)
            for t in self.colorWidgetTexts:
                t.setValue(t.value)

            if isinstance(self.database.selectedEntity, CubeEntity):
                self.cubeWidget.show()
                for i, t in enumerate(self.cubeWidgetTexts):
                    t.value = indexVector3D(self.database.selectedEntity.dimensions, i)
                for t in self.cubeWidgetTexts:
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
        else:
            self.nameWidget.hide()
            self.positionWidget.hide()
            self.rotationWidget.hide()
            self.colorWidget.hide()
            self.cubeWidget.hide()
            self.sphereWidget.hide()