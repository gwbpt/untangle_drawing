#!/usr/bin/env python
"""
from untangle
"""

from __future__ import print_function, division

version="0.1"

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
    def __init__(self, canvas, i, xy, xy0, r=12):
        self.canvas = canvas
        self.solved_xy = xy
        x, y = xy0
        self.x, self.y = x, y
        self.id = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue", tags="node")
        self.txtId = self.canvas.create_text(x, y, text=str(i), fill="yellow")
        self.links = []
        
    def addLink(self, n, lnk):
        self.links.append(lnk)

    def setColor(self, color):
        self.canvas.itemconfig(self.id, fill=color)
    
    def getPos(self, x, y):
        xy = self.canvas.coords(self.id)
        print("xy :", xy)
    
    def move_dxdy(self, dx, dy):
        self.x += dx
        self.y += dy
        
        self.canvas.move(self.id   , dx, dy)
        self.canvas.move(self.txtId, dx, dy)
        
        for lnk in self.links : 
            lnk.updateNodes()
            
    def move_to_xy(self, x, y):
        self.canvas.move(self.id   , self.x, self.y)
        self.canvas.move(self.txtId, self.x, self.y)
        
    def solve(self, k=1.0):
        '''
        k interpolation factor
        k = 0.0 : no solve, k = 1.0 : full solve
        '''
        self.canvas.move(self.id   , x, y)
        self.canvas.move(self.txtId, self.x, self.y)
        
        
class Link:
    def __init__(self, canvas, i, node0, node1, e=3):
        self.canvas = canvas
        self.node0, self.node1 = node0, node1
        self.id = None
        self.updateNodes()

    def updateNodes(self):
        xys = self.node0.x, self.node0.y, self.node1.x, self.node1.y
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
        
        self.canvas = TK.Canvas(parent, width=CVW, height=CVH)
        self.canvas.pack()
        
        xs, ys = zip(*xys) # unzip
        
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        
        self.drawingW, self.drawingH = xmax-xmin, ymax-ymin
        self.xC, self.yC = 0.5*(xmin+xmax), 0.5*(ymin+ymax) # center of drawing
        print("drawingW, drawingH:", self.drawingW, self.drawingH)
        print("drawingCenter :", self.xC, self.yC)
        
        self.xCpix, self.yCpix = CVW//2, CVH//2
        
        pixPerDivX, pixPerDivY = CVW/self.drawingW, CVH/self.drawingH
        self.pixsPerDiv = min(pixPerDivX, pixPerDivY) # keep aspect ratio
        print("pixsPerDiv :", self.pixsPerDiv)
        
        self.itemIdToNode = dict()
        nodes = []
        da = (2*pi) / len(xys)
        r = 0.5 * min(self.drawingW, self.drawingH)
        for i, xy in enumerate(xys):
            xy0    = self.xC + r*cos(i*da), self.yC + r*sin(i*da)
            xy0pix = self.div2pix(xy0) # initial pos in circle
            xy_pix = self.div2pix(xy)  # solved pos
            print(i, xy_pix)
            node = Node(self.canvas, i, xy_pix, xy0pix)
            self.itemIdToNode[node.id] = node
            nodes.append(node)
            
        links = []
        for i, (n0, n1) in enumerate(lnks):
            print(i, n0, n1)
            node0 = nodes[n0]
            node1 = nodes[n1]
            lnk = Link(self.canvas, i, node0, node1)
            links.append(lnk)
            node0.addLink(0, lnk)
            node1.addLink(1, lnk)
            
        self.mouseDown = False
        self.mouseX, self.mouseY = 0, 0
        self.nodesDragged = []
        self.canvas.bind("<ButtonPress-1>"  , self.onMousePress)   # <Button-1>
        self.canvas.bind("<ButtonRelease-1>", self.onMouseRelease) # <Button-1>
        self.canvas.bind('<Motion>', self.onMouseMove)
        
    def div2pix(self, xy):
        x, y = xy
        xp = self.xCpix + int((x-self.xC) * self.pixsPerDiv)
        yp = self.yCpix - int((y-self.yC) * self.pixsPerDiv)
        return xp, yp
    
    def onMousePress(self, event):
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
        if self.mouseDown:
            dx, dy = event.x - self.mouseX, event.y - self.mouseY 
            self.mouseX, self.mouseY = event.x, event.y
            #print("Mouse Down Move x, y, dx, dy :", event.x, event.y, dx, dy)
            for node in self.nodesDragged :
                node.move_dxdy(dx, dy)
    
    def onMouseRelease(self, event):
        self.mouseDown = False
        dx, dy = event.x - self.mouseX, event.y - self.mouseY 
        self.mouseX, self.mouseY = event.x, event.y
        print("Mouse Release x, y, dx, dy :", event.x, event.y, dx, dy)
        for node in self.nodesDragged :
            node.move_dxdy(dx, dy)
            node.setColor('blue')
    
#=================================================================

if __name__ == "__main__":
    root = TK.Tk()
    root.title(__file__)
    guiGame = GuiGame(root)
    
    root.mainloop()
