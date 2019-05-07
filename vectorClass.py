#########################################
# ballClass.py Citation Comment:
# Lines 1-50: Original Code
#########################################

from math import *

class vector3(object):
    def __init__(self, x, y, z):
        self.dx = float(x)
        self.dy = float(y)
        self.dz = float(z)

    def __repr__(self):
        return "Vector(%0.3f, %0.3f, %0.3f)" % (self.dx, self.dy, self.dz)

    def getVector(self):
        return (self.dx, self.dy, self.dz)

    def setVector(self, x, y, z):
        self.dx = float(x)
        self.dy = float(y)
        self.dz = float(z)

    def scaleVector(self, scale):
        self.dx *= scale
        self.dy *= scale
        self.dz *= scale

    def normalize(self):
        mag = sqrt(self.dx**2 + self.dy**2 + self.dz**2)
        return vector3(self.dx / mag, self.dy / mag, self.dz / mag)

    def magnitude(self):
        return sqrt(self.dx**2 + self.dy**2 + self.dz**2)

    @staticmethod
    def difference(vec1, vec2):
        dx = vec1.dx - vec2.dx
        dy = vec1.dy - vec2.dy
        dz = vec1.dz - vec2.dz

        return vector3(dx, dy, dz)

    @staticmethod
    def dot(vector1, vector2):
        x1, y1, z1 = vector1.getVector()
        x2, y2, z2 = vector2.getVector()

        return x1*x2 + y1*y2 + z1*z2