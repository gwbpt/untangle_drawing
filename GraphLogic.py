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

#--------------------------------------------------
import random
from math import cos, sin, pi

DEG2RAD = pi/180

from numbers import Number

class Vect2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.strFormat = "Vec(%7.2f,%7.2f)" # "Vec(%9.4f,%9.4f)"

    def __add__(self, other):
        return self.__class__(self.x+other.x, self.y+other.y)
        
    def __sub__(self, other):
        return self.__class__(self.x-other.x, self.y-other.y)
        
    def __mul__(self, other):
        if isinstance(other, Number):
            #return Vect2D(self.x*other, self.y*other) # Position * float => vect2D !!!!
            return self.__class__(self.x*other, self.y*other) # create an instance of same class as self (inheritance)
        return self.x*other.x + self.y*other.y # scalar product
        
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def rotate(self, cosa, sina, xC=0.0, yC=0.0):
        xrel, yrel = self.x-xC, self.y-yC
        self.x = cosa * xrel - sina * yrel + xC
        self.y = sina * xrel + cosa * yrel + yC
        
    def copy(self):
        return self.__class__(self.x, self.y)
        
    def __str__(self):
        return self.strFormat%(self.x, self.y)
        
#---------------------------------
class Position(Vect2D):
    def __init__(self, x, y):
        Vect2D.__init__(self, x,y)
        self.strFormat = "Pos(%9.4f,%9.4f)"
    '''    
    def __str__(self):
        return "Pos(%7.2f,%7.2f)"%(self.x, self.y)
    '''    
#--------------------------------------------------
INIT_POS_IDX, SOL_POS_IDX, STORE_POS_IDX = 0, 1, 2
  
class Node:
    def __init__(self, graph, id, pos, name=None):
        self.graph = graph
        self.id    = id
        if   name == 'alpha': self.name = chr(ord('A')+id)
        elif name == 'num'  : self.name = str(id)
        elif name == None   : self.name = str(id)
        else                : self.name = name
        #print(self.name)
        self.pos  = pos  # current clickRangePli
        self.posList = [pos.copy()] # or[Position(pos.x, pos.y)]  # copy pos
        self.posList.append(None) # 1 = solution pos if any
        self.posList.append(None) # 2 = to store current pos
        self.links = []
        
    def __str__(self):
        posListStr = ""
        for p in self.posList:
            posListStr += "%s, "%p
        return "%3d :%s; %s; '%s'"%(self.id, self.pos, posListStr, self.name)
    
    def getPos(self):
        return self.pos
        
    def updatePos(self, updateLnk=False):
        if updateLnk:
            self.updateLinks()
    
    def setPos(self, pos, updateLnk=False):
        self.pos = pos
        self.updatePos(updateLnk=updateLnk)
        
    def setSelect(self, selected=True):
        self.selected = selected
    
    def addLink(self, lnk):
        self.links.append(lnk)

    def updateLinks(self):
        for lnk in self.links : 
            lnk.updateNodes()
            
    def calculateStepToTarget(self, targetIdx=SOL_POS_IDX, nbSteps=10):
        dk = 1.0/nbSteps
        self.targetPos = self.posList[targetIdx]
        dx, dy = (self.targetPos.x - self.pos.x) * dk , (self.targetPos.y - self.pos.y) * dk
        self.stepToTarget = Vect2D(dx, dy)
    
    def executeStepToTarget(self, updateLnk=True, last=False):
        if last : self.setPos(self.targetPos)
        else    : self.setPos(self.getPos() + self.stepToTarget, updateLnk=updateLnk)
        
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
            
def updateLinks(links): 
    for lnk in links: lnk.updateNodes()
           
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
    #print("Miror", nodeM1, nodeM2)
    
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

#------------------------------------------------------------       
def calculateStepToTargetNodes(nodes, targetIdx=SOL_POS_IDX, nbSteps=10):    
    #print("calculateStepsToTarget targetIdx :", targetIdx)
    impactedLinks = set()
    for node in nodes:
        node.calculateStepToTarget(targetIdx=targetIdx, nbSteps=nbSteps)
        impactedLinks |= set(node.links)
    return impactedLinks
    
def executeStepToTargetForNodes(nodes, last=False):
    for node in nodes:
        node.executeStepToTarget(updateLnk=False, last=last)
    
#------------------------------------------------------------       
def circularXYs(n, rx, ry, centerXY):
    xC, yC = centerXY
    xys = []
    da = (2*pi) / n
    for i in range(n):
        xys.append((xC + rx*cos(i*da), yC + ry*sin(i*da)))
    return xys
                
#------------------------------------------------------------       
def randomLinks(n):
    print("randomLinks :", n)
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
def nWidthHeightCenter(xys):
    #print("LG.nWidthHeightCenter")
    n = len(xys)

    xs, ys = zip(*xys) # unzip
    
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    
    width, height = xmax-xmin, ymax-ymin
    centerPos = Position(0.5*(xmin+xmax), 0.5*(ymin+ymax)) # center of drawing

    return n, width, height, centerPos
            
