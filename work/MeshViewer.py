#!/usr/bin/env python3
# -*- coding: utf-8
# vim: set fileencoding=utf-8

# pyobjviewer is a simple viewer for obj format 3D meshes. It has no dependencies
# on external 3D libraries such as opengl. It uses vanilla pygame, and provides an
# example and insight into the inner workings of 3D display. lighting and meshes.

# See: http://jestermon.weebly.com/pyobjviewer.html

import sys
import random, math, pygame
from pygame.locals import * # KEYUP and such

#
# Main objects
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Point3D:
    """Provide an elementary 3D point with associated methods for
    creation and transformation"""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, a=0, b=0, c=0):
        self.x, self.y, self.z = a, b, c
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def norm(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        return "Point3D(%f, %f, %f)" % ( self.x, self.y, self.z)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __neg__(self):
        return Point3D(-self.x, -self.y, -self.z)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __add__(self,other):
        return  Point3D(self.x + other.x, self.y + other.y, self.z + other.z)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def scale(self, v):
        self.x *= v; self.y *= v; self.z *= v
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rotateX(self, angle):
        c, s = math.cos(angle), math.sin(angle)
        self.y, self.z = self.y * c - self.z * s, self.y * s + self.z * c
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rotateY(self, angle):
        c, s = math.cos(angle), math.sin(angle)
        self.x, self.z = self.x * c - self.z * s, self.x * s + self.z * c
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rotateZ(self, angle):
        c, s = math.cos(angle), math.sin(angle)
        self.x, self.y = self.x * c - self.y * s, self.x * s + self.y * c
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rotate(self, teta, phi):
        self.rotateY(phi)
        self.rotateZ(teta)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def projection(self, env3d):
        return [env3d.wincenter[0] + env3d.zoom_factor * self.x, env3d.wincenter[1] + env3d.zoom_factor * self.y]
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def normalize(self):
        self.scale(1. / self.norm())


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Face:
    """Common ancestor for Faces, most of the interesting stuff is done in
    children Triangle / Quad"""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def render(self, env3d, points):
        "Render the face, provided a getPolygon() and a lum_coeff() are available"
        polygon = self.getPolygon(points, env3d)
        #color = 255,255,255
        if env3d.colorize:
            # computes colors for both light
            lc1 = int(64*self.lum_coeff(points,env3d.light_vector_1))
            lc2 = int(64*self.lum_coeff(points,env3d.light_vector_2))
            color = lc1*2,lc1+lc2,lc2 # mix color
            pygame.draw.polygon(env3d.screen, color, polygon) # fill face internal
        else: #only display the edges
            pygame.draw.polygon(env3d.screen, (0,0,0), polygon) # fill face internal with black
            pygame.draw.polygon(env3d.screen, (255,255,255), polygon,1) # display face edges in white


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Triangle(Face):
    """A Face which is a triangle"""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def translate(self, t):
        self.a += t; self.b += t; self.c += t
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def dist(self, points):
        return (points[self.a].z + points[self.b].z + points[self.c].z) / 3 # mean distance
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def lum_coeff(self, points, light_vector):
        """return the luminosity coefficient for this triangle, given the light_vector
        This is a float between 0 and 2.
        The light_vector is supposed normalized
        """
        a, b, c = points[self.a], points[self.b], points[self.c]
        v1 = Point3D ( b.x-a.x, b.y-a.y, b.z-a.z)
        v2 = Point3D ( c.x-a.x, c.y-a.y, c.z-a.z)
        v = Point3D( v1.y*v2.z-v2.y*v1.z,v1.z*v2.x-v2.z*v1.x,v1.x*v2.y-v2.x*v1.y ) # vector product
        sp = (v.x*light_vector.x+v.y*light_vector.y+v.z*light_vector.z)/v.norm() # <v,light> / ||v||
        return sp + 1 
        return math.acos(normalised_scalar_product(vector_product,light_vector))/(math.pi)+1  # angle
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getPolygon(self, points, env3d):
        return [points[self.a].projection(env3d),
                points[self.b].projection(env3d),
                points[self.c].projection(env3d)]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Quad(Face):
    """A Face composed of four edges and four vertex, theoretically with
    all of this belonging to the same plane"""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, a, b, c, d):
        self.a, self.b, self.c, self.d = a, b, c, d
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def translate(self, t):
        self.a += t; self.b += t; self.c += t; self.d += t
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def dist(self, points):
        return (points[self.a].z+points[self.b].z+points[self.c].z)+points[self.d].z/4 # mean distance
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def lum_coeff(self, points, light_vector):
        """return the luminosity coefficient for this triangle, given the light_vector
        This is a float between 0 and 2.
        The light_vector is supposed normalized
        """
        a,b,c= points[self.a], points[self.b], points[self.c]
        v1 = Point3D ( b.x-a.x, b.y-a.y, b.z-a.z)
        v2 = Point3D ( c.x-a.x, c.y-a.y, c.z-a.z)
        v = Point3D( v1.y*v2.z-v2.y*v1.z,v1.z*v2.x-v2.z*v1.x,v1.x*v2.y-v2.x*v1.y ) # vector product
        sp = (v.x*light_vector.x+v.y*light_vector.y+v.z*light_vector.z)/v.norm() # <v,light> / ||v||
        return sp +1 
        return math.acos(normalised_scalar_product(vector_product,light_vector))/(math.pi)+1  # angle
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getPolygon(self, points, env3d):
        return [points[self.a].projection(env3d),
                points[self.b].projection(env3d),
                points[self.c].projection(env3d),
                points[self.d].projection(env3d)]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Object:
    """An object is a collection of points (object:Point) and faces
    (object:Faces). The faces are made of indices referencing the points
    array.
    An object can be read from a file, or created by code.

    Objects can be merged using the method __add__. Exemple
    merged_object = object1 + object2

    Once created, an object can be transformed and displayed.
    """
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self,filename=""):
        if filename=="":
            self.name="unknown"
            self.points,self.faces=[], []
        else:
            self.name="Read from "+filename
            self.readFile(filename)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self): return "Object %s : %d points, %d faces" % (self.name,len(self.points),len(self.faces))
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def scale(self,v):
        for p3d in self.points: p3d.scale(v)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def translate(self,v):
        for i in range(len(self.points)): self.points[i]+=v
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rotateX(self,angle):
        for p3d in self.points: p3d.rotateX(angle)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rotateY(self,angle):
        for p3d in self.points: p3d.rotateY(angle)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rotateZ(self,angle):
        for p3d in self.points: p3d.rotateZ(angle)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rotate(self,teta,phi):
        for p3d in self.points: p3d.rotate(teta,phi)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getMinMaxDiam(self):
        VERYMUCH = 1E30
        m,M = Point3D(VERYMUCH,VERYMUCH,VERYMUCH), Point3D(-VERYMUCH,-VERYMUCH,-VERYMUCH)
        for p3d in self.points:
            if (p3d.x<m.x):m.x = p3d.x
            if (p3d.y<m.y):m.y = p3d.y
            if (p3d.z<m.z):m.z = p3d.z
            if (p3d.x>M.x):M.x = p3d.x
            if (p3d.y>M.y):M.y = p3d.y
            if (p3d.z>M.z):M.z = p3d.z
        diam = M.x-m.x
        diam+= M.y-m.y
        diam+= M.z-m.z
        diam /= 3
        return m,M,diam
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getCenter(self):
        m,M,d = self.getMinMaxDiam()
        m+=M
        m.scale(.5)
        return m
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def canonicalView(self):
        m,M,d = self.getMinMaxDiam()
        m+=M
        m.scale(.5) # m is the center
        self.translate(-m)
        self.scale(3000/d)
        return m
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def center(self):
        self.translate(-self.getCenter())
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __add__(self,other):
        "Concatenate this object and 'other', returns it "
        ret = Object()
        ret.points = self.points + other.points
        l=len(self.points)
        # translate faces
        ret.faces = other.faces
        for f in ret.faces:
            f.translate(l)
        # remaining faces
        ret.faces += self.faces
        return ret
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def sort_faces(self):
        "Sort faces according to their distance from the camera, that is the z coordinate from points3d"
        self.faces.sort(key= lambda t : t.dist(self.points)) # compare the distance
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def display(self, env3d):
        "compute the projections and display the whole object"
        #env3d.screen.fill((10,10,20))
        self.sort_faces()
        self.render_faces(env3d)
        #pygame.display.update()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def render_faces(self, env3d):
        "Renders all triangles on the screen"
        for fn in range(len(self.faces)):
            self.faces[fn].render(env3d,self.points)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def random_place(self):
        self.scale(random.random()+0.3)
        p = Point3D(random.random()*2-1, random.random()*2-1, random.random()*2-1)
        self.translate(p)
        self.rotate(random.random()*math.pi, random.random()*2*math.pi)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def readFile(self,filename):
        self.points,self.faces=[], []
        print("Creating object from", filename)
        f=open(filename, 'r')
        # read vertices
        line = ""
        while line != "Vertices":
            line = f.readline().strip()
        nbPoint = int(f.readline().strip())
        for i in range(nbPoint):
            line = f.readline().split()
            self.points.append(Point3D( float(line[0]), float(line[1]), float(line[2])) )
        line = ""
        while line == "":
            line = f.readline().strip()
        # read faces
        if line=="Triangles":
            nbTriangles = int(f.readline().strip())
            for i in range(nbTriangles):
                line = f.readline().split()
                self.faces.append( Triangle( int(line[0])-1, int(line[1])-1, int(line[2])-1) )
        elif line=="Quadrilaterals":
            nbQuad = int(f.readline().strip())
            for i in range(nbQuad):
                line = f.readline().split()
                self.faces.append(Quad (int(line[0])-1, int(line[1])-1, int(line[2])-1, int(line[3])-1) )
        print("readFile done : ", self)
        self.rotate(math.pi/3,math.pi/4)
        self.canonicalView()


