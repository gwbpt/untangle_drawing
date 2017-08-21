#!/usr/bin/env python

from __future__ import print_function, division

def limitSignificantDigits(f, n=3):
    if 0 :
        e10 = 0
        for i in range(12):
            if f >= 1000.0 :
                f /= 10.0
                e10 += 1 
                continue
            if f < 100.0 :
                f *= 10.0
                e10 -= 1
                continue
            break
        return int(f) * 10.0 ** e10
    else:
        format = '%%.%dg'%n # or format = r'%.' + str(n) + 'g'
        print("format :", format)
        s = format%f
        print("s :", s)
        return float(s)

if 0:
    n, f = 3, 0.00123456789 ; print("limitSignificantDigits(%f, n=%d) -> %4f"%(f, n, limitSignificantDigits(f)))
    print("f :", f)
    sg = '%.3g'%f  ; print("sg :", sg)
    fg = float(sg) ; print("fg :", fg)
    print("fg : '%s'"%fg)
    print("%s"% float('%.3g'%f))
    quit()

import random
from math import cos, sin, pi

DEG2RAD = pi/180

from numbers import Number

class Vect2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vect2D(self.x+other.x, self.y+other.y)
        
    def __sub__(self, other):
        return Vect2D(self.x-other.x, self.y-other.y)
        
    def __mul__(self, other):
        if isinstance(other, Number):
            #return Vect2D(self.x*other, self.y*other) # Position * float => vect2D !!!!
            return self.__class__(self.x*other, self.y*other) # create an instance of same class as self (inheritance)
        return self.x*other.x + self.y*other.y # scalar product
        
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def __str__(self):
        return "Vec(%7.2f,%7.2f)"%(self.x, self.y)
        
#---------------------------------
class Position(Vect2D):
    def __init__(self, x, y):
        Vect2D.__init__(self, x,y)
        
    def __str__(self):
        return "Pos(%7.2f,%7.2f)"%(self.x, self.y)
        
#--------------------------------------------------        
class Node:
    def __init__(self, graph, id, pos, name=None):
        self.graph = graph
        self.id    = id
        if name: self.name = name
        else   : self.name = chr(ord('A')+id)
        #print(self.name)
        self.pos  = pos  # current position
        self.posI = pos  # Initial
        self.posS = None # solution
        self.posA = None # Start interpolate
        self.posB = None # End   interpolate
        self.links = []
        
    def __str__(self):
        return "%3d :%s; '%s'"%(self.id, self.pos, self.name)
    
    def getPos(self):
        return self.pos
        
    def setPos(self, pos):
        self.pos = pos
        
    def setSelect(self, selected=True):
        self.selected = selected
    
    def addLink(self, lnk):
        self.links.append(lnk)

    def updateLinks(self):
        for lnk in self.links : 
            lnk.updateNodes()
            
    def interpolatedPos(self, k=0.5):
        if self.posA==None or self.posB==None : return None
        
        pA, pB = self.posA, self.posB
        dx, dy = pB.x-pA.x, pB.y-pA.y
        return Position(pA.x + k*dx, pA.y + k*dy)
    
#----------------------------------------------------------            
class Link:
    def __init__(self, graph, id, node0, node1, name=None):
        self.graph = graph
        self.id   = id
        if name: self.name = name
        else   : self.name = "%s->%s"%(node0.name, node1.name)
        self.node0, self.node1 = node0, node1

    def __str__(self):
        return "%3d :%3d <->%3d; '%s'"%(self.id, self.node0.id, self.node1.id, self.name)
    
#----------------------------------------------------------
           
def groupCenterPos(nodes):
    n = len(nodes)
    sumX, sumY = 0.0, 0.0
    for node in nodes:
        pos = node.pos
        sumX += pos.x
        sumY += pos.y
    return Position(sumX/n, sumY/n)   

UP_DOWN, LEFT_RIGHT = 1, 2    
    