#------------------------------------------------------------
       
def saveNodesPosTo(nodes, toIdx=STORE_POS_IDX):
    print("saveNodesPosTo", toIdx)
    for node in nodes:
        node.posList[toIdx] = Position(node.pos.x, node.pos.y)
        
def restoreNodesPosFrom(nodes, fromIdx=STORE_POS_IDX):
    print("restoreNodesPosFrom", toIdx)
    for node in self.nodes:
        node.pos = Position(node.posList[fromIdx].x, nodeA.posList[idx].y)
                 
#---------------------------------------------------------------
class SoftRotation:     
    def __init__(self, nodes, deg=90, rotCenterPos=None, nbSteps=10):   
        self.nodes = nodes
        
        if rotCenterPos == None :
            rotCenterPos = groupCenterPos(self.nodes)

        self.xC, self.yC = rotCenterPos.x, rotCenterPos.y
        
        a = deg * DEG2RAD
        self.cosa, self.sina = cos(a), sin(a)
        
        self.impactedLinks = set()
        self.lastNodesPos = list()
        for node in self.nodes:
            self.impactedLinks |= set(node.links)
            pos = Position(node.pos.x, node.pos.y)
            pos.rotate(self.cosa, self.sina, xC=self.xC, yC=self.yC)
            self.lastNodesPos.append(pos)
        
        da = a / nbSteps
        self.cosda, self.sinda = cos(da), sin(da)
        
        self.stepCnt = 0
        self.nbSteps = nbSteps # to start
            
    def rotate_da(self):
        self.stepCnt += 1
        last = self.stepCnt >= self.nbSteps
        if last :
            print("last")
            for node, pos in zip(self.nodes,self.lastNodesPos):
                node.setPos(pos)
            self.nbSteps = 0 
        else:
            for node in self.nodes:
                node.pos.rotate(self.cosda, self.sinda, xC=self.xC, yC=self.yC)
                node.updatePos() 
        updateLinks(self.impactedLinks)
        return last # to stop
        
#------------------------------------------------------------       
class Graph:
    def __init__(self, id=0, name='', nodeClass=Node, linkClass=Link, **kwargs): # nodes=None, links=None
        if 0:
            print("LG.Graph kwargs :")
            for key in kwargs: print(key, ':', kwargs[key])
            print("---------------------")
        self.id    = id
        self.name  = name
        self.nodeClass = nodeClass
        self.nodes = []
        self.linkClass = linkClass
        self.links = []
        self.nodesN, self.drawingW, self.drawingH, self.centerPos = None, None, None, None
        
        solutionPositions = kwargs.get('solutionPositions', None)
        initialPostions   = kwargs.get('initialPostions'  , None)
        linksNodes        = kwargs.get('linksNodes'       , None)
        
        if 0:
            print("solutionPositions :", solutionPositions)
            print("initialPostions   :", initialPostions)
            print("linksNodes        :", linksNodes)
        
        if solutionPositions :
            self.nodesN, self.drawingW, self.drawingH, self.centerPos = nWidthHeightCenter(solutionPositions)
    
        if initialPostions:
            initialPosAuto = False
            if self.nodesN == None :
                self.nodesN, self.drawingW, self.drawingH, self.centerPos = nWidthHeightCenter(initialPostions)
            else:
                if len(initialPostionsN) != self.nodesN :
                    print("initialPostions nb != solutionPositions nb => skip initialPostions")
        else:
            initialPosAuto = True
            if self.nodesN == None : 
                self.nodesN = kwargs.get('n', 7)
                self.centerPos = kwargs.get('centerPos', Position(0, 0))
                self.drawingW, self.drawingH = 2.0, 2.0
            
        if linksNodes == None :
            linksNodes = randomLinks(self.nodesN)
        self.linksN = len(linksNodes)
        
        self.displayDivSize = self.geomSetting(self.drawingW, self.drawingH)
        
        if initialPosAuto:
            w, h = self.displayDivSize
            rx, ry = 0.5*w, 0.5*h
            xC, yC = self.centerPos.x, self.centerPos.y
            xys = circularXYs(self.nodesN, rx, ry, centerXY=(xC, yC))
            random.shuffle(xys)
            initialPostions = xys
            
        self.createNodes(initialPostions, solutionPositions)
        self.createLinks(linksNodes)
        
    def geomSetting(self, drawingW, drawingH): # to override according GUI
        print("Number of nodes :", self.nodesN)
        print("Number of links :", self.linksN)
        print("Drawing Width Height:", self.drawingW, self.drawingH)
        print("Drawing Center :", self.centerPos)
        displayDivSize = 2.0, 2.0
        return displayDivSize
        
    def createNodes(self, initialPostions, solutionPositions=None):
        for i, (x, y) in enumerate(initialPostions):
            self.createAndAddNode(i, Position(x, y))
        if solutionPositions : self.load_xys_in_idx(xys=solutionPositions, idx=SOL_POS_IDX)    
    
    def createLinks(self, linksNode0idNode1id):
        for i, (n0, n1) in enumerate(linksNode0idNode1id):
            #print("%3d :%3d <->%3d"%(i, n0, n1))
            node0 = self.nodes[n0]
            node1 = self.nodes[n1]
            link = self.createAndAddLink(i, node0, node1)
            node0.addLink(link)
            node1.addLink(link)        
        
    def __str__(self):
        s = "Graph id:%2d, name:'%s'"%(self.id , self.name)
        
        s += "\n%3d Nodes :"%self.nodesN
        for node in self.nodes: s += "\n    %s"%node
        
        s += "\n%3d Links:"%self.linksN
        for link in self.links: s += "\n    %s"%link
        
        return s
    
    def createAndAddNode(self, i, xy):
        #print("LG.createAndAddNode")
        node = self.nodeClass(self, i, xy)
        self.nodes.append(node)
        return node
        
    def createAndAddLink(self, i, node0, node1, name=None):
        #print("LG.createAndAddLink")
        link = self.linkClass(self, i, node0, node1, name=name)
        self.links.append(link)
        return link
        
    def load_xys_in_idx(self, xys, idx):
        for node, (x, y) in zip(self.nodes, xys):
            node.posList[idx] = Position(x, y)
            