#
# Object building
#

def GetDodecahedron():
    """Created a dodecahedron, see http://en.wikipedia.org/wiki/Dodecahedron"""
    o = Object()
    o.name = "Dodecahedron"
    # golden ration (1+sqrt(5))/2
    gr = 1.61803398874989484820
    # inverse golden ratio
    igr = 1/gr
    o.points.append( Point3D( 1, 1, 1) ) #0
    o.points.append( Point3D( 1, 1,-1) )
    o.points.append( Point3D( 1,-1, 1) )
    o.points.append( Point3D( 1,-1,-1) )
    o.points.append( Point3D(-1, 1, 1) )
    o.points.append( Point3D(-1, 1,-1) )
    o.points.append( Point3D(-1,-1, 1) )
    o.points.append( Point3D(-1,-1,-1) ) #7
 
    o.points.append( Point3D(0, gr, igr)) #8
    o.points.append( Point3D(0, gr,-igr))
    o.points.append( Point3D(0,-gr, igr))
    o.points.append( Point3D(0,-gr,-igr)) #11

    o.points.append( Point3D( gr, igr, 0)) #12
    o.points.append( Point3D( gr,-igr, 0))
    o.points.append( Point3D(-gr, igr, 0))
    o.points.append( Point3D(-gr,-igr, 0)) #15

    o.points.append( Point3D( igr, 0, gr)) #16
    o.points.append( Point3D( igr, 0,-gr))
    o.points.append( Point3D(-igr, 0, gr))
    o.points.append( Point3D(-igr, 0,-gr)) #19

    constructDodecahedronFace(o, 0,8,4,18,16)
    constructDodecahedronFace(o, 0,16,2,13,12)
    constructDodecahedronFace(o, 0,12,1,9,8)
    constructDodecahedronFace(o, 12,13,3,17,1)
    constructDodecahedronFace(o, 1,17,19,5,9)
    constructDodecahedronFace(o, 8,9,5,14,4)
    constructDodecahedronFace(o, 4,14,15,6,18)
    constructDodecahedronFace(o, 16,18,6,10,2)
    constructDodecahedronFace(o, 2,10,11,3,13)
    constructDodecahedronFace(o, 3,11,7,19,17)
    constructDodecahedronFace(o, 19,7,15,14,5)
    constructDodecahedronFace(o, 7,11,10,6,15)
    o.canonicalView()
    return o

