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

# Given a QQuaternion, returns the i-th coordinate, as if the vector was an indexable array
def indexQuaternion(v, i):
    if i == 0:
        return v.toVector4D().x()
    elif i == 1:
        return v.toVector4D().y()
    elif i == 2:
        return v.toVector4D().z()
    elif i == 3:
        return v.toVector4D().w()
    else:
        raise Exception("Trying to index a QVector3D with " + str(i) + ", which is out of allowed range.")