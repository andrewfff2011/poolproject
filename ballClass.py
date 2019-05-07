#########################################
# ballClass.py Citation Comment:
# Lines 1-68: Original Code
# Lines 69-73: Code from gamedev.stackexchange.com/questions/20516/ball-collisions-sticking-together
# Lines 74-92: Original Code
#########################################

import vectorClass
from math import *

class ball(object):
    def __init__(self, number, posX, posY, posZ):
        self.number = number
        self.x = posX
        self.y = posY
        self.z = posZ
        self.r = 1
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.vel = vectorClass.vector3(0, 0, 0)
        self.spin = (0, 0, 0)
        self.potted = False

    def __repr__(self):
        if self.number == 16:
            return "Cue Ball at (%0.2f, %0.2f, %0.2f)" % (self.x, self.y, self.z)
        else:
            return "%d Ball at (%0.2f, %0.2f, %0.2f)" % (self.number, self.x, self.y, self.z)

    def getPos(self):
        return vectorClass.vector3(self.x, self.y, self.z)

    def setPos(self, pos):
        self.x, self.y, self.z = pos
    
    def move(self):
        dx, dy, dz = self.vel.getVector()
        self.x += dx
        self.y += dy
        self.z += dz

    def redoMove(self):
        dx, dy, dz = self.vel.getVector()
        self.x -= dx
        self.y -= dy
        self.z -= dz

    def setVel(self, velocityVector):
        self.vel = velocityVector

    def getVel(self):
        return self.vel

    def decelerate(self, FRIC):
        self.vel.scaleVector(1-FRIC)

    def isColliding(self, other):
        if self.number == -1 and other.number == 16:
            return False

        dirVec = vectorClass.vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        distance = sqrt(dx**2 + dy**2 + dz**2)
        if distance < (self.r + other.r):
            # checks if the two balls are going towards each other using some vector calculations
            # logic from: gamedev.stackexchange.com/questions/20516/ball-collisions-sticking-together
            ballDist = vectorClass.vector3.difference(self.getPos(), other.getPos())
            relativeVelocity = vectorClass.vector3.difference(other.vel, self.vel)
            return vectorClass.vector3.dot(ballDist, relativeVelocity) > 0
        else:
            return False

    def setPotted(self):
        self.vel = vectorClass.vector3(0, 0, 0)
        self.potted = True

    @staticmethod
    def calculateTrajectory(ball1, ball2):
        dirVec = vectorClass.vector3(ball1.x - ball2.x, ball1.y - ball2.y, ball1.z - ball2.z).normalize()
        # print("dirVec", dirVec)
        p = (vectorClass.vector3.dot(ball1.vel, dirVec) - vectorClass.vector3.dot(ball2.vel, dirVec))
        # print("p", p)
        dirVec.scaleVector(p)
        ball1Vec = vectorClass.vector3.difference(ball1.vel, dirVec)
        dirVec.scaleVector(-1)
        ball2Vec = vectorClass.vector3.difference(ball2.vel, dirVec)
        return ball1Vec, ball2Vec
