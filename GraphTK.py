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
class NodeTk(LG.Node):
    def __init__(self, graph, id, pos, r_pix=12, name=None):
        self.r_pix = r_pix
        LG.Node.__init__(self, graph, id, pos, name)
        print("NodeTk.name: '%s'"%self.name)
        
        self.canvas = self.graph.canvas
        
        self.pix = self.graph.div2pix(self.pos)
        
        r = self.r_pix
        h, v = self.pix.h, self.pix.v
        self.itemId = self.canvas.create_oval(h-r, v-r, h+r, v+r, fill='blue') #"light blue"
        self.txtId  = self.canvas.create_text(h, v, text=self.name, fill="yellow")

    def setColor(self, color):
        self.canvas.itemconfig(self.itemId, fill=color)
    
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
        if 1:
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
        self.pixsPerDiv = min(pixPerDivX, pixPerDivY) # keep aspect ratio
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
            
    def findNodesAtXY(self, x, y):
        e = 0
        items = self.canvas.find_overlapping(x-e, y-e, x+e, y+e)
        nodes = []
        for item in items:
            try :
                node = self.itemIdToNode[item] # in node list ?
            except :
                continue
            if node not in nodes :
                nodes.append(node)
        return nodes
    
#------------------------------------------------------------

CVW, CVH = 640, 480

