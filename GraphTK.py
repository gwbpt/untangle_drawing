#!/usr/bin/env python
"""
GWB
"""

from __future__ import print_function, division

version = 'v3.5'

import sys
print(sys.version_info)

if   sys.version_info.major == 2 :
    import Tkinter as TK
    import tkMessageBox
elif sys.version_info.major == 3 :
    import tkinter as TK
    from tkinter import messagebox as tkMessageBox
else : quit()

import GraphLogic as LG


class Pixel(LG.Vect2D):
    def __init__(self, x, y):
        LG.Vect2D.__init__(self, x,y)
        self.strFormat = "Pos(%7.1f,%7.1f)"
        
#--------------------------------------------------------

NORMAL, SELECTED, PIVOT = 0, 1, 2 # _status values
StatusColors = ('blue', 'red', 'green')
        
class NodeTk(LG.Node):
    def __init__(self, graph, id, pos, r_pix=12, name=None):
        self.r_pix = r_pix
        LG.Node.__init__(self, graph, id, pos, name)
        #print("NodeTk.name: '%s'"%self.name)
        
        self.canvas = self.graph.canvas
        
        self.pix = self.graph.div2pix(self.pos)
        
        r = self.r_pix
        x, y = self.pix.x, self.pix.y
        self.itemId = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill='blue', outline='') #"light blue"
        self.txtId  = self.canvas.create_text(x, y, text=self.name, fill="yellow")
        self.graph.itemIdToNode[self.itemId] = self # register itself in graph dict
        self._status = NORMAL
    
    def __str__(self):
        s = LG.Node.__str__(self) + "; %s"%self.pix
        return s
    
    def setStatus(self, status=NORMAL):
        if self._status == status : return # =========>
        
        self._status = status
        self.canvas.itemconfig(self.itemId, fill=StatusColors[status])
    
    def getStatus(self):
        return self._status
        
    def updatePos(self, updateLnk=False):
        #print("TK updatePos")
        self.setPix(self.graph.div2pix(self.pos), updateLnk=updateLnk)
        
    def setPix(self, pix, updateLnk=True):
        #print("TK setPix :", pix)
        self.pix = pix
        
        self.draw(updateLnk=True)
        
    def move_dhdv(self, dh, dv):
        self.pix.x += dh
        self.pix.y += dv
        #print("move_dhdv :", dh, dv, self.pix)
        self.pos = self.graph.pix2div(self.pix)
        
        self.draw(updateLnk=True)
        
    def draw(self, updateLnk=True):
        x, y, r = self.pix.x, self.pix.y, self.r_pix
        self.canvas.coords(self.itemId, x-r, y-r, x+r, y+r)
        self.canvas.coords(self.txtId, x, y)
        
        if updateLnk : self.updateLinks()
        
    def updateLinks(self):
        for lnk in self.links : 
            lnk.updateNodes()
                        
#---------------------------------------------        
class LinkTk(LG.Link):
    def __init__(self, graph, id, node0, node1, name=None):
        #print("LinkTk")
        LG.Link.__init__(self, graph, id, node0, node1, name=name)
        self.canvas        = self.graph.canvas
        self.lineThickness = self.graph.lineThickness
        #self.node0, self.node1 = node0, node1
        self.itemId = None
        self.updateNodes()

    def updateNodes(self):
        pix0 = self.node0.pix 
        pix1 = self.node1.pix 
        xys = pix0.x, pix0.y, pix1.x, pix1.y
        if self.itemId == None :
            self.itemId = self.canvas.create_line(xys, width=self.lineThickness, tags="link")
            self.canvas.tag_lower(self.itemId)
        else :
            self.canvas.coords(self.itemId, xys)
            