def constructDodecahedronFace(o,a,b,c,d,e):
    """Construct a Dodecahedron face using triangles, given the object and 6
    points references IN THE RIGHT ORDER"""
    mp = o.points[a]+ o.points[b]+ o.points[c]+ o.points[d]+ o.points[e] # middle mpoint
    mp.scale(1./5.)
    o.points.append(mp)
    myidx = len(o.points)-1
    o.faces.append( Triangle(a,b,myidx) )
    o.faces.append( Triangle(b,c,myidx) )
    o.faces.append( Triangle(c,d,myidx) )
    o.faces.append( Triangle(d,e,myidx) )
    o.faces.append( Triangle(e,a,myidx) )

def GetIcosahedron():
    """Construct an icosahedron, see http://en.wikipedia.org/wiki/Icosahedron"""
    o = Object()
    o.name = "Icosahedron"
    # golden ration (1+sqrt(5))/2
    gr = 1.61803398874989484820
    o.points.append( Point3D( 0, 1, gr) ) #0
    o.points.append( Point3D( 0, 1,-gr) )
    o.points.append( Point3D( 0,-1, gr) )
    o.points.append( Point3D( 0,-1,-gr) )

    o.points.append( Point3D( 1, gr, 0) ) #4
    o.points.append( Point3D( 1,-gr, 0) )
    o.points.append( Point3D(-1, gr, 0) )
    o.points.append( Point3D(-1,-gr, 0) )

    o.points.append( Point3D( gr, 0, 1) ) #8
    o.points.append( Point3D(-gr, 0, 1) )
    o.points.append( Point3D( gr, 0,-1) )
    o.points.append( Point3D(-gr, 0,-1) )

    o.faces.append( Triangle(0,2,8) )
    o.faces.append( Triangle(0,8,4) )
    o.faces.append( Triangle(0,4,6) )
    o.faces.append( Triangle(0,6,9) )
    o.faces.append( Triangle(0,9,2) )

    o.faces.append( Triangle(3,5,7) )
    o.faces.append( Triangle(3,7,11) )
    o.faces.append( Triangle(3,11,1) )
    o.faces.append( Triangle(3,1,10) )
    o.faces.append( Triangle(3,10,5) )

    o.faces.append( Triangle(7,5,2) )
    o.faces.append( Triangle(5,10,8) )
    o.faces.append( Triangle(10,1,4) )
    o.faces.append( Triangle(1,11,6) )
    o.faces.append( Triangle(11,7,9) )

    o.faces.append( Triangle(5,8,2) )
    o.faces.append( Triangle(10,4,8) )
    o.faces.append( Triangle(1,6,4) )
    o.faces.append( Triangle(11,9,6) )
    o.faces.append( Triangle(7,2,9) )

    o.canonicalView()
    return o