class GuiGame(TK.Frame):
    def __init__(self, parent):
        TK.Frame.__init__(self, parent)
        
        self.parent = parent
        
        self.showSolution = 0.0 # or 1.0
        self.solutionShownAt = 0.0 # from 0.0 (0%) to 1.0 (100%)

        mainMenu = TK.Menu(self.parent) # Barre de menu
        
        self.menuFile = TK.Menu(mainMenu)  # Menu fils menuFile 
        self.menuFile.add_command(label="Show solution", command=self.showSolutionOnOff)  # Ajout d'une option au menu fils menuFile 
        self.menuFile.add_separator() # Ajout d'une ligne separatrice 
        self.menuFile.add_command(label="Quitter", command=self.parent.quit) 
          
        self.menuMove = TK.Menu(mainMenu)  # Menu fils menuMove 
        self.menuMove.add_command(label="Up<->Down"   , command=self.flipUpDown)  # Ajout d'une option au menu fils menuMove 
        self.menuMove.add_command(label="Left<->Right", command=self.flipLeftRight)  # Ajout d'une option au menu fils menuMove 
        self.menuMove.add_command(label="Rotate180"   , command=self.Rotate180)  # Ajout d'une option au menu fils menuMove 
        self.menuMove.add_command(label="RotateCW"    , command=self.RotateCW )  # Ajout d'une option au menu fils menuMove 
        self.menuMove.add_command(label="RotateCCW"   , command=self.RotateCCW)  # Ajout d'une option au menu fils menuMove 
        self.menuMove.add_command(label="Mirror"      , command=self.Mirror   )  # Ajout d'une option au menu fils menuMove 
          
        menuHelp = TK.Menu(mainMenu) # Menu Fils 
        menuHelp.add_command(label="A propos", command=self.about) 
          
        mainMenu.add_cascade(label = "File", menu=self.menuFile) 
        mainMenu.add_cascade(label = "Moves", menu=self.menuMove) 
        mainMenu.add_cascade(label = "Aide", menu=menuHelp) 
        self.parent.config(menu = mainMenu) 
        
        self.canvas = TK.Canvas(self.parent, width=CVW, height=CVH, bg='light yellow')
        self.canvas.pack()
        
        self.graph = GraphTk(   self.canvas, 
                                #initialPostions  =LG.sailBoatNodesPos, 
                                solutionPositions=LG.sailBoatNodesPos, 
                                linksNodes       =LG.sailBoatlinks )
        
        self.shiftModifier = False
        self.ctrlModifier  = False
    
        self.moveGroup = False
        self.mouseX, self.mouseY = 0, 0
        self.nodesSelected = []
        self.nodesMirror   = [] # 2 and only 2 are need to define the mirror line
        
        self.canvas.bind("<ButtonPress-1>"  , self.onMousePress)   # <Button-1>
        self.canvas.bind("<ButtonRelease-1>", self.onMouseRelease) # <Button-1>
        self.canvas.bind('<Motion>', self.onMouseMove)
        if 1 :
            self.parent.bind("<KeyPress-Shift_L>"  , self.onShiftPress) # <Key>
            self.parent.bind("<KeyRelease-Shift_L>", self.onShiftRealease) # <Key>
        
        if 1 :
            self.parent.bind("<KeyPress-Control_L>"  , self.onCtrlPress) # <Key>
            self.parent.bind("<KeyRelease-Control_L>", self.onCtrlRealease) # <Key>
        
        self.canvas.bind("<Button-3>", self.popup)

        self.periodicTask()

    def popup(self, event):
        #print("popup")
        self.menuMove.post(event.x_root, event.y_root)

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
        
    def Rotate180(self):
        print("Rotate180")
        impactedLinks = LG.Rotate(self.nodesSelected, deg=180) #, rotCenterPos=None
        self.updateLinks(impactedLinks)
        
    def RotateCW(self):
        print("RotateCW")
        impactedLinks = LG.Rotate(self.nodesSelected, deg=-90) #, rotCenterPos=None
        self.updateLinks(impactedLinks)
        
    def RotateCCW(self):
        print("RotateCCW")
        impactedLinks = LG.Rotate(self.nodesSelected, deg=90) #, rotCenterPos=None
        self.updateLinks(impactedLinks)
        
    def Mirror(self):
        if len(self.nodesMirror) != 2 :
            print("Mirror needs exactly 2 mirror nodes(green) !")
            return # ======>
        impactedLinks = LG.mirror(self.nodesSelected, *self.nodesMirror)
        self.updateLinks(impactedLinks)
        
    def onShiftPress(self, event):
        if event.state == 9: return # ====>
        #print("onShiftPress Keycode:", event.keycode, "State:", event.state)
        self.shiftModifier = True
        
    def onShiftRealease(self, event):
        #print("onShiftRealease Keycode:", event.keycode, "State:", event.state)
        self.shiftModifier = False
        
    def onCtrlPress(self, event):
        if event.state == 9: return # ====>
        #print("onKeyPressed Keycode:", event.keycode, "State:", event.state)
        self.ctrlModifier = True
        
    def onCtrlRealease(self, event):
        #print("onKeyRealease Keycode:", event.keycode, "State:", event.state)
        self.ctrlModifier = False
        
    def periodicTask(self):
        self.showSolutionPeriodic()
        self.after(20, self.periodicTask)

    def about(self):
        print("Menu about")

    def showSolutionOnOff(self):
        if self.showSolution == 0.0 : 
            self.graph.NodesCopyPos(fromPos='pos' , toPos='posA')
            self.graph.NodesCopyPos(fromPos='posS', toPos='posB')
            self.showSolution = 1.0
            label = "Hide solution"
        else : 
            self.showSolution = 0.0
            label = "Show solution"
        print("showSolution :", self.showSolution)
        self.menuFile.entryconfig(1, label=label)
        
    def showSolutionPeriodic(self):    
        dSol = self.showSolution - self.solutionShownAt 
        if dSol == 0.0 : return # ========>
        
        dmax = 0.02001 # 50 steps
        if   dSol >  dmax : dSol =  dmax
        elif dSol < -dmax : dSol = -dmax
        self.solutionShownAt += dSol
        #print("solutionShownAt :", self.solutionShownAt)
        
        LG.morphing(self.graph.nodes, self.solutionShownAt)    
            
    def addNodesToSelection(self, nodes):
        for node in nodes:
            if node in self.nodesSelected:
                node.setColor('blue')
                self.nodesSelected.remove(node) # toggle
            else:
                node.setColor('red')
                self.nodesSelected.append(node)
    
    def resetSelection(self):
        for node in self.nodesSelected :
            node.setColor('blue')
        self.nodesSelected = []
        
    def reselectGroup(self, nodes):
        reselect = False
        for node in nodes:
            if node in self.nodesSelected : 
                reselect = True 
                break
        #print("reselectGroup :", reselect)
        return reselect
        
    def onMousePress(self, event):
        if self.solutionShownAt > 0.0 : return # =========>
        
        #print("\nonMousePress : x, y, shift, ctrl :", event.x, event.y, self.shiftModifier, self.ctrlModifier)
        self.mouseX, self.mouseY = event.x, event.y
        foundNodes = self.graph.findNodesAtXY(event.x, event.y)
        
        if self.shiftModifier :
            if len(foundNodes) == 1 : # normal case
                node = foundNodes[0]
                if node in self.nodesMirror:
                    node.setColor('blue')
                    self.nodesMirror.remove(node) # toggle
                else:
                    node.setColor('green')
                    self.nodesMirror.append(node)
            return # =========>
        else:    
            if len(foundNodes) == 0 :
                print("no node found => resetSelection")
                self.resetSelection()
                return # =========>
            if 1:
                foundNodesNames = [n.name for n in foundNodes]
                print("nodes found :", foundNodesNames)
                    
            if self.ctrlModifier : 
                self.addNodesToSelection(foundNodes)
                return # =========>
                
            if self.reselectGroup(foundNodes):
                self.moveGroup = True
                return # =========>
                
            self.addNodesToSelection(foundNodes)
            self.moveGroup = True
            
    def onMouseMove(self, event):
        if self.solutionShownAt > 0.0 : return # =========>
        
        if self.moveGroup:
            dx, dy = event.x - self.mouseX, event.y - self.mouseY 
            self.mouseX, self.mouseY = event.x, event.y
            #print("Mouse Down Move x, y, dx, dy :", event.x, event.y, dx, dy)
            for node in self.nodesSelected :
                node.move_dhdv(dx, dy)
    
    def onMouseRelease(self, event):
        if self.solutionShownAt > 0.0 : return # =========>
        if self.moveGroup :
            self.moveGroup = False
            dx, dy = event.x - self.mouseX, event.y - self.mouseY 
            self.mouseX, self.mouseY = event.x, event.y
            #print("Mouse Release x, y, dx, dy :", event.x, event.y, dx, dy)
            for node in self.nodesSelected :
                node.move_dhdv(dx, dy)
            if len(self.nodesSelected) == 1 :
                self.resetSelection()
        
#=================================================================

if __name__ == "__main__":
    root = TK.Tk()
    root.title(__file__)
    guiGame = GuiGame(root)
    
    root.mainloop()