#------------------------------------------------------
class GraphTk(LG.Graph):
    def __init__(self, canvas, id=0, name='', lineThickness=None, **kwargs):
        if 0:
            print("GraphTk kwargs :")
            for key in kwargs: print(key, ':', kwargs[key])
            print("---------------------")
        self.canvas = canvas
        self.itemIdToNode = dict()
        self.lineThickness = lineThickness
        
        LG.Graph.__init__(self, id=id, name=name, nodeClass=NodeTk, linkClass=LinkTk, **kwargs) # id=0, name='', nodes=None, links=None
        
    def geomSetting(self, drawingW, drawingH):    
        if self.lineThickness == None :
            n = self.linksN
            if   n <= 20: self.lineThickness = 5
            elif n <= 25: self.lineThickness = 4
            elif n <= 33: self.lineThickness = 3
            elif n <= 50: self.lineThickness = 2
            else        : self.lineThickness = 1
            
        print("scaleAndCenter")
        rNode = 12
        self.centerPix = Pixel(CVW//2, CVH//2)
        w, h = CVW-3*rNode, CVH-3*rNode
        pixPerDivX, pixPerDivY = w/drawingW, h/drawingH
        ppd = min(pixPerDivX, pixPerDivY) # keep aspect ratio
        self.pixsPerDiv = float('%.2g'%ppd) # limitSignificantDigits
        print("pixsPerDiv :", self.pixsPerDiv)
        displayDivSize = w / self.pixsPerDiv, h / self.pixsPerDiv
        return w/self.pixsPerDiv, h/self.pixsPerDiv
       
    def div2pix(self, pos):
        #if not hasattr(self, 'pixsPerDiv'): self.scaleAndCenter()
        x = self.centerPix.x + int((pos.x-self.centerPos.x) * self.pixsPerDiv)
        y = self.centerPix.y - int((pos.y-self.centerPos.y) * self.pixsPerDiv)
        return Pixel(x, y)
            
    def pix2div(self, pix):
        #if not hasattr(self, 'pixsPerDiv'): self.scaleAndCenter()
        x  = self.centerPos.x + (pix.x - self.centerPix.x)/self.pixsPerDiv
        y  = self.centerPos.y - (pix.y - self.centerPix.y)/self.pixsPerDiv
        return LG.Position(x, y)
        
    def findNodesAmong(self, items):
        nodes = []
        for item in items:
            try :
                node = self.itemIdToNode[item] # in node list ?
            except :
                continue
            if node not in nodes :
                nodes.append(node)
        return nodes
        
    def findNodesAtXY(self, x, y):
        e = 0
        items = self.canvas.find_overlapping(x-e, y-e, x+e, y+e)
        return self.findNodesAmong(items)
    
    def findEnclosedNodes(self, xys):
        items = self.canvas.find_enclosed(*xys)
        return self.findNodesAmong(items)
        
#------------------------------------------------------------

CVW, CVH = 640, 480

REMOVE, NOP, ADD, TOGGLE = -1, 0, 1, 2 # selectionMode

PLAY, SHOW = 0, 1

rotationHelpText = '''Use mouse wheel
or move mouse while 'r' key pressed
with 2 or more selected nodes (red)
step of 5 deg

To select node :
while Ctrl-key pressed
mouse left-click on nodes'''

mirrorHelpText = '''Mirror needs exactly 2 pivot nodes(green) !
To select / deselect pivot node :
while Shilt-key pressed
mouse left-click on nodes'''

class GuiGame(TK.Frame):
    def __init__(self, parent, solutionPositions=None, linksNodes=None, initialPostions=None, n=None):
        TK.Frame.__init__(self, parent)
        
        self.parent = parent
        
        self.noSolutionProvided = (solutionPositions == None) 
        
        self.initMenus()
        
        self.canvas = TK.Canvas(self.parent, width=CVW, height=CVH, bg='light yellow')
        self.canvas.pack()
        
        self.graph = GraphTk( self.canvas, solutionPositions=solutionPositions, linksNodes=linksNodes, initialPostions=initialPostions, n=n )
        self.shiftModifier = False
        self.ctrlModifier  = False
        self.RkeyModifier  = False
        self.freeRotation  = False        
        self.moveGroup     = False
        self.selectionMode = NOP
        
        self.mouseX, self.mouseY = 0, 0
        self.selectionRect = None
        self.nodesSelected = []
        self.pivots   = [] # 2 and only 2 are need to define the mirror line
        
        self.initBindings()
        
        self.gameMode = PLAY
        
        self.nbSteps = 100 # 
        self.dt_ms   = 20 # transition time = nbSteps * dt_ms
        self.periodicTasks = list()
        self.periodicLoop()

    def periodicLoop(self):
        self.animateInterpolation()
        for periodicTask in tuple(self.periodicTasks):
            if periodicTask():
                self.periodicTasks.remove(periodicTask)
        self.after(self.dt_ms, self.periodicLoop)

    def initMenus(self):
        mainMenu = TK.Menu(self.parent)
        
        self.menuFile = TK.Menu(mainMenu)
        self.menuFile.add_command(label="Show inital pos", command=self.showInitial )
        self.menuFile.add_command(label="Show solution"  , command=self.showSolution)
        if self.noSolutionProvided: self.menuFile.entryconfig("Show solution", state="disabled")
        self.menuFile.add_command(label="Show current"   , command=self.showCurrent) 
        self.menuFile.add_separator() 
        self.menuFile.add_command(label="Print info"     , command=self.printInfo) 
        self.menuFile.add_separator()
        self.menuFile.add_command(label="Test"           , command=self.test) 
        self.menuFile.add_separator() 
        self.menuFile.add_command(label="Quitter", command=self.parent.quit) 
          
        self.menuMove = TK.Menu(mainMenu)  
        self.menuMove.add_command(label="Rotate Help" , command=self.RotateHelp) 
        self.MoveMenuLabelCmds = (  ("Rotate +90"  , self.RotateCCW    ),  
                                    ("Rotate -90"  , self.RotateCW     ), 
                                    ("Rotate 180"  , self.Rotate180    ), 
                                    ("Up<->Down"   , self.flipUpDown   ), 
                                    ("Left<->Right", self.flipLeftRight),
                                    ("Mirror"      , self.Mirror       ),  ) 
        for label, cmd in self.MoveMenuLabelCmds :
            self.menuMove.add_command(label=label, command=cmd)
            
        menuHelp = TK.Menu(mainMenu)
        menuHelp.add_command(label = "About", command=self.about) 
          
        mainMenu.add_cascade(label = "File" , menu=self.menuFile) 
        mainMenu.add_cascade(label = "Moves", menu=self.menuMove) 
        mainMenu.add_cascade(label = "Aide" , menu=menuHelp) 
        self.parent.config(menu = mainMenu)
        
    def moveMenuChangeState(self, state):
        for label, cmd in self.MoveMenuLabelCmds :
            self.menuMove.entryconfig(label, state=state)
            
    def enableMoveMenu (self): self.moveMenuChangeState("normal"  )
    def disableMoveMenu(self): self.moveMenuChangeState("disabled")
    
    #-----------------------------        
    def initBindings(self):    
        self.canvas.bind("<ButtonPress-1>"  , self.onMousePress)   # <Button-1>
        self.canvas.bind("<ButtonRelease-1>", self.onMouseRelease) # <Button-1>
        self.canvas.bind('<Motion>', self.onMouseMove)
        # with Windows OS
        self.canvas.bind('<MouseWheel>', self.onMouseWheel)
        '''
        # with Linux OS
        root.bind("<Button-4>", self.onMouseWheel)
        root.bind("<Button-5>", self.onMouseWheel)
        '''
        self.parent.bind("<KeyPress-Shift_L>"  , self.onShiftPress) 
        self.parent.bind("<KeyRelease-Shift_L>", self.onShiftRealease)
    
        self.parent.bind("<KeyPress-Control_L>"  , self.onCtrlPress)
        self.parent.bind("<KeyRelease-Control_L>", self.onCtrlRealease)
        
        self.parent.bind("<KeyPress>"  , self.onKeyPress)
        self.parent.bind("<KeyRelease>", self.onKeyRealease)
        
        self.canvas.bind("<Button-3>", self.popup)

    #---------------------------------------------------------------
    
    def test(self):
        for i in range(3):
            print("Solution.y :", self.graph.nodes[i].posList[LG.SOL_POS_IDX].y)
        for i in range(3):
            print("Pos.y      :", self.graph.nodes[i].pos.y)
    
    def info(self):
        s = "info:"
        for node in self.graph.nodes:
            s += "\n    %3d :%s; %s; '%s'"%(node.id, node.pos, node.pix, node.name)
        return s
    
    def about(self):
        print("Menu about")
        dialog = TK.Toplevel(self) #, width=320, height=240
        
        dialog.title("Help")
        if 0:
            TK.Label(dialog, text="Rotation").pack()
            wt = TK.Text(dialog, height=8, width=60)
            wt.insert(TK.END, rotationHelpText)
            wt.pack()
            
            TK.Label(dialog, text="Mirror").pack()
            wt = TK.Text(dialog, height=8, width=60)
            wt.insert(TK.END, mirrorHelpText)
            wt.pack()
        else:
            sb = TK.Scrollbar(dialog)
            tw = TK.Text(dialog, height=12, width=60)
            sb.pack(side=TK.RIGHT, fill=TK.Y)
            tw.pack(side=TK.LEFT, fill=TK.Y)
            sb.config(command=tw.yview)
            tw.config(yscrollcommand=sb.set)
            tw.insert(TK.END, rotationHelpText)
            tw.insert(TK.END, mirrorHelpText)
            
    def printInfo(self):
        print("\ngraph info :", self.graph)
        #print("\n" + self.info())
    
    def popup(self, event):
        #link contextual menu to Move menu
        self.menuMove.post(event.x_root, event.y_root)
        
    #--------------------- keys related callbacks -------------------    
    def onShiftPress   (self, event): self.shiftModifier = True
    def onShiftRealease(self, event): self.shiftModifier = False
    def onCtrlPress    (self, event): self.ctrlModifier  = True
    def onCtrlRealease (self, event): self.ctrlModifier  = False
        
    def onKeyPress(self, event):
        #print("onKeyPressed Keycode:", event.keycode, "State:", event.state)
        if event.keycode == 82 : self.RkeyModifier = True
        
    def onKeyRealease(self, event):
        #print("onKeyRealease Keycode:", event.keycode, "State:", event.state)
        if event.keycode == 82 : self.RkeyModifier = False
    
    #--------------------- move related callbacks -------------------    
    def updateLinks(self, links):
        for lnk in links:
            lnk.updateNodes()
            
    def flipUpDown(self):
        print("flipUpDown")
        impactedLinks = LG.flip(self.nodesSelected, mode=LG.UP_DOWN) #, centerPos=None
        self.updateLinks(impactedLinks)
        
    def flipLeftRight(self):
        print("flipLeftRight")
        impactedLinks = LG.flip(self.nodesSelected, mode=LG.LEFT_RIGHT) #, centerPos=None
        self.updateLinks(impactedLinks)
        
    def RotateHelp(self): tkMessageBox.showinfo("Rotate Help", rotationHelpText)
                
    def Rotate(self, deg=5):
        if len(self.nodesSelected) >= 2 :
            #print("Rotate %+d deg"%deg)
            if 0 :
                impactedLinks = LG.Rotate(self.nodesSelected, deg=deg) #, rotCenterPos=None
                self.updateLinks(impactedLinks)
            else:
                softRot = LG.SoftRotation(self.nodesSelected, deg=deg, nbSteps=1) # 1 step => hard rot
                softRot.rotate_da() # one step
        
    def Rotate180(self): self.RotateSoft(deg=180)
    def RotateCW (self): self.RotateSoft(deg=-90)
    def RotateCCW(self): self.RotateSoft(deg=+90)
        
    def RotateSoft(self, deg=90): 
        self.softRot = LG.SoftRotation(self.nodesSelected, deg=deg, nbSteps=self.nbSteps)
        self.periodicTasks.append(self.softRot.rotate_da)
    
    def Mirror(self):
        if len(self.pivots) != 2 :
            tkMessageBox.showwarning("Mirror", mirrorHelpText)
            return # ======>
        impactedLinks = LG.mirror(self.nodesSelected, *self.pivots)
        self.updateLinks(impactedLinks)
    
    #----------------------------------    
    
    def showSolution(self):
        self.disableMoveMenu()
        self.transitTo(targetIdx=LG.SOL_POS_IDX)
        
    def showInitial(self):
        self.disableMoveMenu()
        self.transitTo(targetIdx=LG.INIT_POS_IDX)
        
    def showCurrent(self):
        self.enableMoveMenu()
        self.transitTo(targetIdx=LG.STORE_POS_IDX)
        
    def transitTo(self, targetIdx):
        print("transitTo targetIdx, self.nbSteps :", targetIdx, self.nbSteps)
        if self.gameMode == PLAY :
            # save Play pos to posA
            LG.saveNodesPosTo(self.graph.nodes, toIdx=LG.STORE_POS_IDX)
            self.gameMode = SHOW
        self.targetIdx = targetIdx
        self.stepCnt = 0
        self.impactedLinks = LG.calculateStepToTargetNodes(self.graph.nodes, targetIdx=targetIdx, nbSteps=self.nbSteps)
        
    def animateInterpolation(self):    
        if self.gameMode == PLAY : return # =======>
        self.stepCnt += 1
        last = self.stepCnt >= self.nbSteps
        LG.executeStepToTargetForNodes(self.graph.nodes, last=last)
        self.updateLinks(self.impactedLinks)
        if last and self.targetIdx == LG.STORE_POS_IDX : 
            self.gameMode = PLAY
            print("gameMode <= PLAY")
        
    def removeNodeFromSelection(self, node):
        node.setStatus(NORMAL)
        self.nodesSelected.remove(node)
        
    def addNodeToSelection(self, node):
        status = node.getStatus()
        if status == SELECTED : return
        if status == PIVOT :
            self.removeNodeFromPivots(node)
        node.setStatus(SELECTED)
        self.nodesSelected.append(node)
        
    def removeNodeFromPivots(self, node):
        node.setStatus(NORMAL)
        self.pivots.remove(node)
        
    def addNodeToPivots(self, node):
        status = node.getStatus()
        if status == PIVOT : return
        if status == SELECTED :
            self.removeNodeFromSelection(node)
        node.setStatus(PIVOT)
        self.pivots.append(node)
        
    def addNodesToSelection(self, nodes, selectionMode=TOGGLE):
        for node in nodes:
            if node in self.nodesSelected:
                if selectionMode in (TOGGLE, REMOVE) :
                    self.removeNodeFromSelection(node)
            else:
                if selectionMode in (TOGGLE, ADD) :
                    self.addNodeToSelection(node)
    
    def resetSelection(self):
        #for node in self.nodesSelected : self.removeNodeFromSelection(node) # BAD !!!!
        for i in reversed(range(len(self.nodesSelected))) : self.removeNodeFromSelection(self.nodesSelected[i])
        assert len(self.nodesSelected) == 0
        
    def resetPivots(self):
        for i in reversed(range(len(self.pivots))) : self.removeNodeFromPivots(self.pivots[i])
        assert len(self.pivots) == 0
        
    def reselectGroup(self, nodes):
        reselect = False
        for node in nodes:
            if node in self.nodesSelected : 
                reselect = True 
                break
        #print("reselectGroup :", reselect)
        return reselect
        
    def onMousePress(self, event):
        if self.gameMode != PLAY : return # =========>
        #print("\nonMousePress : x, y, shift, ctrl :", event.x, event.y, self.shiftModifier, self.ctrlModifier)
        self.mouseX, self.mouseY = event.x, event.y
        foundNodes = self.graph.findNodesAtXY(event.x, event.y)
        
        if len(foundNodes) == 0 :
            if self.ctrlModifier :
                self.selectionMode = ADD
                color='red'
            elif self.shiftModifier : 
                self.selectionMode = REMOVE
                color='blue'
            else :
                self.selectionMode = NOP
            print("selectionMode :", self.selectionMode)
            if self.selectionMode in (ADD, REMOVE):
                self.xy0SelectionRect = self.mouseX, self.mouseY
                xys = self.mouseX, self.mouseY, self.mouseX, self.mouseY
                self.selectionRect = self.canvas.create_rectangle(xys, width=2, fill='', dash=(1, 1), outline=color)
            else:
                print("no node found => reset Pivots and Selection")
                self.resetSelection()
                self.resetPivots()
                return # =========>
                
        if self.shiftModifier :
            if len(foundNodes) == 1 : # normal case
                node = foundNodes[0]
                if node in self.pivots:
                    self.removeNodeFromPivots(node) # toggle
                else:
                    self.addNodeToPivots(node)
            return # =========>
        else:    
            if 1:
                foundNodesNames = [n.name for n in foundNodes]
                #print("nodes found :", foundNodesNames)
                    
            if self.ctrlModifier : 
                self.addNodesToSelection(foundNodes, selectionMode=TOGGLE)
                return # =========>
                
            if self.reselectGroup(foundNodes):
                self.moveGroup = True
                return # =========>
                
            self.addNodesToSelection(foundNodes, selectionMode=TOGGLE)
            self.moveGroup = True
    
    def moveNodesSelected_dhdv(self, dh, dv):
        for node in self.nodesSelected :
            node.move_dhdv(dh, dv)
    
    def onMouseMove(self, event):
        if self.selectionRect :
            x0, y0 = self.xy0SelectionRect
            xys = x0, y0, event.x, event.y
            self.canvas.coords(self.selectionRect, xys)
            return # ============>
        dx, dy = event.x - self.mouseX, event.y - self.mouseY 
        self.mouseX, self.mouseY = event.x, event.y
        if self.RkeyModifier : 
            if dy != 0 :
                self.Rotate(deg=dy)
                return # =========>
        if self.gameMode != PLAY : return # =========>
        #print("Mouse Move moveGroup :", self.moveGroup)
        if self.moveGroup: self.moveNodesSelected_dhdv(dx, dy)

    def onMouseWheel(self, event):
        #print("Mouse Wheel event .x, .y, .num, .delta :", event.x, event.y, event.num, event.delta)
        # respond to Linux or Windows wheel event
        
        if   event.num == 5 or event.delta == -120: rotate = -1
        elif event.num == 4 or event.delta ==  120: rotate = +1
        else                                      : rotate =  0
        
        if rotate != 0 :
            #print("Mouse Wheel rotate : %+d; moveGroup :"%rotate, self.moveGroup)
            self.Rotate(deg=5*rotate)
        
    def onMouseRelease(self, event):
        if self.gameMode != PLAY : return # =========>
        if self.selectionRect :
            x0, y0 = self.xy0SelectionRect
            xys = x0, y0, event.x, event.y
            self.canvas.coords(self.selectionRect, xys)
            color = None
            if self.ctrlModifier and self.selectionMode != ADD:
                self.selectionMode = ADD
                color='red'
            elif self.shiftModifier and self.selectionMode != REMOVE: 
                self.selectionMode = REMOVE
                color='blue'
            if color : node.setOutline('blue')
            enclosedNodes = self.graph.findEnclosedNodes(xys)
            self.addNodesToSelection(enclosedNodes, selectionMode=self.selectionMode)
            self.canvas.delete(self.selectionRect)
            self.selectionRect = None
            return # ============>
            
        if self.moveGroup :
            self.moveGroup = False
            dx, dy = event.x - self.mouseX, event.y - self.mouseY 
            self.mouseX, self.mouseY = event.x, event.y
            #print("Mouse Release x, y, dx, dy :", event.x, event.y, dx, dy)
            self.moveNodesSelected_dhdv(dx, dy)
            if len(self.nodesSelected) == 1 : self.resetSelection() # one node selection is temporary
        
#==========================================================================================

if __name__ == "__main__":
    root = TK.Tk()
    root.title('untangle_drawing ' + version)
    
    from datas import samples
    
    drawing = samples[0]    
    
    #solutionPositions, linksNodes, initialPostions, n = LG.sailBoatNodesPos, LG.sailBoatlinks, None, None
    #solutionPositions, linksNodes, initialPostions, n = LG.busNodesPos     , LG.buslinks     , None, None
    #solutionPositions, linksNodes, initialPostions, n = LG.sailBoatNodesPos, None            , None, None
    #solutionPositions, linksNodes, initialPostions, n = None               , None            , None, 12
    guiGame = GuiGame(root, solutionPositions=drawing['solxys'], linksNodes=drawing['links'], initialPostions=drawing['initxys'], n=drawing['nbPts'] )
    
    root.mainloop()
