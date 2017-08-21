#!/usr/bin/env python
"""
from untangle
"""
version = 'v0.3'

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
    def __init__(self, canvas, i, xy, xy0, r):
        self.canvas = canvas
        self.r = r
        self.solved_x, self.solved_y = xy
        x, y = xy0
        self.x, self.y = x, y
        self.id = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue", tags="node")
        self.txtId = self.canvas.create_text(x, y, text=str(i), fill="yellow")
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
    
    def move_dxdy(self, dx, dy):
        self.x += dx
        self.y += dy
        
        #self.canvas.move(self.id   , dx, dy)
        #self.canvas.move(self.txtId, dx, dy)
        self.setPos(self.x, self.y)
        
        for lnk in self.links : 
            lnk.updateNodes()
            
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
        
        self.showSolution = 0.0 # or 1.0
        self.solutionShownAt = 0.0 # from 0.0 (0%) to 1.0 (100%)

        mainmenu = TK.Menu(parent) # Barre de menu
        
        self.menuExample = TK.Menu(mainmenu)  # Menu fils menuExample 
        self.menuExample.add_command(label="Show solution", command=self.showSolutionOnOff)  # Ajout d'une option au menu fils menuFile 
        self.menuExample.add_separator() # Ajout d'une ligne separatrice 
        self.menuExample.add_command(label="Quitter", command=parent.quit) 
          
        menuHelp = TK.Menu(mainmenu) # Menu Fils 
        menuHelp.add_command(label="A propos", command=self.about) 
          
        mainmenu.add_cascade(label = "Exemple", menu=self.menuExample) 
        mainmenu.add_cascade(label = "Aide", menu=menuHelp) 
        parent.config(menu = mainmenu) 
        
        self.canvas = TK.Canvas(parent, width=CVW, height=CVH, bg='light yellow')
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
            node = Node(self.canvas, i, xy_pix, xy0pix, rNode)
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
            
        self.mouseDown = False
        self.mouseX, self.mouseY = 0, 0
        self.nodesDragged = []
        self.canvas.bind("<ButtonPress-1>"  , self.onMousePress)   # <Button-1>
        self.canvas.bind("<ButtonRelease-1>", self.onMouseRelease) # <Button-1>
        self.canvas.bind('<Motion>', self.onMouseMove)
        
        self.periodicTask()
        
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
        self.menuExample.entryconfig(1, label=label)
        
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
    
    def onMousePress(self, event):
        if self.solutionShownAt > 0.0 : return # =========>
        
        print("onMousePress :", event.x, event.y)
        self.mouseDown = True
        self.mouseX, self.mouseY = event.x, event.y
        e = 0
        items = self.canvas.find_overlapping(event.x-e, event.y-e, event.x+e, event.y+e)
        print("items :", items)
        
        self.nodesDragged = []
        for item in items:
            tags = self.canvas.gettags(item)
            print("item tags :", item, tags)
            try :
                node = self.itemIdToNode[item]
                #print("node :", node)
                self.nodesDragged.append(node)
            except :
                continue
        print("self.nodesDragged :", self.nodesDragged)
        
        for node in self.nodesDragged :
            node.setColor('red')

    def onMouseMove(self, event):
        if self.solutionShownAt > 0.0 : return # =========>
        
        if self.mouseDown:
            dx, dy = event.x - self.mouseX, event.y - self.mouseY 
            self.mouseX, self.mouseY = event.x, event.y
            #print("Mouse Down Move x, y, dx, dy :", event.x, event.y, dx, dy)
            for node in self.nodesDragged :
                node.move_dxdy(dx, dy)
    
    def onMouseRelease(self, event):
        if self.solutionShownAt > 0.0 : return # =========>
        
        self.mouseDown = False
        dx, dy = event.x - self.mouseX, event.y - self.mouseY 
        self.mouseX, self.mouseY = event.x, event.y
        print("Mouse Release x, y, dx, dy :", event.x, event.y, dx, dy)
        for node in self.nodesDragged :
            node.move_dxdy(dx, dy)
            node.setColor('blue')
            #x, y = node.getPos()
            #node.setPos(x=40, y=20)
    
#=================================================================

if __name__ == "__main__":
    root = TK.Tk()
    root.title(__file__)
    guiGame = GuiGame(root)
    
    root.mainloop()