def GetTetrahedron():
    """Construct a tetrahedron"""
    o = Object()
    o.name = "Tetrahedron"

    o.points.append( Point3D( 1, 1, 1) )
    o.points.append( Point3D(-1,-1, 1) )
    o.points.append( Point3D(-1, 1,-1) )
    o.points.append( Point3D( 1,-1,-1) )

    o.faces.append( Triangle(0,2,1) )
    o.faces.append( Triangle(0,3,2) )
    o.faces.append( Triangle(0,1,3) )
    o.faces.append( Triangle(1,2,3) )
    o.canonicalView()
    return o

def GetCube():
    """Construct a cube centered on (0,0,0) with edges of size 2.
    This cube is only made of triangles.
    """
    o = Object()
    o.name = "Cube"
    o.points.append( Point3D(-1,-1,-1) )
    o.points.append( Point3D(-1,-1, 1) )
    o.points.append( Point3D(-1, 1,-1) )
    o.points.append( Point3D(-1, 1, 1) )
    o.points.append( Point3D( 1,-1,-1) )
    o.points.append( Point3D( 1,-1, 1) )
    o.points.append( Point3D( 1, 1,-1) )
    o.points.append( Point3D( 1, 1, 1) )
    o.faces.append( Triangle(0,1,2) )
    o.faces.append( Triangle(3,2,1) )
    o.faces.append( Triangle(7,2,3) )
    o.faces.append( Triangle(7,6,2) )
    o.faces.append( Triangle(5,4,7) )
    o.faces.append( Triangle(7,4,6) )
    o.faces.append( Triangle(5,1,4) )
    o.faces.append( Triangle(1,0,4) )
    o.faces.append( Triangle(1,5,3) )
    o.faces.append( Triangle(7,3,5) )
    o.faces.append( Triangle(6,2,4) )
    o.faces.append( Triangle(0,2,4) )
    o.canonicalView()
    return o

def GetCubeQuad():
    """Construct a cube centered on (0,0,0) with edges of size 2.
    This cube is made using 6 square faces, hence only using the "Quad"
    type of face, no triangles."""
    o = Object()
    o.name = "Cube"
    o.points.append( Point3D(-1,-1,-1) )
    o.points.append( Point3D(-1,-1, 1) )
    o.points.append( Point3D(-1, 1,-1) )
    o.points.append( Point3D(-1, 1, 1) )
    o.points.append( Point3D( 1,-1,-1) )
    o.points.append( Point3D( 1,-1, 1) )
    o.points.append( Point3D( 1, 1,-1) )
    o.points.append( Point3D( 1, 1, 1) )
    o.faces.append( Quad(0,1,3,2) )
    o.faces.append( Quad(4,6,1,0) )
    o.faces.append( Quad(7,5,2,3) )
    o.faces.append( Quad(6,7,3,1) )
    o.faces.append( Quad(6,4,5,7) )
    o.faces.append( Quad(5,4,0,2) )
    o.canonicalView()
    return o


def GetGeode(power=1):
    """return a Geode made starting from a Icosahedron, where each edge has
    been splitted 2^power times. The created points have been placed on the
    sphere."""
    o = GetIcosahedron()
    for i in range(power):
        o = Geodise(o)
    o.name = "Geode(splits : 2^%d=%d)" % (power,2**power)
    return o