def flip(nodes, centerPos=None, mode=UP_DOWN):
    if centerPos == None :
        centerPos = groupCenterPos(nodes)
    cp = centerPos
        
    impactedLinks = set()
    for node in nodes:
        np = node.pos
        if   mode == UP_DOWN :
            node.setPos(Position(np.x, cp.y-(np.y-cp.y)))
        elif mode == LEFT_RIGHT :
            node.setPos(Position(cp.x-(np.x-cp.x), np.y))
        
        impactedLinks |= set(node.links)
        
    return impactedLinks
    
def mirror(nodes, nodeM1, nodeM2): # nodes M1 and M2 define the mirror line
    print("Miror", nodeM1, nodeM2)
    
    posA = nodeM1.pos
    posB = nodeM2.pos
    
    AB = posB - posA
    ABm2 = 1.0 / (AB*AB)
    
    impactedLinks = set()
    for node in nodes:
        posN = node.pos
        AN = posN - posA
        k = (AB*AN) * ABm2 # 
        AC = k * AB
        posC = posA + AC
        NC   = posC - posN
        posM = posC + NC # Mirror of N
        node.setPos(posM)
        
        impactedLinks |= set(node.links)
        
    return impactedLinks
        
def Rotate(nodes, deg=90, rotCenterPos=None):
    a = deg * DEG2RAD
    print("Rotate %6.1f"%deg)
    
    if rotCenterPos == None :
        rotCenterPos = groupCenterPos(nodes)
    cp = rotCenterPos
    
    c, s = cos(a), sin(a)
    
    impactedLinks = set()
    for node in nodes:
        np = node.pos
        xrel, yrel = np.x-cp.x, np.y-cp.y
        x = c * xrel - s * yrel 
        y = s * xrel + c * yrel 
        node.setPos(Position(cp.x + x, cp.y + y))
        impactedLinks |= set(node.links)
        
    return impactedLinks
    
def morphing(nodes, k=0.5):    
    impactedLinks = set()
    for node in nodes:
        pos = node.interpolatedPos(k)
        if pos : 
            node.setPos(pos, updateLnk=False)
            impactedLinks |= set(node.links)
    return impactedLinks
            
#------------------------------------------------------------       
def circularXYs(n, r, centerXY):
    xC, yC = centerXY
    xys = []
    da = (2*pi) / n
    for i in range(n):
        xys.append((xC + r*cos(i*da), yC + r*sin(i*da)))
    return xys
                
#------------------------------------------------------------       
def randomLinks(n):
    print("randomLinks")
    links = set()
    scrambledNodesIds = list(range(n))
    random.shuffle(scrambledNodesIds)
    print("scrambledNodesIds:", scrambledNodesIds)
    for i in range(n):
        id0 = scrambledNodesIds[i]
        next_i = (i+1) % n
        id1 = scrambledNodesIds[next_i]
        links.add((id0, id1))
    for i in range(n):
        id0 = random.randint(0, n-1)
        id1 = random.randint(0, n-1)
        if id0 == id1 : continue
        links.add((id0, id1))
    return list(links)
    
#------------------------------------------------------------       
def widthHeightCenter(xys):
    print("LG.widthHeightCenter")
    xs, ys = zip(*xys) # unzip
    
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    
    width, height = xmax-xmin, ymax-ymin
    centerPos = Position(0.5*(xmin+xmax), 0.5*(ymin+ymax)) # center of drawing
    print("drawing Width Height:", width, height)
    print("drawing Center :", centerPos)

    return width, height, centerPos
            
