#!/usr/bin/env python
"""
from untangle
"""

from __future__ import print_function, division

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


class Pixel:
    def __init__(self, h, v):
        self.h = h
        self.v = v

    def __str__(self):
        return "Pix(%7.1f,%7.1f)"%(self.h, self.v)
        
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
        h, v = self.pix.h, self.pix.v
        self.itemId = self.canvas.create_oval(h-r, v-r, h+r, v+r, fill='blue') #"light blue"
        self.txtId  = self.canvas.create_text(h, v, text=self.name, fill="yellow")
        self._status = NORMAL

    def setStatus(self, status=NORMAL):
        if self._status == status : return # =========>
        
        self._status = status
        self.canvas.itemconfig(self.itemId, fill=StatusColors[status])
    
    def getStatus(self):
        return self._status
    
    def setPos(self, pos, updateLnk=True):
        #print("TK setPos x, y :", x, y)
        LG.Node.setPos(self, pos)
        self.setPix(self.graph.div2pix(self.pos), updateLnk=updateLnk)
        
    def setPix(self, pix, updateLnk=True):
        #print("TK setPix :", pix)
        self.pix = pix
        
        self.draw(updateLnk=True)
        
    def move_dhdv(self, dh, dv):
        self.pix.h += dh
        self.pix.v += dv
        #print("move_dhdv :", dh, dv, self.pix)
        self.pos = self.graph.pix2div(self.pix)
        
        self.draw(updateLnk=True)
        
    def draw(self, updateLnk=True):
        h, v, r = self.pix.h, self.pix.v, self.r_pix
        self.canvas.coords(self.itemId, h-r, v-r, h+r, v+r)
        self.canvas.coords(self.txtId, h, v)
        
        if updateLnk : self.updateLinks()
        
    def updateLinks(self):
        for lnk in self.links : 
            lnk.updateNodes()
                        
#---------------------------------------------        
class LinkTk(LG.Link):
    def __init__(self, graph, id, node0, node1, name=None, e=3):
        LG.Link.__init__(self, graph, id, node0, node1, name=name)
        self.canvas = self.graph.canvas
        #self.node0, self.node1 = node0, node1
        self.itemId = None
        self.updateNodes()

    def updateNodes(self):
        pix0 = self.node0.pix 
        pix1 = self.node1.pix 
        xys = pix0.h, pix0.v, pix1.h, pix1.v
        if self.itemId == None :
            self.itemId = self.canvas.create_line(xys, width=3, tags="link")
            self.canvas.tag_lower(self.itemId)
        else :
            self.canvas.coords(self.itemId, xys)
            
