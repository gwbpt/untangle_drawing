#!/usr/bin/env python
"""
from untangle
"""

version = 'v1.0'

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

from math import cos, sin, pi

class Node:
    def __init__(self, canvas, xy, xy0, r, txt='*'):
        self.canvas = canvas
        self.r = r
        self.txt = txt
        self.solved_x, self.solved_y = xy
        x, y = xy0
        self.x, self.y = x, y
        self.id = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue")
        self.txtId = self.canvas.create_text(x, y, text=txt, fill="yellow")
        self.links = []
        
    def addLink(self, n, lnk):
        self.links.append(lnk)

    def setColor(self, color):
        self.canvas.itemconfig(self.id, fill=color)
    
    def getPos(self):
        xyText = self.canvas.coords(self.txtId)
        '''
        x0, y0, x1, y1 = self.canvas.coords(self.id)
        xyOval = 0.5*(x0+x1), 0.5*(y0+y1)
        print("getPos: ", xyText, xyOval)
        '''
        return xyText
        
    def setPos(self, x, y):
        x, y = int(x), int(y)
        #print("setPos x, y :", x, y)
        self.canvas.coords(self.id, x-self.r, y-self.r, x+self.r, y+self.r)
        self.canvas.coords(self.txtId, x, y)
        
    def updateLinks(self):
        for lnk in self.links : 
            lnk.updateNodes()
    
    def move_to_xy(self, x, y):
        self.x = x
        self.y = y
        #print("move_to_xy :",self.x, self.y)
        self.setPos(self.x, self.y)
        self.updateLinks()
    
    def move_dxdy(self, dx, dy):
        self.x += dx
        self.y += dy
        #print("move_dxdy :",self.x, self.y, dx, dy)
        self.setPos(self.x, self.y)
        self.updateLinks()
            
    def solve(self, k=1.0):
        '''
        k interpolation factor
        k = 0.0 : no solve, k = 1.0 : full solve
        '''
        x = self.x + k*(self.solved_x-self.x)
        y = self.y + k*(self.solved_y-self.y)
        self.setPos(x, y)
        
        
class Link:
    def __init__(self, canvas, i, node0, node1, e=3):
        self.canvas = canvas
        self.node0, self.node1 = node0, node1
        self.id = None
        self.updateNodes()

    def updateNodes(self):
        x0, y0 = self.node0.getPos() 
        x1, y1 = self.node1.getPos() 
        xys = x0, y0, x1, y1
        if self.id == None :
            self.id = self.canvas.create_line(xys, width=3, tags="link")
            self.canvas.tag_lower(self.id)
        else :
            self.canvas.coords(self.id, xys)
    