#------------------------------ samples ----------------------------------
           
sailBoatNodesPos = (
    (-4.0, 0.0), ( 0.0, 0.0), (6.0, 0.0), (-2.0,-1.0), (5.0,-1.0),
    (0.0, 10.0), (-1.0, 1.0), (0.0, 1.0), ( 5.0, 1.0), (0.0, 8.0),
    )      
sailBoatlinks = (
    (0, 1), (1, 2), (3, 4), (0, 3), (2, 4), (0, 9), (5, 9),
    (9, 7), (7, 1), (7, 8), (8, 5), (0, 6), (6, 9), (6, 1),
    )     

busNodesPos = ( 
    (-12, 7),( -9, 7),( -6, 7),( -3, 7),(  0, 7),(  3, 7),(  6, 7),(  9, 7), 
    ( 11, 7),( 12, 4),( 12, 1),(  9, 1),(  8, 0),(  7, 0),(  6, 1),( -6, 1),
    ( -7, 0),( -8, 0),( -9, 1),(-12, 1),(-12, 4),(  9, 2),(  8, 3),(  7, 3), 
    (  6, 2),( -6, 2),( -7, 3),( -8, 3),( -9, 2),(  9, 4),(  6, 4),(  3, 4),
    (  0, 4),( -3, 4),( -6, 4),( -9, 4),
    )      
buslinks = (
    ( 0,  1),( 1,  2),( 2,  3),( 3,  4),( 4,  5),( 5,  6),( 6,  7),( 7,  8),
    ( 8,  9),( 9, 10),(10, 11),(11, 12),(12, 13),(13, 14),(14, 15),(15, 16),
    (16, 17),(17, 18),(18, 19),(19, 20),(20,  0),(11, 21),(21, 22),(22, 23), 
    (23, 24),(24, 14),(15, 25),(25, 26),(26, 27),(27, 28),(28, 18),( 9, 29),
    (29, 30),(30, 31),(31, 32),(32, 33),(33, 34),(34, 35),(35, 20),( 7, 29),
    ( 6, 30),( 5, 31),( 4, 32),( 3, 33),( 2, 34),( 1, 35),
    )     
#===============================================================================

if __name__ == "__main__":
    if 0:
        v = Vect2D(2,3)
        print("v :", v*3)
        
        p1 = Position(2,3)
        print("p1 :", p1*3)
        
        p2 = Position(2,3)
        print("p2 :", 3*p2)
        
        quit()
    if 0:    
        node = Node(graph=None, id=0, pos=Position(0,0)) 
        node.posList[SOL_POS_IDX] = Position(2, 1) # solution
        
        n = 10
        node.calculateStepToTarget(targetIdx=SOL_POS_IDX, nbSteps=n)
        print(node)
        for i in range(n):
            node.executeStepToTarget()
            print(node)
            
        quit()
        
    if 0:    
        node = Node(graph=None, id=0, pos=Position(1,0))
        nodes = [node]
        n = 10
        softRot = SoftRotation(nodes, deg=180, rotCenterPos=Position(0,0), nbSteps=n)
        for i in range(n):
            softRot.rotate_da()
            print("%3d : %s"%(i, node))
        quit()
        
    from datas import samples
    drawing = samples[0]    
    g = Graph(initialPostions=drawing['solxys'], linksNodes=drawing['links'])
    print("Graph ", g)
        
