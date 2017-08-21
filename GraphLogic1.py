#!/usr/bin/env python

from __future__ import print_function, division

import random
from math import cos, sin, pi

class Node:
    def __init__(self, id, xy, name=None):
        self.id   = id
        if name: self.name = name
        else   : self.name = chr(ord('A')+id)
        print(self.name)
        self.xy   = xy
        self.links = []
        
    def __str__(self):
        x, y = self.xy
        return "%3d :%6.2f, %6.2f; '%s'"%(self.id, x, y, self.name)
    
    def getPos(self):
        return self.x, self.y
        
    def setPos(self, x, y):
        self.x, self.y = x, y
        
    def setSelect(self, selected=True):
        self.selected = selected
    
    def addLink(self, lnk):
        self.links.append(lnk)

    def updateLinks(self):
        for lnk in self.links : 
            lnk.updateNodes()
                
    def interpolate(self, k=1.0):
        x = self.x + k*(self.solved_x-self.x)
        y = self.y + k*(self.solved_y-self.y)
        self.setPos(x, y)
        
        
class Link:
    def __init__(self, id, node0, node1, name=None):
        self.id   = id
        if name: self.name = name
        else   : self.name = "%s->%s"%(node0.name, node1.name)
        self.node0, self.node1 = node0, node1

    def __str__(self):
        return "%3d :%3d <->%3d; '%s'"%(self.id, self.node0.id, self.node1.id, self.name)
    
class Graph:
    def __init__(self, id=0, name='', nodes=None, links=None):
        self.id    = id
        self.name  = name
        self.nodes = []
        self.links = []
        if nodes : self.createNodes(nodesPostions=nodes)
        if links : self.createLinks(linksNodes=links)
    
    def __str__(self):
        s = "Graph %2d, '%s'"%(self.id , self.name)
        
        s += "\n%3d Nodes :"%len(self.nodes)
        for node in self.nodes: s += "\n    %s"%node
        
        s += "\n%3d Links:"%len(self.links)
        for link in self.links: s += "\n    %s"%link
        
        return s
    
    def addNode(self, node):
        self.nodes.append(node)
        
    def addLink(self, link):
        self.links.append(link)
        
    def createNodes(self, **kwargs): # args : nodesPostions or n , centerPos, radius   
        if 'nodesPostions' in kwargs:
            nodesPostions = kwargs['nodesPostions']
        else:
            if 'n' in kwargs:
                n = kwargs['n']
            else:
                n = 12
                
            if 'centerPos' in kwargs:
                xC, yC = kwargs['centerPos']
            else:
                xC, yC = 0.0, 0.0
            
            if 'radius' in kwargs:
                r = kwargs['radius']
            else:
                r = 1.0
            
            da = (2*pi) / n
            nodesPostions = []
            for i in range(n):
                nodesPostions.append((xC + r*cos(i*da), yC + r*sin(i*da)))
                
        for i, xy in enumerate(nodesPostions):
            self.addNode(Node(i, xy))
            
            
    def createLinks(self, linksNodes=None):
        if linksNodes == None:
            links = set()
            n = len(self.nodes)
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
            linksNodes = list(links)
            
        for i, (n0, n1) in enumerate(linksNodes):
            #print("%3d :%3d <->%3d"%(i, n0, n1))
            node0 = self.nodes[n0]
            node1 = self.nodes[n1]
            lnk = Link(i, node0, node1)
            self.links.append(lnk)
            node0.addLink(lnk)
            node1.addLink(lnk)

#--------------------------------------- sample ----------------------------------------            
sailBoatNodesPos = ((-4.0, 0.0), (0.0, 0.0), (6.0, 0.0), (-2.0, -1.0), (5.0, -1.0), (0.0, 10.0), (-1.0, 1.0), (0.0, 1.0), (5.0, 1.0), (0.0, 8.0))      
sailBoatlinks    = ((0, 1), (1, 2), (3, 4), (0, 3), (2, 4), (0, 9), (5, 9), (9, 7), (7, 1), (7, 8), (8, 5), (0, 6), (6, 9), (6, 1))     

#=======================================================================================

if __name__ == "__main__":

    g = Graph(nodes=sailBoatNodesPos, links=sailBoatlinks)
    print(g)
    
    #g.createNodes()
    #g.createLinks()
    
    
    