#------------------------------------------------------------
xys  = ((-4.0, 0.0), (0.0, 0.0), (6.0, 0.0), (-2.0, -1.0), (5.0, -1.0), (0.0, 10.0), (-1.0, 1.0), (0.0, 1.0), (5.0, 1.0), (0.0, 8.0))      
lnks = ((0, 1), (1, 2), (3, 4), (0, 3), (2, 4), (0, 9), (5, 9), (9, 7), (7, 1), (7, 8), (8, 5), (0, 6), (6, 9), (6, 1))     

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
          
        menuHelp = TK.Menu(mainMenu) # Menu Fils 
        menuHelp.add_command(label="A propos", command=self.about) 
          
        mainMenu.add_cascade(label = "File", menu=self.menuFile) 
        mainMenu.add_cascade(label = "Moves", menu=self.menuMove) 
        mainMenu.add_cascade(label = "Aide", menu=menuHelp) 
        self.parent.config(menu = mainMenu) 
        
        self.canvas = TK.Canvas(self.parent, width=CVW, height=CVH, bg='light yellow')
        self.canvas.pack()
        
        xs, ys = zip(*xys) # unzip
        
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        
        rNode = 12
        self.drawingW, self.drawingH = xmax-xmin, ymax-ymin
        self.xC, self.yC = 0.5*(xmin+xmax), 0.5*(ymin+ymax) # center of drawing
        print("drawingW, drawingH:", self.drawingW, self.drawingH)
        print("drawingCenter :", self.xC, self.yC)
        
        self.xCpix, self.yCpix = CVW//2, CVH//2
        
        pixPerDivX, pixPerDivY = (CVW-3*rNode)/self.drawingW, (CVH-3*rNode)/self.drawingH
        self.pixsPerDiv = min(pixPerDivX, pixPerDivY) # keep aspect ratio
        print("pixsPerDiv :", self.pixsPerDiv)
        
        self.itemIdToNode = dict()
        self.nodes = []
        da = (2*pi) / len(xys)
        r = 0.5 * min(self.drawingW, self.drawingH)
        for i, xy in enumerate(xys):
            xy0    = self.xC + r*cos(i*da), self.yC + r*sin(i*da)
            xy0pix = self.div2pix(xy0) # initial pos in circle
            xy_pix = self.div2pix(xy)  # solved pos
            print(i, xy_pix)
            node = Node(self.canvas, xy_pix, xy0pix, rNode, str(i))
            self.itemIdToNode[node.id] = node
            self.nodes.append(node)
            
        self.allLinks = []
        for i, (n0, n1) in enumerate(lnks):
            print(i, n0, n1)
            node0 = self.nodes[n0]
            node1 = self.nodes[n1]
            lnk = Link(self.canvas, i, node0, node1)
            self.allLinks.append(lnk)
            node0.addLink(0, lnk)
            node1.addLink(1, lnk)
            
        self.shiftModifier = False
        self.ctrlModifier  = False
    
        self.moveGroup = False
        self.mouseX, self.mouseY = 0, 0
        self.nodesSelected = []
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

    def flipUpDown(self):
        print("flipUpDown")
        xC, yC = self.groupCenter(self.nodesSelected)
        
        impactedLinks = set()
        for node in self.nodesSelected:
            x, y = node.getPos()
            node.move_to_xy(x, yC-(y-yC))
            impactedLinks |= set(node.links)
            
        for lnk in impactedLinks:
            lnk.updateNodes()
    
    def flipLeftRight(self):
        print("flipLeftRight")
        xC, yC = self.groupCenter(self.nodesSelected)
        
        impactedLinks = set()
        for node in self.nodesSelected:
            x, y = node.getPos()
            node.move_to_xy(xC-(x-xC), y)
            impactedLinks |= set(node.links)
            
        for lnk in impactedLinks:
            lnk.updateNodes()
        
    def Rotate180(self):
        print("Rotate180")
        xC, yC = self.groupCenter(self.nodesSelected)
        
        impactedLinks = set()
        for node in self.nodesSelected:
            x, y = node.getPos()
            node.move_to_xy(xC-(x-xC), yC-(y-yC))
            impactedLinks |= set(node.links)
            
        for lnk in impactedLinks:
            lnk.updateNodes()
        
    def RotateCW(self):
        print("RotateCW")
        
    def RotateCCW(self):
        print("RotateCCW")
        
    def groupCenter(self, nodes):
        n = len(nodes)
        sumX, sumY = 0.0, 0.0
        for node in nodes:
            x, y = node.getPos()
            sumX += node.x
            sumY += node.y
        return sumX/n, sumY/n   
        
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
        
        for node in self.nodes:
            node.solve(self.solutionShownAt)
        for lnk in self.allLinks:
            lnk.updateNodes()
        '''    
        self.canvas.update_idletasks()
        self.canvas.after(20)
        '''
    def div2pix(self, xy):
        x, y = xy
        xp = self.xCpix + int((x-self.xC) * self.pixsPerDiv)
        yp = self.yCpix - int((y-self.yC) * self.pixsPerDiv)
        return xp, yp
    
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
        if self.shiftModifier :
            self.rectStartXY = event.x, event.y
        else:    
            self.mouseX, self.mouseY = event.x, event.y
            foundNodes = self.findNodesAtXY(event.x, event.y)
            if len(foundNodes) == 0 :
                print("no node found => resetSelection")
                self.resetSelection()
                return # =========>
            if 1:
                foundNodesNames = [n.txt for n in foundNodes]
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
                node.move_dxdy(dx, dy)
    
    def onMouseRelease(self, event):
        if self.solutionShownAt > 0.0 : return # =========>
        if self.moveGroup :
            self.moveGroup = False
            dx, dy = event.x - self.mouseX, event.y - self.mouseY 
            self.mouseX, self.mouseY = event.x, event.y
            #print("Mouse Release x, y, dx, dy :", event.x, event.y, dx, dy)
            for node in self.nodesSelected :
                node.move_dxdy(dx, dy)
            if len(self.nodesSelected) == 1 :
                self.resetSelection()
        
#=================================================================

if __name__ == "__main__":
    root = TK.Tk()
    root.title(__file__)
    guiGame = GuiGame(root)
    
    root.mainloop()