#------------------------------------------------------
class GraphTk(LG.Graph):
    def __init__(self, canvas, id=0, name='', e=3, **kwargs):
        if 0:
            print("GraphTk kwargs :")
            for key in kwargs: print(key, ':', kwargs[key])
        self.canvas = canvas
        self.e = e
        self.itemIdToNode = dict()
        LG.Graph.__init__(self, id=id, name=name, **kwargs) # id=0, name='', nodes=None, links=None
        
    def createAndAddNode(self, i, xy, r_pix=12, name=None):
        #print("TK.createAndAddNode")
        node = NodeTk(self, i, xy, name=name, r_pix=r_pix)
        self.itemIdToNode[node.itemId] = node
        self.nodes.append(node)
        return node
        
    def createAndAddLink(self, i, node0, node1, name=None, e=3):
        #print("TK.createAndAddLink")
        link = LinkTk(self, i, node0, node1, name=name, e=e)
        self.links.append(link)
        return link
        
    def scaleAndCenter(self):
        print("scaleAndCenter")
        rNode = 12
        self.centerPix = Pixel(CVW//2, CVH//2)
        pixPerDivX, pixPerDivY = (CVW-3*rNode)/self.drawingW, (CVH-3*rNode)/self.drawingH
        ppd = min(pixPerDivX, pixPerDivY) # keep aspect ratio
        self.pixsPerDiv = float('%.2g'%ppd) # limitSignificantDigits
        print("pixsPerDiv :", self.pixsPerDiv)
        
    def div2pix(self, pos):
        if not hasattr(self, 'pixsPerDiv'): self.scaleAndCenter()
        h = self.centerPix.h + int((pos.x-self.centerPos.x) * self.pixsPerDiv)
        v = self.centerPix.v - int((pos.y-self.centerPos.y) * self.pixsPerDiv)
        return Pixel(h, v)
            
    def pix2div(self, pix):
        #if not hasattr(self, 'pixsPerDiv'): self.scaleAndCenter()
        x  = self.centerPos.x + (pix.h - self.centerPix.h)/self.pixsPerDiv
        y  = self.centerPos.y - (pix.v - self.centerPix.v)/self.pixsPerDiv
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
    def __init__(self, parent):
        TK.Frame.__init__(self, parent)
        
        self.parent = parent
        
        self.dt_ms = 20 # periodic task
        self.dinterpolation = 0.02001
        self.interpolation_k = 0.0 # from 0.0 (0%) to 1.0 (100%)
        
        self.initMenus()
        
        self.canvas = TK.Canvas(self.parent, width=CVW, height=CVH, bg='light yellow')
        self.canvas.pack()
        
        self.graph = GraphTk(   self.canvas, 
                                #initialPostions  =LG.sailBoatNodesPos, 
                                solutionPositions=LG.sailBoatNodesPos, 
                                linksNodes       =LG.sailBoatlinks )
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
        
        self.periodicTask()

    def periodicTask(self):
        self.animateInterpolation()
        self.after(self.dt_ms, self.periodicTask)

    def initMenus(self):
        mainMenu = TK.Menu(self.parent) # Barre de menu
        
        self.menuFile = TK.Menu(mainMenu)  # Menu fils menuFile 
        self.menuFile.add_command(label="Show inital pos", command=self.showInitial )
        self.menuFile.add_command(label="Show solution"  , command=self.showSolution) 
        self.menuFile.add_command(label="Show current"   , command=self.showCurrent) 
        self.menuFile.add_separator() # Ajout d'une ligne separatrice 
        self.menuFile.add_command(label="Quitter", command=self.parent.quit) 
          
        self.menuMove = TK.Menu(mainMenu)  # Menu fils menuMove 
        self.menuMove.add_command(label="Rotate Help" , command=self.RotateHelp) 
        self.menuMove.add_command(label="Rotate +90"  , command=self.RotateCCW)  
        self.menuMove.add_command(label="Rotate -90"  , command=self.RotateCW ) 
        self.menuMove.add_command(label="Rotate 180"  , command=self.Rotate180) 
        self.menuMove.add_command(label="Up<->Down"   , command=self.flipUpDown) 
        self.menuMove.add_command(label="Left<->Right", command=self.flipLeftRight)
        self.menuMove.add_command(label="Mirror"      , command=self.Mirror)  
          
        menuHelp = TK.Menu(mainMenu) # Menu Fils 
        menuHelp.add_command(label="A propos", command=self.about) 
          
        mainMenu.add_cascade(label = "File", menu=self.menuFile) 
        mainMenu.add_cascade(label = "Moves", menu=self.menuMove) 
        mainMenu.add_cascade(label = "Aide", menu=menuHelp) 
        self.parent.config(menu = mainMenu)
        
    def enableMoveMenu(self):
        self.menuMove.entryconfig("Rotate +90"  , state="normal")
        self.menuMove.entryconfig("Rotate -90"  , state="normal")
        self.menuMove.entryconfig("Rotate 180"  , state="normal")
        self.menuMove.entryconfig("Up<->Down"   , state="normal")
        self.menuMove.entryconfig("Left<->Right", state="normal")
        self.menuMove.entryconfig("Mirror"      , state="normal")

    def disableMoveMenu(self):
        self.menuMove.entryconfig("Rotate +90"  , state="disabled")
        self.menuMove.entryconfig("Rotate -90"  , state="disabled")
        self.menuMove.entryconfig("Rotate 180"  , state="disabled")
        self.menuMove.entryconfig("Up<->Down"   , state="disabled")
        self.menuMove.entryconfig("Left<->Right", state="disabled")
        self.menuMove.entryconfig("Mirror"      , state="disabled")
        
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
        self.parent.bind("<KeyPress-Shift_L>"  , self.onShiftPress) # <Key>
        self.parent.bind("<KeyRelease-Shift_L>", self.onShiftRealease) # <Key>
    
        self.parent.bind("<KeyPress-Control_L>"  , self.onCtrlPress) # <Key>
        self.parent.bind("<KeyRelease-Control_L>", self.onCtrlRealease) # <Key>
        
        self.parent.bind("<KeyPress>"  , self.onKeyPress)    # <Key>
        self.parent.bind("<KeyRelease>", self.onKeyRealease) # <Key>
        
        self.canvas.bind("<Button-3>", self.popup)

    def about(self):
        print("Menu about")

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
            impactedLinks = LG.Rotate(self.nodesSelected, deg=deg) #, rotCenterPos=None
            self.updateLinks(impactedLinks)
        
    def Rotate180(self): self.Rotate(deg=180)
    def RotateCW (self): self.Rotate(deg=-90)
    def RotateCCW(self): self.Rotate(deg=+90)
        
    def Mirror(self):
        if len(self.pivots) != 2 :
            tkMessageBox.showwarning("Mirror", mirrorHelpText)
            return # ======>
        impactedLinks = LG.mirror(self.nodesSelected, *self.pivots)
        self.updateLinks(impactedLinks)
    
    #----------------------------------    
    def showSolution(self):
        self.disableMoveMenu()
        self.transitTo('posS')
        
    def showInitial(self):
        self.disableMoveMenu()
        self.transitTo('posI')
        
    def showCurrent(self):
        self.enableMoveMenu()
        self.transitTo('posA')
        
    def transitTo(self, pos):
        if self.gameMode == PLAY :
            # save Play pos to posA
            self.graph.NodesCopyPos(fromPos='pos' , toPos='posA')
            self.gameMode = SHOW
        self.targetPos = pos
        print("transitTo targetPos :", self.targetPos)
        
        
    def animateInterpolation(self):    
        if self.gameMode == PLAY : return # =======>
        dk = 1.0 - self.interpolation_k 
        if -1e-6 < dk < 1e-6 :
            if self.targetPos == 'posA' : self.gameMode == PLAY # stop animation
            return # ========>
        # interpolation speed = dmax/self.period_ms
        dmax = self.dinterpolation
        if   dk >  dmax : dk =  dmax
        elif dk < -dmax : dk = -dmax
        self.interpolation_k += dk
        #print("interpolation_k :", self.interpolation_k)
        LG.morphing(self.graph.nodes, self.targetPos, self.interpolation_k)    
        
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
        if self.interpolation_k > 0.0 : return # =========>
        
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
                print("nodes found :", foundNodesNames)
                    
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
        if self.interpolation_k > 0.0 : return # =========>
        #print("Mouse Move moveGroup :", self.moveGroup)
        if self.moveGroup: self.moveNodesSelected_dhdv(dx, dy)

    def onMouseWheel(self, event):
        #print("Mouse Wheel event .x, .y, .num, .delta :", event.x, event.y, event.num, event.delta)
        # respond to Linux or Windows wheel event
        rotate = 0
        if event.num == 5 or event.delta == -120:
            rotate = -1
        elif event.num == 4 or event.delta == 120:
            rotate = +1
        if rotate != 0 :
            #print("Mouse Wheel rotate : %+d; moveGroup :"%rotate, self.moveGroup)
            self.Rotate(deg=5*rotate)
        
    def onMouseRelease(self, event):
        if self.interpolation_k > 0.0 : return # =========>
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
        
#=================================================================

if __name__ == "__main__":
    root = TK.Tk()
    root.title(__file__)
    guiGame = GuiGame(root)
    
    root.mainloop()
