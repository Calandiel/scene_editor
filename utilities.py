from PySide2.QtGui import QVector3D, QColor, QQuaternion

# Given a QVector3D, returns the i-th coordinate, as if the vector was an indexable array
def indexVector3D(v, i):
    if i == 0:
        return v.x()
    elif i == 1:
        return v.y()
    elif i == 2:
        return v.z()
    else:
        raise Exception("Trying to index a QVector3D with " + str(i) + ", which is out of allowed range.")

def writeVector3D(v, i, val):
    if i == 0:
        v.setX(val)
    elif i == 1:
        v.setY(val)
    elif i == 2:
        v.setZ(val)
    else:
        raise Exception("Trying to index a QVector3D with " + str(i) + ", which is out of allowed range.")

def copyVector3D(v):
    return QVector3D(v.x(), v.y(), v.z())


# Given a QQuaternion, returns the i-th coordinate, as if the vector was an indexable array
def indexQuaternion(v, i):
    if i == 1:
        return v.x()
    elif i == 2:
        return v.y()
    elif i == 3:
        return v.z()
    elif i == 0:
        return v.scalar()
    else:
        raise Exception("Trying to index a QQuaternion with " + str(i) + ", which is out of allowed range.")

def writeQuaternion(v, i, val):
    if i == 1:
        v.setX(val)
    elif i == 2:
        v.setY(val)
    elif i == 3:
        v.setZ(val)
    elif i == 0:
        v.setScalar(val)
    else:
        raise Exception("Trying to index a QQuaternion with " + str(i) + ", which is out of allowed range.")

def copyQuaternion(v):
    return QQuaternion(v.scalar(), v.x(), v.y(), v.z())



def writeColor(v, i, val):
    if i == 0:
        v.setRed(val)
    elif i == 1:
        v.setGreen(val)
    elif i == 2:
        v.setBlue(val)
    else:
        raise Exception("Trying to index a QColor with " + str(i) + ", which is out of allowed range.")

def copyColor(v):
    return QColor(v.red(), v.green(), v.blue())