#------------------------------------------------------------       
class Graph:
    def __init__(self, id=0, name='', **kwargs): # nodes=None, links=None
        if 0:
            print("LG.Graph kwargs :")
            for key in kwargs: print(key, ':', kwargs[key])
        self.id    = id
        self.name  = name
        self.nodes = []
        self.links = []
        self.nodesN = None
        self.drawingW, self.drawingH, self.centerPos = None, None, None
        '''
        if nodes : self.createNodes(initialPostions=nodes)
        if links : self.createLinks(linksNodes=links)
        '''
        if 'solutionPositions' in kwargs:
            solutionPositions = kwargs['solutionPositions']
            self.nodesN = len(solutionPositions)
            self.drawingW, self.drawingH, self.centerPos = widthHeightCenter(solutionPositions)
        else:
            solutionPositions = None
    
        if 'initialPostions' in kwargs:
            initialPostions = kwargs['initialPostions']
        else:
            if 'n' in kwargs:
                self.nodesN = kwargs['n']
                
            if 'centerPos' in kwargs:
                xC, yC = kwargs['centerPos']
            else:
                xC, yC = self.centerPos.x, self.centerPos.y
            
            if 'radius' in kwargs:
                radius = kwargs['radius']
            else:
                radius = 0.5 * min(self.drawingW, self.drawingH)
            
            initialPostions = circularXYs(self.nodesN, radius, centerXY=(xC, yC))
            
        if self.drawingW == None :    
            self.drawingW, self.drawingH, self.centerPos = widthHeightCenter(initialPostions)
               
        for i, (x, y) in enumerate(initialPostions):
            self.createAndAddNode(i, Position(x, y))
            
        if solutionPositions : self.loadSolutionXYs(solutionPositions)    
    
        if 'linksNodes' in kwargs:
            linksNodes = kwargs['linksNodes']
        else:
            linksNodes = randomLinks(self.nodesN)
            
        self.createLinks(linksNodes)
        
    def createLinks(self, linksNode0idNode1id):
        for i, (n0, n1) in enumerate(linksNode0idNode1id):
            #print("%3d :%3d <->%3d"%(i, n0, n1))
            node0 = self.nodes[n0]
            node1 = self.nodes[n1]
            link = self.createAndAddLink(i, node0, node1)
            node0.addLink(link)
            node1.addLink(link)        
        
    def __str__(self):
        s = "Graph %2d, '%s'"%(self.id , self.name)
        
        s += "\n%3d Nodes :"%len(self.nodes)
        for node in self.nodes: s += "\n    %s"%node
        
        s += "\n%3d Links:"%len(self.links)
        for link in self.links: s += "\n    %s"%link
        
        return s
    
    def createAndAddNode(self, i, xy):
        #print("LG.createAndAddNode")
        node = Node(self, i, xy)
        self.nodes.append(node)
        return node
        
    def createAndAddLink(self, i, node0, node1):
        #print("LG.createAndAddLink")
        link = Link(self, i, node0, node1)
        self.links.append(link)
        return link
        
    def loadSolutionXYs(self, xys):
        for node, (x, y) in zip(self.nodes, xys):
            node.posS = Position(x, y)
            
    def saveNodesPosInPosA(self):
        for node in self.nodes:
            node.posA = Position(node.pos.x, node.pos.y)
            
    def restoreNodesPosfromPosA(self):
        for node in self.nodes:
            node.pos = Position(node.posA.x, nodeA.pos.y)
            
    def NodesCopyPos(self, fromPos='posS', toPos='posA'):
        print("NodesCopyPos", fromPos, toPos)
        for node in self.nodes:
            setattr(node, toPos, getattr(node, fromPos))
            
#--------------------------------------- sample ----------------------------------------            
sailBoatNodesPos = ((-4.0, 0.0), (0.0, 0.0), (6.0, 0.0), (-2.0, -1.0), (5.0, -1.0), (0.0, 10.0), (-1.0, 1.0), (0.0, 1.0), (5.0, 1.0), (0.0, 8.0))      
sailBoatlinks    = ((0, 1), (1, 2), (3, 4), (0, 3), (2, 4), (0, 9), (5, 9), (9, 7), (7, 1), (7, 8), (8, 5), (0, 6), (6, 9), (6, 1))     

#=======================================================================================

if __name__ == "__main__":
    if 0:
        v = Vect2D(2,3)
        print("v :", v*3)
        
        p1 = Position(2,3)
        print("p1 :", p1*3)
        
        p2 = Position(2,3)
        print("p2 :", 3*p2)
        
        quit()
        
    g = Graph(initialPostions=sailBoatNodesPos, linksNodes=sailBoatlinks)
    print("Graph ", g)
    
    #g.createNodes()
    #g.createLinks()
    
    
    