def Geodise(o):
    newo = Object()
    newo.points = o.points
    newpoints = {}

    def testCreatePoint(p,q):
        """ return the index of the new point between points p & q, creates
        it if it doesn't exist already and cache it in dict newpoints"""
        # should be this, but the one used is enough :-) if newpoints.has_key((p,q)) or newpoints.has_key((q,p)):
        if newpoints.has_key((q,p)):
            return newpoints[(q,p)]
        r = newo.points[p] + newo.points[q]
        r.scale(newo.points[p].norm()/r.norm())
        newo.points.append(r)
        index = len(newo.points)-1
        newpoints[(p,q)] = index
        return index

    for t in o.faces:
        a = t.a
        b = t.b
        c = t.c
        x = testCreatePoint(a,b)
        y = testCreatePoint(b,c)
        z = testCreatePoint(c,a)
        newo.faces.append( Triangle(a,x,z) )
        newo.faces.append( Triangle(x,b,y) )
        newo.faces.append( Triangle(x,y,z) )
        newo.faces.append( Triangle(z,y,c) )

    return newo


def sphere_point(i,j,N,M):
    teta=math.pi*i/N
    phi=2*math.pi*j/M
    c=math.cos(math.pi/2-teta)
    return Point3D( math.cos(phi)*c, math.sin(phi)*c, math.sin(math.pi/2-teta))

def GetSphere(N=10, M=10):
    """Create a sphere by creating triangles along longitude/latidue.
    The first arguement N is the number of (non-trivial = different from
    poles) latitudes, and the second argument M is the number of
    longitudes.
    """
    o = Object()
    o.points= [ Point3D(0,0,1) ]
    # north pole
    o.points.append(sphere_point(1,0,N,M))
    for j in range(1,M):
        o.points.append(sphere_point(1,j,N,M))
        o.faces.append(Triangle(0,j+1,j) )
    o.faces.append(Triangle(0,1,M) )
    # middle
    for i in range(2,N):
        o.points.append(sphere_point(i,0,N,M))
        for j in range(1,M):
            o.points.append(sphere_point(i,j,N,M))
            l = len(o.points)
            o.faces.append(Triangle(l-2-M,l-1-M,l-1) )
            o.faces.append(Triangle(l-2-M,l-1,l-2) )
        l = len(o.points)
        o.faces.append(Triangle(l-1-M,l-M-M,l-M) )
        o.faces.append(Triangle(l-1-M,l-M,l-1) )
    # south pole
    o.points.append(Point3D(0,0,-1) )
    southpole = len(o.points)-1
    o.points.append(sphere_point(N-1,0,N,M))
    for j in range(1,M):
        o.points.append(sphere_point(N-1,j,N,M))
        o.faces.append(Triangle(southpole,southpole+j,southpole+1+j) )
    o.faces.append(Triangle(southpole,southpole+M,southpole+1) )
    o.canonicalView()
    return o

def torus_point(i,j,N,M,r,R):
    teta,phi=2*math.pi*i/N, 2*math.pi*j/M
    ct,st = math.cos(teta), math.sin(teta)
    myr = R+r*math.cos(phi)
    return Point3D( myr*ct, myr*st, r*math.sin(phi) )

def GetTorus(N=20, M=20,r=.3,R=.6):
    """Create a Torus, see http://en.wikipedia.org/wiki/Torus"""
    # first circle
    o = Object()
    o.name = "torus"
    for j in range(0,M):
        o.points.append(torus_point(0,j,N,M,r,R))
    c = M-1 # index of last point
    # main loop
    for i in range(1,N):
        o.points.append(torus_point(i,0,N,M,r,R))
        c+=1
        for j in range(1,M):
            o.points.append(torus_point(i,j,N,M,r,R))
            c+=1
            o.faces.append(Triangle(c,c-1,c-M) )
            o.faces.append(Triangle(c-M-1,c-M,c-1) )
    # last circle
    for j in range(1,M):
        o.faces.append(Triangle(c,c-1,c-M) )
        o.faces.append(Triangle(c-M-1,c-M,c-1) )
    o.canonicalView()
    return o

class Env3D:
    def __init__(self, winsize=[800,600]):
        self.winsize=winsize
        self.zoom_factor = 1
        self.light_vector_1 = Point3D (random.random(),random.random(),random.random())
        self.light_vector_1.normalize()
        self.light_vector_2 = Point3D (random.random(),random.random(),random.random())
        self.light_vector_2.normalize()
        self.screen = pygame.display.set_mode(winsize)
        self.wincenter = [winsize[0]/2, winsize[1]/2]
        self.colorize = True
