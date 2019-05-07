#########################################
#myProject.py Citation Comment:
# Lines 1-1054: Original code
# Lines 1055-1076: Mouse dragging code taken from Panda3D sample program: Chessboard, by Shao Zhang, Phil Saltzman, and Eddie Canaan
# Lines 1077-1263: Original code
#########################################

from math import *
import ballClass
import vectorClass
import sys
import random
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Material, AmbientLight, DirectionalLight, Camera
from panda3d.core import NodePath, PandaNode, TextNode
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay
from panda3d.core import LRotationf, LVector3f, LVector3
from panda3d.core import loadPrcFileData, LineSegs, BitMask32, TransparencyAttrib
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

loadPrcFileData('', 'win-size 1366 768')

FRIC = 0.00800
SPACING = 0
MAXPWR = 2

# This is the main function where the game lives, it starts in the menu screen
class play(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.gameMode = 0
        self.gameStateNum = 0
        self.initMenuScreen()

    # function that loads all the menu screen assets
    def initMenuScreen(self):
        # loads the background as an image file
        self.background = OnscreenImage(image = 'models/menuBackground.jpg',
            pos = (0,0,0), scale = (1366/768, 1, 1))
        # loads the title text as an image
        self.titleText = OnscreenImage(image = 'models/menuTitle.png',
            pos = (0, 0, 0.75), scale = (640/120/5, 1, 1/5))
        self.titleText.setTransparency(TransparencyAttrib.MAlpha)
        # loads the two buttons so that the player can choose which game to play
        self.eightButton = DirectButton(text = "Play 8 Ball!", pos = (0.75, 0, 0.12),
            relief = "raised", borderWidth = (0.01, 0.01),
            frameSize = (-0.3, 0.3, -0.1, 0.1),
            text_scale = 0.08, command = self.menuToEight)
        self.nineButton = DirectButton(text = "Play 9 Ball!", pos = (0.75, 0, -0.12),
            relief = "raised", borderWidth = (0.01, 0.01),
            frameSize = (-0.3, 0.3, -0.1, 0.1),
            text_scale = 0.08, command = self.menuToNine)

    # unloads everything from the menu screen, clearing it from memory
    def deInitMenuScreen(self):
        self.background.removeNode()
        self.titleText.removeNode()
        self.eightButton.removeNode()
        self.nineButton.removeNode()

    # wrapper function that loads all the variables and models for 8 ball
    def init8Ball(self):
        self.gameMode = 8
        self.currentPlayer = 0
        self.continueTurn = False
        self.playerObj = [None, None]
        self.openTable = True
        self.calculated = True
        self.firstContact = None

        # these set up the controller keys
        self.keyMap = {"cam-left": 0, "cam-right": 0, "cam-down": 0, "cam-up": 0,
            "cam-fine": False}

        self.accept("a", self.setKey, ["cam-left", True])
        self.accept("d", self.setKey, ["cam-right", True])
        self.accept("w", self.setKey, ["cam-down", True])
        self.accept("s", self.setKey, ["cam-up", True])
        self.accept("a-up", self.setKey, ["cam-left", False])
        self.accept("d-up", self.setKey, ["cam-right", False])
        self.accept("w-up", self.setKey, ["cam-down", False])
        self.accept("s-up", self.setKey, ["cam-up", False])

        self.accept("space", self.deInit8Ball)

        self.accept("shift", self.setKey, ["cam-fine", True])
        self.accept("control", self.setKey, ["cam-fine", False])
        self.accept("enter", self.hitBallHandler)
        self.accept("escape", sys.exit)

        self.accept("mouse1", self.grabBall)
        self.accept("mouse1-up", self.releaseBall)

        self.accept("r", self.resetCamera)

        self.origin = render.attachNewNode("origin")
        self.origin.setPos(0, 0, 0)
        self.tableFloater = self.origin.attachNewNode("tableFloater")

        self.ballsDone = True
        self.scratched = False
        self.placing = False
        self.gameOver = False
        self.grabbed = False

        # the task manager runs every frame and does the calculations
        taskMgr.add(self.moveCamera, "moveCameraTask")
        taskMgr.add(self.showBalls, "showBallsTask")
        taskMgr.add(self.moveBalls, "moveBallsTask")
        taskMgr.add(self.showTrajectory, "showTrajectoryTask")
        taskMgr.add(self.gameState, "gameStateTask")
        taskMgr.add(self.mouseTask, "mouseTask")

        # this is code used for picking up the cue ball when it scratches
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.pickerNode = CollisionNode("mouseRay")
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)

        # loads all the models for the table and attach textures to it
        def loadTable(self):
            self.modelRoot = render.attachNewNode("modelRoot")

            cherry = loader.loadTexture("models/cherry.png")
            aluminum = loader.loadTexture("models/brushed_aluminum.png")
            leather = loader.loadTexture("models/leather.png")
            fabric = loader.loadTexture("models/dobby.png")

            self.tableSurface = loader.loadModel("models/table_surface")
            self.tableSurface.setTexture(fabric)
            bounds = self.tableSurface.getTightBounds()
            scale = 44 / (bounds[1] - bounds[0])[0]
            self.tableSurface.setScale(scale)
            self.tableSurface.reparentTo(self.modelRoot)
            
            self.tableEdge = loader.loadModel("models/table_edge")
            self.tableEdge.setTexture(cherry)
            self.tableEdge.setScale(scale)
            self.tableEdge.reparentTo(self.modelRoot)

            self.bottomCushion = loader.loadModel("models/table_bottom_cushion")
            self.bottomCushion.setTexture(fabric)
            self.bottomCushion.setScale(scale)
            self.bottomCushion.reparentTo(self.modelRoot)

            self.topCushion = loader.loadModel("models/table_top_cushion")
            self.topCushion.setTexture(fabric)
            self.topCushion.setScale(scale)
            self.topCushion.reparentTo(self.modelRoot)

            self.bottomRightCushion = loader.loadModel("models/table_bottomRight_cushion")
            self.bottomRightCushion.setTexture(fabric)
            self.bottomRightCushion.setScale(scale)
            self.bottomRightCushion.reparentTo(self.modelRoot)

            self.bottomLeftCushion = loader.loadModel("models/table_bottomLeft_cushion")
            self.bottomLeftCushion.setTexture(fabric)
            self.bottomLeftCushion.setScale(scale)
            self.bottomLeftCushion.reparentTo(self.modelRoot)

            self.topRightCushion = loader.loadModel("models/table_topRight_cushion")
            self.topRightCushion.setTexture(fabric)
            self.topRightCushion.setScale(scale)
            self.topRightCushion.reparentTo(self.modelRoot)

            self.topLeftCushion = loader.loadModel("models/table_topLeft_cushion")
            self.topLeftCushion.setTexture(fabric)
            self.topLeftCushion.setScale(scale)
            self.topLeftCushion.reparentTo(self.modelRoot)

            self.cornerPockets = loader.loadModel("models/table_pockets")
            self.cornerPockets.setTexture(leather)
            self.cornerPockets.setScale(scale)
            self.cornerPockets.reparentTo(self.modelRoot)

            self.cornerCovers = loader.loadModel("models/table_covers")
            self.cornerCovers.setTexture(aluminum)
            self.cornerCovers.setScale(scale)
            self.cornerCovers.reparentTo(self.modelRoot)
            
            coord1, coord2 = self.modelRoot.getTightBounds()
            size = coord2 - coord1
            self.modelRoot.setPos(-coord1[0] - size[0]/2, 
                -coord1[1] - size[1]/2, -coord1[2] - size[2])
            coord1, coord2 = self.tableSurface.getTightBounds()
            zShift = -coord2[2]
            self.modelRoot.setZ(zShift)

        # loads lighting in the scene and attaches the lighting to all the models
        def loadLighting(self):
            ambientLight = AmbientLight("ambientLight")
            ambientLight.setColor((0.55, 0.55, 0.7, 1))
            self.ambLightNode = render.attachNewNode(ambientLight)
            render.setLight(self.ambLightNode)

            directionalLight = DirectionalLight("directionalLight")
            directionalLight.setColor((0.8, 0.8, 0.8, 1))
            directionalLight.setSpecularColor((1, 1, 1, 1))
            self.dnlp = render.attachNewNode(directionalLight)
            self.dnlp.setHpr(0, -90, 0)
            render.setLight(self.dnlp)

            reflectionLight = DirectionalLight("reflectionLight")
            reflectionLight.setColor((0.01, 0.01, 0.1, 1))
            self.rnlp = render.attachNewNode(reflectionLight)
            self.rnlp.setHpr(0, 90, 0)
            render.setLight(self.rnlp)

        # loads the ball models as well as load Ball() objects that deal with collision
        def initBalls(self):
            coord1, coord2 = self.tableSurface.getTightBounds()
            size = coord2 - coord1
            self.dot = self.origin.attachNewNode("dot")
            self.dot.setY(-size[1]/4)

            lst = [1, 3, 4, 8, 10, 14, 11, 5, 2, 6, 7, 9, 15, 13, 12]

            sqrt3 = 3**0.5
            positions = {1: (0, 0), 
            2: (-1-SPACING, -(sqrt3+SPACING)), 3: (1+SPACING, -(sqrt3+SPACING)), 
            4: (-2-SPACING, -2*(sqrt3+SPACING)), 5: (0, -2*(sqrt3+SPACING)), 6: (2+SPACING, -2*(sqrt3+SPACING)),
            7: (-3-0.002, -3*(sqrt3+SPACING)), 8: (-1-SPACING, -3*(sqrt3+SPACING)), 9: (1+SPACING, -3*(sqrt3+SPACING)), 10: (3+0.002, -3*(sqrt3+SPACING)),
            11: (-4-0.002, -4*(sqrt3+SPACING)), 12: (-2-SPACING, -4*(sqrt3+SPACING)), 13: (0, -4*(sqrt3+SPACING)), 
            14: (2+SPACING, -4*(sqrt3+SPACING)), 15: (4+0.002, -4*(sqrt3+SPACING))}

            self.ballObjList = []
            r = 1
            index = 0
            for num in lst:
                index += 1
                temp_ball = ballClass.ball(index, r*positions[num][0], r*positions[num][1], 1)
                self.ballObjList.append(temp_ball)

            cue_ball = ballClass.ball(16, 0, 2*size[1]/4, 1)
            self.ballObjList.append(cue_ball)

            self.ball_1 = loader.loadModel("models/ball_1")
            self.ball_2 = loader.loadModel("models/ball_2")
            self.ball_3 = loader.loadModel("models/ball_3")
            self.ball_4 = loader.loadModel("models/ball_4")
            self.ball_5 = loader.loadModel("models/ball_5")
            self.ball_6 = loader.loadModel("models/ball_6")
            self.ball_7 = loader.loadModel("models/ball_7")
            self.ball_8 = loader.loadModel("models/ball_8")
            self.ball_9 = loader.loadModel("models/ball_9")
            self.ball_10 = loader.loadModel("models/ball_10")
            self.ball_11 = loader.loadModel("models/ball_11")
            self.ball_12 = loader.loadModel("models/ball_12")
            self.ball_13 = loader.loadModel("models/ball_13")
            self.ball_14 = loader.loadModel("models/ball_14")
            self.ball_15 = loader.loadModel("models/ball_15")
            self.cueBall = loader.loadModel("models/ballCue")
            self.ballModelList = [self.ball_1, self.ball_2, self.ball_3, self.ball_4,
                self.ball_5, self.ball_6, self.ball_7, self.ball_8, self.ball_9, self.ball_10,
                self.ball_11, self.ball_12, self.ball_13, self.ball_14, self.ball_15, self.cueBall]

            bounds = self.ball_1.getTightBounds()
            size = bounds[1] - bounds[0]
            scale = (r*2) / size[0]

            for ball in self.ballModelList:
                ball.reparentTo(self.dot)
                ball.setScale(scale)

            self.cueBall.find("**/ball").node().setIntoCollideMask(BitMask32.bit(1))

        # loads the heads up display, including cue power indicator, trajectory line, etc.
        def loadHUD(self):
            self.solidsPosList = [(0.01, 0, 0.365), (0.01, 0, 0.205), (0.01, 0, 0.045), 
                (0.01, 0, -0.115), (0.01, 0, -0.275), (0.01, 0, -0.435), (0.01, 0, -0.595)]
            self.stripesPosList = [(-0.01, 0, 0.365), (-0.01, 0, 0.205), (-0.01, 0, 0.045), 
                (-0.01, 0, -0.115), (-0.01, 0, -0.275), (-0.01, 0, -0.435), (-0.01, 0, -0.595)]

            self.currentPower = "Current\nCue\nPower:\n50%"
            width = base.win.getXSize()/2
            height = base.win.getYSize()/2
            xRatio = width/height
            fClr = (193, 126, 25) # rgb values of the frame color
            self.pottedBallStripes = set()
            self.pottedBallSolids = set()
            self.cueCtrlFrame = DirectFrame(pos = (xRatio,0,0), 
                frameSize = (-0.5, 0, -1, 1),
                frameColor = (fClr[0]/255, fClr[1]/255, fClr[2]/255, 0.2),
                relief = "raised", borderWidth = (0.03, 0.03))

            self.cuePowerFrame = DirectFrame(pos = (0, 0.5, 0))
            self.cuePowerFrame.reparentTo(self.cueCtrlFrame)
            self.cuePower = DirectSlider(range = (0, 100),
                value = 50, pageSize = 1, orientation = "vertical",
                pos = (-0.37, 0, 0.45), frameSize = (-0.3, 0.3, -0.5, 0.5),
                thumb_frameSize = (-0.07, 0.07, -0.05, 0.05),
                thumb_relief = "flat", command = showValue)
            self.cuePower.reparentTo(self.cuePowerFrame)
            self.cuePowerText = OnscreenText(text = str(self.currentPower),
                pos = (-0.28, 0.5,0), align = TextNode.ALeft)
            self.cuePowerText.reparentTo(self.cuePowerFrame)

            textColor = (256, 0, 0)
            self.currentPlayerText = OnscreenText(text = "Current Player:\n" + str(self.currentPlayer + 1),
                pos = (-0.25, -0.4), scale = 0.06,
                fg = (textColor[0]/256, textColor[1]/256, textColor[2]/256, 1),
                shadow = (0,0,0, 0.8),
                mayChange = True,
                parent = self.cueCtrlFrame)

            self.hitButton = DirectButton(pos = (-0.25, 0, -0.85), 
                frameSize = (-0.2, 0.2, -0.1, 0.1), 
                relief = "raised", borderWidth = (0.01, 0.01),
                text = ("Hit Ball!", "Hit Ball!", "Hit Ball!", "Rolling"),
                text_scale = 0.05, command = hitBall)
            self.hitButton.reparentTo(self.cueCtrlFrame)

            self.pottedBallsFrame = DirectFrame(pos = (-xRatio, 0, 0),
                frameSize = (0, 0.5, -1, 1), 
                frameColor = (fClr[0]/255, fClr[1]/255, fClr[2]/255, 0.2),
                relief = "raised", borderWidth = (0.03, 0.03))
            self.pottedSolidsFrame = DirectFrame(pos = (0.125, 0, 0.5),
                frameSize = (-0.08, 0.1, -0.7, 0.455),
                relief = "flat")
            self.pottedSolidsFrame.reparentTo(self.pottedBallsFrame)
            self.pottedStripesFrame = DirectFrame(pos = (0.375, 0, 0.5),
                frameSize = (-0.1, 0.08, -0.7, 0.455),
                relief = "flat")
            self.pottedStripesFrame.reparentTo(self.pottedBallsFrame)

            self.showinst = False
            self.instButton = DirectButton(pos = (0.25, 0, -0.85),
                frameSize = (-0.2, 0.2, -0.1, 0.1),
                relief = "raised", borderWidth = (0.01, 0.01),
                text = ("Show\nInstructions"),
                text_scale = 0.05, command = showInstructions)
            self.instButton.reparentTo(self.pottedBallsFrame)

            self.menuButton = DirectButton(pos = (0.25, 0, -0.65),
                frameSize = (-0.2, 0.2, -0.1, 0.1),
                relief = "raised", borderWidth = (0.01, 0.01),
                text = "Return to Menu",
                text_scale = 0.05, command = eightToMenu)
            self.menuButton.reparentTo(self.pottedBallsFrame)

            self.cueLine = LineSegs()
            self.cueLine.moveTo(self.cueBall.getPos())
            self.cueLine.drawTo(self.cueBall.getPos())
            self.cueLineNode = NodePath(self.cueLine.create(dynamic = True))
            self.cueLineNode.reparentTo(self.dot)

            self.objBallLine = LineSegs()
            self.objBallLine.moveTo(self.cueBall.getPos())
            self.objBallLine.drawTo(self.cueBall.getPos())
            self.objBallLineNode = NodePath(self.objBallLine.create(dynamic = True))
            self.objBallLineNode.reparentTo(self.dot)

            self.reboundLine = LineSegs()
            self.reboundLine.moveTo(self.cueBall.getPos())
            self.reboundLine.drawTo(self.cueBall.getPos())
            self.reboundLineNode = NodePath(self.reboundLine.create(dynamic = True))
            self.reboundLineNode.reparentTo(self.dot)

        # helper function that shows the current cue power
        def showValue():
            self.currentPower = round(self.cuePower['value'])
            self.cuePowerText.setText("Current\nCue\nPower:\n" + str(self.currentPower) + "%")

        # this function is called when the "hit ball" button is pressed
        def hitBall():
            self.hitButton['state'] = DGG.DISABLED
            self.hitButton['relief'] = 'sunken'
            cuePower = self.cuePower['value']
            self.hitBallHandler(cuePower)

        # this function is called when the "show instructions" button is pressed
        def showInstructions():
            self.showinst = not self.showinst
            self.hitButton['relief'] = 'sunken'
            self.instructionsHandler()

        # this function is called when the "return to menu" button is pressed
        def eightToMenu():
            self.deInit8Ball()
            self.initMenuScreen()
        
        # actually calls all the helper functions
        loadTable(self)
        loadLighting(self)
        initBalls(self)
        loadHUD(self)
        self.disableMouse()
        camera.setPos(2, 90, 70)

        # variables relating to wall collisions
        wL = self.wallLst = [self.bottomCushion.getTightBounds(self.dot),
            self.topCushion.getTightBounds(self.dot),
            self.bottomLeftCushion.getTightBounds(self.dot),
            self.bottomRightCushion.getTightBounds(self.dot),
            self.topLeftCushion.getTightBounds(self.dot),
            self.topRightCushion.getTightBounds(self.dot)]

        rT = self.railThickness = [wL[0][1][1]-wL[0][0][1],
            wL[1][1][1]-wL[1][0][1],
            wL[2][1][0]-wL[2][0][0],
            wL[3][1][0]-wL[3][0][0],
            wL[4][1][0]-wL[4][0][0],
            wL[5][1][0]-wL[5][0][0]]

        pC = self.pocketCorners = [(wL[0][0][0] + rT[0], wL[0][1][1]),
            (wL[0][1][0] - rT[0], wL[0][1][1]),
            (wL[1][0][0] + rT[1], wL[1][0][1]),
            (wL[1][1][0] - rT[1], wL[1][0][1]),
            (wL[2][1][0], wL[2][0][1] + rT[2]),
            (wL[2][1][0], wL[2][1][1] - rT[2]),
            (wL[3][0][0], wL[3][0][1] + rT[3]), 
            (wL[3][0][0], wL[3][1][1] - rT[2]),
            (wL[4][1][0], wL[4][0][1] + rT[4]),
            (wL[4][1][0], wL[4][1][1] - rT[4]),
            (wL[5][0][0], wL[5][0][1] + rT[5]),
            (wL[5][0][0], wL[5][1][1] - rT[5])]

    # removes all the assets of eight ball from memory
    def deInit8Ball(self):
        self.gameMode = 0

        def unloadLighting(self):
            render.clearLight(self.ambLightNode)
            render.clearLight(self.dnlp)
            render.clearLight(self.rnlp)

        def unloadBalls(self):
            for ball in self.ballModelList:
                ball.removeNode()

        def unloadHUD(self):
            self.cueCtrlFrame.removeNode()
            self.pottedBallsFrame.removeNode()
            self.cueLine.reset()
            self.objBallLine.reset()
            self.reboundLine.reset()

        taskMgr.remove("moveCameraTask")
        taskMgr.remove("showBallsTask")
        taskMgr.remove("moveBallsTask")
        taskMgr.remove("showTrajectoryTask")
        taskMgr.remove("gameStateTask")
        taskMgr.remove("mouseTask")

        self.origin.removeNode()
        self.tableFloater.removeNode()
        self.modelRoot.removeNode()
        unloadLighting(self)
        unloadHUD(self)
        unloadBalls(self)

    # wrapper function that loads all the variables and models for 9 ball
    def init9Ball(self):
        self.gameMode = 9
        self.currentPlayer = 0
        self.continueTurn = False
        self.calculated = True
        self.firstContact = None

        # these set up the controller keys
        self.keyMap = {"cam-left": 0, "cam-right": 0, "cam-down": 0, "cam-up": 0,
            "cam-fine": False}

        self.accept("a", self.setKey, ["cam-left", True])
        self.accept("d", self.setKey, ["cam-right", True])
        self.accept("w", self.setKey, ["cam-down", True])
        self.accept("s", self.setKey, ["cam-up", True])
        self.accept("a-up", self.setKey, ["cam-left", False])
        self.accept("d-up", self.setKey, ["cam-right", False])
        self.accept("w-up", self.setKey, ["cam-down", False])
        self.accept("s-up", self.setKey, ["cam-up", False])

        self.accept("space", self.deInit9Ball)

        self.accept("shift", self.setKey, ["cam-fine", True])
        self.accept("control", self.setKey, ["cam-fine", False])
        self.accept("enter", self.hitBallHandler)
        self.accept("escape", sys.exit)

        self.accept("mouse1", self.grabBall)
        self.accept("mouse1-up", self.releaseBall)

        self.accept("r", self.resetCamera)

        self.origin = render.attachNewNode("origin")
        self.origin.setPos(0, 0, 0)
        self.tableFloater = self.origin.attachNewNode("tableFloater")

        self.ballsDone = True
        self.scratched = False
        self.placing = False
        self.gameOver = False
        self.gameOverEight = False
        self.grabbed = False

        # the task manager runs every frame and does the calculations
        taskMgr.add(self.moveCamera, "moveCameraTask")
        taskMgr.add(self.showBalls, "showBallsTask")
        taskMgr.add(self.moveBalls, "moveBallsTask")
        taskMgr.add(self.showTrajectory, "showTrajectoryTask")
        taskMgr.add(self.gameState, "gameStateTask")
        taskMgr.add(self.mouseTask, "mouseTask")

        # this is code used for picking up the cue ball when it scratches
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.pickerNode = CollisionNode("mouseRay")
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)

        # loads all the models for the table and attach textures to it
        def loadTable(self):
            self.modelRoot = render.attachNewNode("modelRoot")

            cherry = loader.loadTexture("models/cherry.png")
            aluminum = loader.loadTexture("models/brushed_aluminum.png")
            leather = loader.loadTexture("models/leather.png")
            fabric = loader.loadTexture("models/dobby.png")

            self.tableSurface = loader.loadModel("models/table_surface")
            self.tableSurface.setTexture(fabric)
            bounds = self.tableSurface.getTightBounds()
            scale = 44 / (bounds[1] - bounds[0])[0]
            self.tableSurface.setScale(scale)
            self.tableSurface.reparentTo(self.modelRoot)
            
            self.tableEdge = loader.loadModel("models/table_edge")
            self.tableEdge.setTexture(cherry)
            self.tableEdge.setScale(scale)
            self.tableEdge.reparentTo(self.modelRoot)

            self.bottomCushion = loader.loadModel("models/table_bottom_cushion")
            self.bottomCushion.setTexture(fabric)
            self.bottomCushion.setScale(scale)
            self.bottomCushion.reparentTo(self.modelRoot)

            self.topCushion = loader.loadModel("models/table_top_cushion")
            self.topCushion.setTexture(fabric)
            self.topCushion.setScale(scale)
            self.topCushion.reparentTo(self.modelRoot)

            self.bottomRightCushion = loader.loadModel("models/table_bottomRight_cushion")
            self.bottomRightCushion.setTexture(fabric)
            self.bottomRightCushion.setScale(scale)
            self.bottomRightCushion.reparentTo(self.modelRoot)

            self.bottomLeftCushion = loader.loadModel("models/table_bottomLeft_cushion")
            self.bottomLeftCushion.setTexture(fabric)
            self.bottomLeftCushion.setScale(scale)
            self.bottomLeftCushion.reparentTo(self.modelRoot)

            self.topRightCushion = loader.loadModel("models/table_topRight_cushion")
            self.topRightCushion.setTexture(fabric)
            self.topRightCushion.setScale(scale)
            self.topRightCushion.reparentTo(self.modelRoot)

            self.topLeftCushion = loader.loadModel("models/table_topLeft_cushion")
            self.topLeftCushion.setTexture(fabric)
            self.topLeftCushion.setScale(scale)
            self.topLeftCushion.reparentTo(self.modelRoot)

            self.cornerPockets = loader.loadModel("models/table_pockets")
            self.cornerPockets.setTexture(leather)
            self.cornerPockets.setScale(scale)
            self.cornerPockets.reparentTo(self.modelRoot)

            self.cornerCovers = loader.loadModel("models/table_covers")
            self.cornerCovers.setTexture(aluminum)
            self.cornerCovers.setScale(scale)
            self.cornerCovers.reparentTo(self.modelRoot)
            
            coord1, coord2 = self.modelRoot.getTightBounds()
            size = coord2 - coord1
            self.modelRoot.setPos(-coord1[0] - size[0]/2, 
                -coord1[1] - size[1]/2, -coord1[2] - size[2])
            coord1, coord2 = self.tableSurface.getTightBounds()
            zShift = -coord2[2]
            self.modelRoot.setZ(zShift)

        # loads lighting in the scene and attaches the lighting to all the models
        def loadLighting(self):
            ambientLight = AmbientLight("ambientLight")
            ambientLight.setColor((0.55, 0.55, 0.7, 1))
            self.ambLightNode = render.attachNewNode(ambientLight)
            render.setLight(self.ambLightNode)

            directionalLight = DirectionalLight("directionalLight")
            directionalLight.setColor((0.8, 0.8, 0.8, 1))
            directionalLight.setSpecularColor((1, 1, 1, 1))
            self.dnlp = render.attachNewNode(directionalLight)
            self.dnlp.setHpr(0, -90, 0)
            render.setLight(self.dnlp)

            reflectionLight = DirectionalLight("reflectionLight")
            reflectionLight.setColor((0.01, 0.01, 0.1, 1))
            self.rnlp = render.attachNewNode(reflectionLight)
            self.rnlp.setHpr(0, 90, 0)
            render.setLight(self.rnlp)

        # loads the ball models as well as load Ball() objects that deal with collision
        def initBalls(self):
            coord1, coord2 = self.tableSurface.getTightBounds()
            size = coord2 - coord1
            self.dot = self.origin.attachNewNode("dot")
            self.dot.setY(-size[1]/4)

            lst = [1, 2, 3, 6, 4, 7, 8, 9, 5]

            sqrt3 = 3**0.5
            positions = {1: (0, 0), 
            2: (-1-SPACING, -(sqrt3+SPACING)), 3: (1+SPACING, -(sqrt3+SPACING)), 
            4: (-2-SPACING, -2*(sqrt3+SPACING)), 5: (0, -2*(sqrt3+SPACING)), 6: (2+SPACING, -2*(sqrt3+SPACING)),
            7: (0, -4*(sqrt3+SPACING)), 8: (-1-SPACING, -3*(sqrt3+SPACING)), 9: (1+SPACING, -3*(sqrt3+SPACING))}

            self.ballObjList = []
            r = 1
            index = 0
            for num in lst:
                index += 1
                temp_ball = ballClass.ball(index, r*positions[num][0], r*positions[num][1], 1)
                self.ballObjList.append(temp_ball)

            cue_ball = ballClass.ball(10, 0, 2*size[1]/4, 1)
            self.ballObjList.append(cue_ball)

            self.ball_1 = loader.loadModel("models/ball_1")
            self.ball_2 = loader.loadModel("models/ball_2")
            self.ball_3 = loader.loadModel("models/ball_3")
            self.ball_4 = loader.loadModel("models/ball_4")
            self.ball_5 = loader.loadModel("models/ball_5")
            self.ball_6 = loader.loadModel("models/ball_6")
            self.ball_7 = loader.loadModel("models/ball_7")
            self.ball_8 = loader.loadModel("models/ball_8")
            self.ball_9 = loader.loadModel("models/ball_9")
            self.cueBall = loader.loadModel("models/ballCue")
            self.ballModelList = [self.ball_1, self.ball_2, self.ball_3, self.ball_4,
                self.ball_5, self.ball_6, self.ball_7, self.ball_8, self.ball_9, self.cueBall]

            bounds = self.ball_1.getTightBounds()
            size = bounds[1] - bounds[0]
            scale = (r*2) / size[0]

            for ball in self.ballModelList:
                ball.reparentTo(self.dot)
                ball.setScale(scale)

            self.cueBall.find("**/ball").node().setIntoCollideMask(BitMask32.bit(1))

        # loads the heads up display, including cue power indicator, trajectory line, etc.
        def loadHUD(self):
            self.solidsPosList = [(0.01, 0, 0.365), (0.01, 0, 0.205), (0.01, 0, 0.045), 
                (0.01, 0, -0.115), (0.01, 0, -0.275), (0.01, 0, -0.435), (0.01, 0, -0.595)]
            self.stripesPosList = [(-0.01, 0, 0.365), (-0.01, 0, 0.205), (-0.01, 0, 0.045), 
                (-0.01, 0, -0.115), (-0.01, 0, -0.275), (-0.01, 0, -0.435), (-0.01, 0, -0.595)]

            self.currentPower = "Current\nCue\nPower:\n50%"
            width = base.win.getXSize()/2
            height = base.win.getYSize()/2
            xRatio = width/height
            fClr = (193, 126, 25) # rgb values of the frame color
            self.pottedBallStripes = set()
            self.pottedBallSolids = set()
            self.cueCtrlFrame = DirectFrame(pos = (xRatio,0,0), 
                frameSize = (-0.5, 0, -1, 1),
                frameColor = (fClr[0]/255, fClr[1]/255, fClr[2]/255, 0.2),
                relief = "raised", borderWidth = (0.03, 0.03))

            self.cuePowerFrame = DirectFrame(pos = (0, 0.5, 0))
            self.cuePowerFrame.reparentTo(self.cueCtrlFrame)
            self.cuePower = DirectSlider(range = (0, 100),
                value = 50, pageSize = 1, orientation = "vertical",
                pos = (-0.37, 0, 0.45), frameSize = (-0.3, 0.3, -0.5, 0.5),
                thumb_frameSize = (-0.07, 0.07, -0.05, 0.05),
                thumb_relief = "flat", command = showValue)
            self.cuePower.reparentTo(self.cuePowerFrame)
            self.cuePowerText = OnscreenText(text = str(self.currentPower),
                pos = (-0.28, 0.5,0), align = TextNode.ALeft)
            self.cuePowerText.reparentTo(self.cuePowerFrame)

            textColor = (256, 0, 0)
            self.currentPlayerText = OnscreenText(text = "Ball in Hand",
                pos = (-0.25, -0.5), scale = 0.06,
                fg = (textColor[0]/256, textColor[1]/256, textColor[2]/256, 1),
                shadow = (0,0,0, 0.8),
                mayChange = True,
                parent = self.cueCtrlFrame)

            self.hitButton = DirectButton(pos = (-0.25, 0, -0.85), 
                frameSize = (-0.2, 0.2, -0.1, 0.1), 
                relief = "raised", borderWidth = (0.01, 0.01),
                text = ("Hit Ball!", "Hit Ball!", "Hit Ball!", "Rolling"),
                text_scale = 0.05, command = hitBall)
            self.hitButton.reparentTo(self.cueCtrlFrame)

            self.pottedBallsFrame = DirectFrame(pos = (-xRatio, 0, 0),
                frameSize = (0, 0.5, -1, 1), 
                frameColor = (fClr[0]/255, fClr[1]/255, fClr[2]/255, 0.2),
                relief = "raised", borderWidth = (0.03, 0.03))
            self.pottedSolidsFrame = DirectFrame(pos = (0.24, 0, 0.5),
                frameSize = (-0.08, 0.1, -1.03, 0.455),
                relief = "flat")
            self.pottedSolidsFrame.reparentTo(self.pottedBallsFrame)

            self.showinst = False
            self.instButton = DirectButton(pos = (0.25, 0, -0.85),
                frameSize = (-0.2, 0.2, -0.1, 0.1),
                relief = "raised", borderWidth = (0.01, 0.01),
                text = ("Show\nInstructions"),
                text_scale = 0.05, command = showInstructions)
            self.instButton.reparentTo(self.pottedBallsFrame)

            self.menuButton = DirectButton(pos = (0.25, 0, -0.65),
                frameSize = (-0.2, 0.2, -0.1, 0.1),
                relief = "raised", borderWidth = (0.01, 0.01),
                text = "Return to Menu",
                text_scale = 0.05, command = nineToMenu)
            self.menuButton.reparentTo(self.pottedBallsFrame)

            self.cueLine = LineSegs()
            self.cueLine.moveTo(self.cueBall.getPos())
            self.cueLine.drawTo(self.cueBall.getPos())
            self.cueLineNode = NodePath(self.cueLine.create(dynamic = True))
            self.cueLineNode.reparentTo(self.dot)

            self.objBallLine = LineSegs()
            self.objBallLine.moveTo(self.cueBall.getPos())
            self.objBallLine.drawTo(self.cueBall.getPos())
            self.objBallLineNode = NodePath(self.objBallLine.create(dynamic = True))
            self.objBallLineNode.reparentTo(self.dot)

            self.reboundLine = LineSegs()
            self.reboundLine.moveTo(self.cueBall.getPos())
            self.reboundLine.drawTo(self.cueBall.getPos())
            self.reboundLineNode = NodePath(self.reboundLine.create(dynamic = True))
            self.reboundLineNode.reparentTo(self.dot)

        # helper function that shows the current cue power
        def showValue():
            self.currentPower = round(self.cuePower['value'])
            self.cuePowerText.setText("Current\nCue\nPower:\n" + str(self.currentPower) + "%")

        # this function is called when the "hit ball" button is pressed
        def hitBall():
            self.hitButton['state'] = DGG.DISABLED
            self.hitButton['relief'] = 'sunken'
            cuePower = self.cuePower['value']
            self.hitBallHandler(cuePower)

        # this function is called when the "show instructions" button is pressed
        def showInstructions():
            self.showinst = not self.showinst
            self.hitButton['relief'] = 'sunken'
            self.instructionsHandler()

        # this function is called when the "return to menu" button is pressed
        def nineToMenu():
            self.deInit9Ball()
            self.initMenuScreen()
        
        # actually calls all the helper functions
        loadTable(self)
        loadLighting(self)
        initBalls(self)
        loadHUD(self)
        self.disableMouse()
        camera.setPos(2, 90, 70)

        # variables relating to wall collisions
        wL = self.wallLst = [self.bottomCushion.getTightBounds(self.dot),
            self.topCushion.getTightBounds(self.dot),
            self.bottomLeftCushion.getTightBounds(self.dot),
            self.bottomRightCushion.getTightBounds(self.dot),
            self.topLeftCushion.getTightBounds(self.dot),
            self.topRightCushion.getTightBounds(self.dot)]

        rT = self.railThickness = [wL[0][1][1]-wL[0][0][1],
            wL[1][1][1]-wL[1][0][1],
            wL[2][1][0]-wL[2][0][0],
            wL[3][1][0]-wL[3][0][0],
            wL[4][1][0]-wL[4][0][0],
            wL[5][1][0]-wL[5][0][0]]

        pC = self.pocketCorners = [(wL[0][0][0] + rT[0], wL[0][1][1]),
            (wL[0][1][0] - rT[0], wL[0][1][1]),
            (wL[1][0][0] + rT[1], wL[1][0][1]),
            (wL[1][1][0] - rT[1], wL[1][0][1]),
            (wL[2][1][0], wL[2][0][1] + rT[2]),
            (wL[2][1][0], wL[2][1][1] - rT[2]),
            (wL[3][0][0], wL[3][0][1] + rT[3]), 
            (wL[3][0][0], wL[3][1][1] - rT[2]),
            (wL[4][1][0], wL[4][0][1] + rT[4]),
            (wL[4][1][0], wL[4][1][1] - rT[4]),
            (wL[5][0][0], wL[5][0][1] + rT[5]),
            (wL[5][0][0], wL[5][1][1] - rT[5])]

    # removes all the assets of nine ball from memory
    def deInit9Ball(self):
        self.gameMode = 0

        def unloadLighting(self):
            render.clearLight(self.ambLightNode)
            render.clearLight(self.dnlp)
            render.clearLight(self.rnlp)

        def unloadBalls(self):
            for ball in self.ballModelList:
                ball.removeNode()

        def unloadHUD(self):
            self.cueCtrlFrame.removeNode()
            self.pottedBallsFrame.removeNode()
            self.cueLine.reset()
            self.objBallLine.reset()
            self.reboundLine.reset()

        taskMgr.remove("moveCameraTask")
        taskMgr.remove("showBallsTask")
        taskMgr.remove("moveBallsTask")
        taskMgr.remove("showTrajectoryTask")
        taskMgr.remove("gameStateTask")
        taskMgr.remove("mouseTask")

        self.origin.removeNode()
        self.tableFloater.removeNode()
        self.modelRoot.removeNode()
        unloadLighting(self)
        unloadHUD(self)
        unloadBalls(self)

    # function that is called whenever a key is pressed,
    # and will update a global dictionary of key states
    def setKey(self, key, value):
        self.keyMap[key] = value

    # move camera every frame if certain keys are pressed
    def moveCamera(self, task):
        dt = globalClock.getDt()

        cameraAngle = self.camera.getP()
        if self.keyMap["cam-fine"]:
            if self.keyMap["cam-left"]:
                self.camera.setX(self.camera, -5 * dt * cos(radians(cameraAngle)))
            if self.keyMap["cam-right"]:
                self.camera.setX(self.camera, +5 * dt * cos(radians(cameraAngle)))
            if self.keyMap["cam-down"] and cameraAngle > -80:
                self.camera.setZ(self.camera, +40 * dt)
            if self.keyMap["cam-up"] and cameraAngle < -10:
                self.camera.setZ(self.camera, -40 * dt)
        else:
            if self.keyMap["cam-left"]:
                self.camera.setX(self.camera, -100 * dt * cos(radians(cameraAngle)))
            if self.keyMap["cam-right"]:
                self.camera.setX(self.camera, +100 * dt * cos(radians(cameraAngle)))
            if self.keyMap["cam-down"] and cameraAngle > -80:
                self.camera.setZ(self.camera, +80 * dt)
            if self.keyMap["cam-up"] and cameraAngle < -10:
                self.camera.setZ(self.camera, -80 * dt)

        if self.ballsDone and not self.placing:
            self.camera.lookAt(self.cueBall)
        else:
            self.camera.lookAt(self.origin)

        return task.cont

    # display the balls in Panda3D, updated every frame
    def showBalls(self, task):
        dt = globalClock.getDt()

        if dt > .2:
            return task.cont

        for ball in self.ballObjList:
            num = ball.number
            x, y, z = ball.getPos().getVector()
            if not ball.potted:
                self.ballModelList[num-1].setPos(x, y, z)

                ballV = LVector3f(ball.vel.getVector())
                prevRot = LRotationf(self.ballModelList[num-1].getQuat())
                axis = LVector3.up().cross(ballV)
                newRot = LRotationf(axis, 120.0 * ballV.length())
                self.ballModelList[num-1].setQuat(prevRot * newRot)
            elif num != 16 and self.gameMode == 8:
                self.ballModelList[num-1].detachNode()
            elif num != 10 and self.gameMode == 9:
                self.ballModelList[num-1].detachNode()

        return task.cont

    # calculates the velocity and moves the balls, updated every frame
    def moveBalls(self, task):
        dt = globalClock.getDt()

        if dt > .2:
            return task.cont

        for i in range(len(self.ballObjList)):
            ball = self.ballObjList[i]
            if not ball.potted:
                ball.move()
                for objBall in self.ballObjList[i+1:]:
                    if not objBall.potted and ball.isColliding(objBall):
                        ballVec, objBallVec = ballClass.ball.calculateTrajectory(ball, objBall)
                        ball.setVel(ballVec)
                        objBall.setVel(objBallVec)
                        if self.gameMode == 8:
                            if ball.number == 16 and self.firstContact == None:
                                self.firstContact = objBall.number
                            elif objBall.number == 16 and self.firstContact == None:
                                self.firstContact = ball.number
                        elif self.gameMode == 9:
                            if ball.number == 10 and self.firstContact == None:
                                self.firstContact = objBall.number
                            elif objBall.number == 10 and self.firstContact == None:
                                self.firstContact = ball.number
                self.testWallCollision(ball)
                ball.decelerate(FRIC)

                if ball.vel.magnitude() <= 0.010:
                    ball.vel = vectorClass.vector3(0,0,0)
            else:
                ball.setVel(vectorClass.vector3(0, 0, 0))

        self.ballsDone = True
        for ball in self.ballObjList:
            if ball.vel.magnitude() >= 0.005:
                self.ballsDone = False
                break

        # checks whether every shot was legal
        if self.ballsDone: 
            self.hitButton['state'] = DGG.NORMAL
            self.hitButton['relief'] = "raised"
            if self.gameMode == 8:
                if self.calculated == False:
                    if self.openTable == False:
                        if self.firstContact not in self.playerObj[self.currentPlayer]:
                            self.scratched = True
                            self.continueTurn = False
                    if not self.continueTurn:
                        self.currentPlayer = alternate(self.currentPlayer)
                self.calculated = True

                if len(self.pottedBallStripes) + len(self.pottedBallSolids) > 0:
                    self.openTable = False

            if self.gameMode == 9:
                if self.calculated == False:
                    if self.firstContact != targetNine(self.pottedBallSolids):
                        self.scratched = True
                        self.continueTurn = False
                    if not self.continueTurn:
                        self.currentPlayer = alternate(self.currentPlayer)
                self.calculated = True

        return task.cont

    # displays the trajectory of the cue ball, updated every frame
    def showTrajectory(self, task):
        self.cueLineNode.removeNode()
        self.objBallLineNode.removeNode()
        self.reboundLineNode.removeNode()
        if self.ballsDone and not self.placing:
            def testTrajectory(self):
                cuex, cuey, cuez = self.cueBall.getPos()
                ghostBall = ballClass.ball(-1, cuex, cuey, cuez)
                power = MAXPWR * 30 / 100
                camDir = self.camera.getHpr()[0]
                ghostBallVel = vectorClass.vector3(-power*sin(radians(camDir)), power*cos(radians(camDir)), 0)
                ghostBall.setVel(ghostBallVel)
                while True:
                    ghostBall.move()
                    for objBall in self.ballObjList:
                        if not objBall.potted and ghostBall.isColliding(objBall):
                            objBallVec = ballClass.ball.calculateTrajectory(ghostBall, objBall)[1]
                            return ghostBall.getPos(), objBall.getPos(), objBallVec
                    if self.testWallCollision(ghostBall):
                        return ghostBall.getPos(), ghostBall.getVel()

            result = testTrajectory(self)

            self.cueLine.moveTo(self.cueBall.getPos())
            self.cueLine.drawTo(result[0].getVector())
            self.cueLine.setThickness(4)
            self.cueLineNode = NodePath(self.cueLine.create(dynamic = True))
            self.cueLineNode.reparentTo(self.dot)

            if len(result) == 3:
                objPos = result[1].getVector()
                objBallVec = result[2]
                objBallVec.scaleVector(5)
                objVec = objBallVec.getVector()
                self.objBallLine.moveTo(objPos)
                self.objBallLine.drawTo(objPos[0] + objVec[0], objPos[1] + objVec[1], objPos[2] + objVec[2])
                self.objBallLine.setThickness(3)
                self.objBallLine.setColor(1, 0, 0, 1)
                self.objBallLineNode = NodePath(self.objBallLine.create(dynamic = True))
                self.objBallLineNode.reparentTo(self.dot)
            elif len(result) == 2:
                ghostPos = result[0].getVector()
                ghostBallVec = result[1]
                ghostBallVec.scaleVector(4)
                ghostVec = ghostBallVec.getVector()
                self.reboundLine.moveTo(ghostPos)
                self.reboundLine.drawTo(ghostPos[0] + ghostVec[0], ghostPos[1] + ghostVec[1], ghostPos[2] + ghostVec[2])
                self.reboundLine.setThickness(4)
                self.reboundLine.setColor(0, 1, 0, 1)
                self.reboundLineNode = NodePath(self.reboundLine.create(dynamic = True))
                self.reboundLineNode.reparentTo(self.dot)


        return task.cont

    # updates the gameState message on the right of the screen, updated every frame
    def gameState(self, task):
        if self.gameMode == 8:
            if self.scratched:
                self.currentPlayerText["text"] = "Current Player:\nPlayer %d\nBall in Hand" % (self.currentPlayer + 1)
            elif self.openTable:
                self.currentPlayerText["text"] = "Current Player:\nPlayer %d\nOpen Table" % (self.currentPlayer + 1)
            elif self.playerObj[self.currentPlayer] == set([1, 2, 3, 4, 5, 6, 7]):
                self.currentPlayerText["text"] = "Current Player:\nPlayer %d\nSolids" % (self.currentPlayer + 1)
            else:
                self.currentPlayerText["text"] = "Current Player:\nPlayer %d\nStripes" % (self.currentPlayer + 1)

            if self.gameOver:
                if self.playerObj[self.currentPlayer] == set([1, 2, 3, 4, 5, 6, 7]) and len(self.pottedBallSolids) == 7:
                    self.currentPlayerText['text'] = "GAME OVER!!\nPlayer %d wins!!" % (self.currentPlayer + 1)
                elif self.playerObj[self.currentPlayer] == set([9, 10, 11, 12, 13, 14, 15]) and len(self.pottedBallStripes) == 7:
                    self.currentPlayerText['text'] = "GAME OVER!!\nPlayer %d wins!!" % (self.currentPlayer + 1)
                else:
                    self.currentPlayerText['text'] = "GAME OVER!!\nPlayer %d wins!!" % (int(alternate(self.currentPlayer)) + 1)
        if self.gameMode == 9:
            if self.scratched:
                self.currentPlayerText['text'] = "Current Player:\nPlayer %d\nBall in Hand" % (self.currentPlayer + 1)
            else:
                self.currentPlayerText['text'] = "Current Player:\nPlayer %d\nTarget: %d" % (self.currentPlayer + 1, targetNine(self.pottedBallSolids))

            if self.gameOver:
                self.currentPlayerText['text'] = "GAME OVER!!\nPlayer %d wins!!" % (self.currentPlayer + 1)

        return task.cont

    # tracks whether the mouse cursor is hovering over the ball, and allows the ball to be picked up when scratched
    def mouseTask(self, task):
        # This task deals with dragging the cue ball:
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()

            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            if self.placing == True:
                nearPoint = self.dot.getRelativePoint(camera, self.pickerRay.getOrigin())
                nearVec = self.dot.getRelativeVector(camera, self.pickerRay.getDirection())
                self.cueBall.setPos(PointAtZ(1, nearPoint, nearVec))
                if self.gameMode == 8:
                    self.ballObjList[15].setPos(PointAtZ(1, nearPoint, nearVec))
                elif self.gameMode == 9:
                    self.ballObjList[9].setPos(PointAtZ(1, nearPoint, nearVec))

            self.picker.traverse(self.cueBall)
            if self.pq.getNumEntries() > 0:
                self.grabbed = True

        return task.cont

    # picks up the ball
    def grabBall(self):
        if self.grabbed and self.scratched:
            self.placing = True

    # releases the ball
    def releaseBall(self):
        if self.grabbed:
            self.placing = False
            self.grabbed = False

    # resets the camera at a closer position to the cue ball
    def resetCamera(self):
        camera.setPos(2, 90, 70)

    # calculates whether the ball collides with a wall or pocket
    def testWallCollision(self, ball):        
        ballx, bally = ball.x, ball.y
        balldx, balldy = ball.vel.dx, ball.vel.dy
        ballr = 1

        def setPotted(self, ball):
            ballNum = ball.number
            ball.setPotted()
            if self.gameMode == 8:
                if ballNum > 0 and ballNum < 8:
                    if self.playerObj[self.currentPlayer] == None:
                        self.playerObj[self.currentPlayer] = set([i for i in range(1, 8)])
                        self.playerObj[alternate(self.currentPlayer)] = set([i for i in range(9, 16)])
                        self.continueTurn = True
                    elif ballNum in self.playerObj[self.currentPlayer]:
                        self.continueTurn = True
                    self.showPottedSolids(ballNum)
                elif ballNum > 8 and ballNum < 16:
                    if self.playerObj[self.currentPlayer] == None:
                        self.playerObj[self.currentPlayer] = set([i for i in range(9, 16)])
                        self.playerObj[alternate(self.currentPlayer)] = set([i for i in range(1, 8)])
                        self.continueTurn = True
                    elif ballNum in self.playerObj[self.currentPlayer]:
                        self.continueTurn = True
                    self.showPottedStripes(ballNum)
                elif ballNum == 16:
                    self.scratched = True
                    ball.potted = False
                elif ballNum == 8:
                    self.gameOver = True
            elif self.gameMode == 9:
                if ballNum > 0 and ballNum < 9:
                    self.showPottedSolids(ballNum)
                    self.continueTurn = True
                elif ballNum == 9 and self.scratched == False:
                    self.gameOver = True
                elif ballNum == 9 and self.scratched == True:
                    ball.potted = False
                elif ballNum == 10:
                    self.scratched = True
                    ball.potted = False

        if bally - ballr <= self.wallLst[0][1][1] and balldy < 0:
            if ballx < self.pocketCorners[0][0] and balldx < 0:
                setPotted(self, ball)
            elif ballx > self.pocketCorners[1][0] and balldx > 0:
                setPotted(self, ball)
            else:
                ball.vel.dy *= -1
                ball.decelerate(FRIC*1.4)
            return True
        elif bally + ballr >= self.wallLst[1][0][1] and balldy > 0:
            if ballx < self.pocketCorners[2][0] and balldx < 0:
                setPotted(self, ball)
            elif ballx > self.pocketCorners[3][0] and balldx > 0:
                setPotted(self, ball)
            else:
                ball.vel.dy *= -1
                ball.decelerate(FRIC*1.4)
            return True
        elif ballx - ballr <= self.wallLst[2][1][0] and balldx < 0:
            if bally < self.pocketCorners[4][1] and balldy < 0:
                setPotted(self, ball)
            elif bally > self.pocketCorners[9][1] and balldy > 0:
                setPotted(self, ball)
            elif bally < self.pocketCorners[8][1] and bally > self.pocketCorners[5][1]:
                setPotted(self, ball)
            else:
                ball.vel.dx *= -1
                ball.decelerate(FRIC*1.4)
            return True
        elif ballx + ballr >= self.wallLst[3][0][0] and balldx > 0:
            if bally < self.pocketCorners[6][1] and balldy < 0:
                setPotted(self, ball)
            elif bally > self.pocketCorners[11][1] and balldy > 0:
                setPotted(self, ball)
            elif bally < self.pocketCorners[10][1] and bally > self.pocketCorners[7][1]:
                setPotted(self, ball)
            else:
                ball.vel.dx *= -1
                ball.decelerate(FRIC*1.4)
            return True

    # updates the heads up display with the balls currently potted
    def showPottedSolids(self, ballNum):
        numPotted = len(self.pottedBallSolids)
        self.pottedBallSolids.add(ballNum)
        imagePath = "models/icons/icon" + str(ballNum) + ".png"
        ballHUD = OnscreenImage(image = imagePath, pos = self.solidsPosList[numPotted])
        ballHUD.setTransparency(TransparencyAttrib.MAlpha)
        ballHUD.setScale(0.08, 0.08, 0.08)
        ballHUD.reparentTo(self.pottedSolidsFrame)
        if len(self.pottedBallSolids) == 7:
            self.gameOver = True
    
    # updates the heads up display with the balls currently potted
    def showPottedStripes(self, ballNum):
        numPotted = len(self.pottedBallStripes)
        self.pottedBallStripes.add(ballNum)
        imagePath = "models/icons/icon" + str(ballNum) + ".png"
        ballHUD = OnscreenImage(image = imagePath, pos = self.stripesPosList[numPotted])
        ballHUD.setTransparency(TransparencyAttrib.MAlpha)
        ballHUD.setScale(0.08, 0.08, 0.08)
        ballHUD.reparentTo(self.pottedStripesFrame)
        if len(self.pottedBallStripes) == 7:
            self.gameOver = True

    # function is called whenever the hit ball button is pressed
    def hitBallHandler(self, powerScale = 30):
        self.calculated = False
        self.continueTurn = False
        self.firstContact = None
        self.scratched = False
        power = MAXPWR * powerScale / 100
        camDir = self.camera.getHpr()[0]
        cueBallVel = vectorClass.vector3(-power*sin(radians(camDir)), power*cos(radians(camDir)), 0)
        self.ballObjList[-1].setVel(cueBallVel)

    # function is called whenever the instructions button is pressed
    def instructionsHandler(self):
        instructionsText = """Instructions:
A. Pan Camera - right
D. Pan Camera - left
S. Pan Camera - up
W. Pan Camera - down
Shift. Fine Camera speed
Ctrl. Fast Camera speed
        """
        instColor = (244, 173, 66)
        if self.showinst:
            self.instTextObject = OnscreenText(text = instructionsText, 
                pos = (-1.2, 0.9), scale = 0.05,
                fg = (instColor[0]/256, instColor[1]/256, instColor[2]/256, 1),
                align = TextNode.ALeft)
            self.instButton["text"] = ("Hide\nInstructions")
            self.instButton['relief'] = "sunken"
        else:
            self.instTextObject.removeNode()
            self.instButton["text"] = ("Show\nInstructions")
            self.instButton['relief'] = "raised"

    # changes the screen from menu screen to eight ball
    def menuToEight(self):
        self.deInitMenuScreen()
        self.init8Ball()

    # changes the screen from menu screen to nine ball
    def menuToNine(self):
        self.deInitMenuScreen()
        self.init9Ball()

# returns a position on the z = 0 plane where the mouse is pointing at
def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())

# alternate between 0 and 1
def alternate(num):
    if num == 0:
        return 1
    else:
        return 0

# finds the lowest unpotted ball in 9 ball
def targetNine(lst):
    for i in range(1, 10):
        if i not in lst:
            return i

app = play()
app.run()