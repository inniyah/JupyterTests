#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    This script is designed to export a mass amount of MagicaVoxel .vox files
    to .obj. Unlike Magica's internal exporter, this exporter preserves the
    voxel vertices for easy manipulating in a 3d modeling program like Blender.

    Various meshing algorithms are included (or to be included). MagicaVoxel
    uses monotone triangulation (I think). The algorithms that will (or do)
    appear in this script will use methods to potentially reduce rendering
    artifacts that could be introduced by triangulation of this nature.

    I may also include some features like light map generation for easy
    importing into Unreal Engine, etc.

    Notes:
        * There may be a few floating point equality comparisons. They seem to
            work but it scares me a little.
        * TODO: use constants instead of magic numbers (as defined in AAQuad),
                (i.e., ..., 2 -> AAQuad.TOP, ...)
        * A lot of assertions should probably be exceptions since they are
            error checking user input (this sounds really bad now that I've put
            it on paper...). So don't run in optimized mode (who does that
            anyways?).
        * I am considering adding FBX support.
"""

# https://gist.github.com/awesomez/cf9e29392a3fb910970b66a6d639a337
# https://gist.github.com/shivshank/34ffc56283273e1e904e8dc50491a7a6

import math

class AAQuad:
    """ A solid colored axis aligned quad. """
    normals = [
        (-1, 0, 0), # left = 0
        (1, 0, 0),  # right = 1
        (0, 0, 1),  # top = 2
        (0, 0, -1), # bottom = 3
        (0, -1, 0), # front = 4
        (0, 1, 0)   # back = 5
    ]
    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3
    FRONT = 4
    BACK = 5
    def __init__(self, verts, uv=None, normal=None):
        assert len(verts) == 4, "face must be a quad"
        self.vertices = verts
        self.uv = uv
        self.normal = normal
    def __str__(self):
        s = []
        for i in self.vertices:
            s.append( str(i) + '/' + str(self.uv) + '/' + str(self.normal))
        return 'f ' + ' '.join(s)
    def center(self):
        return (
            sum(i[0] for i in self.vertices)/4,
            sum(i[1] for i in self.vertices)/4,
            sum(i[2] for i in self.vertices)/4
        )

def bucketHash(faces, origin, maximum, bucket=16):
    extents = (
        math.ceil((maximum[0] - origin[0])/bucket),
        math.ceil((maximum[1] - origin[1])/bucket),
        math.ceil((maximum[2] - origin[2])/bucket)
    )
    buckets = {}
    for f in faces:
        c = f.center()
        # TODO

def optimizedGreedyMesh(faces):
    # TODO
    edges = adjacencyGraphEdges(faces)
    groups = contiguousFaces(faces, edges)
    return faces

def adjacencyGraphEdges(faces):
    """ Get the list of edges representing adjacent faces. """
    # a list of edges, where edges are tuple(face_a, face_b)
    edges = []
    # build the list of edges in the graph
    for root in faces:
        for face in faces:
            if face is root:
                continue
            if facesAreAdjacent(root, face):
                # the other edge will happen somewhere else in the iteration
                # (i.e., the relation isAdjacent is symmetric)
                edges.append((root, face))
    return edges

def contiguousFaces(faces, adjacencyGraphEdges):
    """ Get the list of connected components from a list of graph edges.
        The list will contain lists containing the edges within the components.
    """
    groups = []
    visited = dict((f, False) for f in faces)
    for face in faces:
        # if the face hasn't been visited, it is not in any found components
        if not visited[face]:
            g = []
            _visitGraphNodes(face, adjacencyGraphEdges, visited, g)
            # there is only a new component if face has not been visited yet
            groups.append(g)
    return groups

def _visitGraphNodes(node, edges, visited, component):
    """ Recursive routine used in findGraphComponents """
    # visit every component connected to this one
    for edge in edges:
        # for all x in nodes, (node, x) and (x, node) should be in edges!
        # therefore we don't have to check for "edge[1] is node"
        if edge[0] is node and not visited[edge[1]]:
            assert edge[1] is not node, "(node, node) should not be in edges"
            # mark the other node as visited
            visited[edge[1]] = True
            component.append(edge[1])
            # visit all of that nodes connected nodes
            _visitGraphNodes(edge[1], edges, visited, component)

def facesAreAdjacent(a, b):
    """ Adjacent is defined as same normal, uv, and a shared edge.
        This isn't entirely intuitive (i.e., corner faces are not adjacent)
        but this definition fits the problem domain.
        Only works on AAQuads.
    """
    # note: None is == None, this shouldn't matter
    if a.uv != b.uv:
        return False
    if a.normal != b.normal:
        return False
    # to be adjacent, two faces must share an edge
    # use == and not identity in case edge split was used
    shared = 0
    for vert_a in a.vertices:
        for vert_b in b.vertices:
            if vert_a == vert_b:
                shared += 1
            # hooray we have found a shared edge (or a degenerate case...)
            if shared == 2:
                return True
    return False

class GeoFace:
    """ An arbitrary geometry face
        This should only be used for arbitrary models, not ones we can
        reasonably assume are axis aligned.
    """
    def __init__(self, verts, uvs=None, normals=None):
        self.vertices = verts
        assert len(verts) in (3, 4), "only quads and tris are supported"
        self.normals = normals
        self.uvs = uvs
    def toAAQuad(self, skipAssert=False):
        q = AAQuad(self.vertices)
        if self.normals is not None and len(self.normals) > 0:
            if not skipAssert:
                for i in self.normals:
                    assert self.normals[0] == i, \
                        "face must be axis aligned (orthogonal normals)"
            q.normal = self.normals[0]
        if self.uvs is not None and len(self.uvs) > 0:
            if not skipAssert:
                for i in self.uvs:
                    assert self.uvs[0] == i, \
                        "face must be axis aligned (orthogonal)"
            q.uv = self.uvs[0]
        return q

class VoxelStruct:
    """ Describes a voxel object
    """
    def __init__(self):
        # a dict is probably the best way to go about this
        # (as a trade off between performance and code complexity)
        # see _index for the indexing method
        self.voxels = {}
        self.colorIndices = set()
    def fromList(self, voxels):
        self.voxels = {}
        for voxel in voxels:
            self.setVoxel(voxel)
            self.colorIndices.add(voxel.colorIndex)
    def setVoxel(self, voxel):
        self.voxels[voxel.z*(256**2) + voxel.y * 256 + voxel.x] = voxel
    def getVoxel(self, x, y, z):
        return self.voxels.get(z*(256**2) + y * 256 + x, None)
    def _index(self, x, y, z):
        return z*(256**2) + y * 256 + x
    def getBounds(self):
        origin = (float("inf"), float("inf"), float("inf"))
        maximum = (float("-inf"), float("-inf"), float("-inf"))
        for key, voxel in self.voxels.items():
            origin = (
                min(origin[0], voxel.x),
                min(origin[1], voxel.y),
                min(origin[2], voxel.z)
            )
            maximum = (
                max(maximum[0], voxel.x),
                max(maximum[1], voxel.y),
                max(maximum[2], voxel.z)
            )
        return origin, maximum
    def zeroOrigin(self):
        """ Translate the model so that it's origin is at 0, 0, 0 """
        origin, maximum = self.getBounds()
        result = {}
        xOff, yOff, zOff = origin
        for key, voxel in self.voxels.iteritems():
            result[self._index(voxel.x-xOff, voxel.y-yOff, voxel.z-zOff)] = \
                Voxel(voxel.x-xOff, voxel.y-yOff, voxel.z-zOff,
                      voxel.colorIndex)
        self.voxels = result
        return (0, 0, 0), (maximum[0] - xOff,
                           maximum[1] - yOff,
                           maximum[2] - zOff)
    def toQuads(self):
        """ --> a list of AAQuads """
        faces = []
        for key, voxel in self.voxels.items():
            self._getObjFaces(voxel, faces)
        return faces
    def _getObjFaces(self, voxel, outFaces):
        if voxel.colorIndex == 0:
            # do nothing if this is an empty voxel
            # n.b., I do not know if this ever can happen.
            return []
        sides = self._objExposed(voxel)
        if sides[0]:
            f = self._getLeftSide(voxel)
            self._getObjFacesSupport(0, voxel.colorIndex, f, outFaces)
        if sides[1]:
            f = self._getRightSide(voxel)
            self._getObjFacesSupport(1, voxel.colorIndex, f, outFaces)
        if sides[2]:
            f = self._getTopSide(voxel)
            self._getObjFacesSupport(2, voxel.colorIndex, f, outFaces)
        if sides[3]:
            f = self._getBottomSide(voxel)
            self._getObjFacesSupport(3, voxel.colorIndex, f, outFaces)
        if sides[4]:
            f = self._getFrontSide(voxel)
            self._getObjFacesSupport(4, voxel.colorIndex, f, outFaces)
        if sides[5]:
            f = self._getBackSide(voxel)
            self._getObjFacesSupport(5, voxel.colorIndex, f, outFaces)
        return
        n = AAQuad.normals[i]
        # note: texcoords are based on MagicaVoxel's texturing scheme!
        #   meaning a color index of 0 translates to pixel[255]
        #   and color index [1:256] -> pixel[0:255]
        u = ((voxel.colorIndex - 1)/256 + 1/512, 0.5)
        outFaces.append(
            # this is most definitely not "fun"
            AAQuad(f, u, n)
        )
    def _getObjFacesSupport(self, side, color, faces, outFaces):
        n = AAQuad.normals[side]
        # note: texcoords are based on MagicaVoxel's texturing scheme!
        #   meaning a color index of 0 translates to pixel[255]
        #   and color index [1:256] -> pixel[0:255]
        u = ((color - 1)/256 + 1/512, 0.5)
        outFaces.append(
            # fact: the parameters were coincidentally "f, u, n" at one point!
            AAQuad(faces, u, n)
        )
    # MagicaVoxel does -.5 to +.5 for each cube, we'll do 0.0 to 1.0 ;)
    def _getLeftSide(self, voxel):
        return [
            (voxel.x, voxel.y + 1, voxel.z + 1),
            (voxel.x, voxel.y + 1, voxel.z),
            (voxel.x, voxel.y, voxel.z),
            (voxel.x, voxel.y, voxel.z + 1)
        ]
    def _getRightSide(self, voxel):
        return (
            (voxel.x + 1, voxel.y, voxel.z + 1),
            (voxel.x + 1, voxel.y, voxel.z),
            (voxel.x + 1, voxel.y + 1, voxel.z),
            (voxel.x + 1, voxel.y + 1, voxel.z + 1)
        )
    def _getTopSide(self, voxel):
        return (
            (voxel.x, voxel.y + 1, voxel.z + 1),
            (voxel.x, voxel.y, voxel.z + 1),
            (voxel.x + 1, voxel.y, voxel.z + 1),
            (voxel.x + 1, voxel.y + 1, voxel.z + 1)
        )
    def _getBottomSide(self, voxel):
        return (
            (voxel.x, voxel.y, voxel.z),
            (voxel.x, voxel.y + 1, voxel.z),
            (voxel.x + 1, voxel.y + 1, voxel.z),
            (voxel.x + 1, voxel.y, voxel.z)
        )
    def _getFrontSide(self, voxel):
        return (
            (voxel.x, voxel.y, voxel.z + 1),
            (voxel.x, voxel.y, voxel.z),
            (voxel.x + 1, voxel.y, voxel.z),
            (voxel.x + 1, voxel.y, voxel.z + 1)
        )
    def _getBackSide(self, voxel):
        return (
            (voxel.x + 1, voxel.y + 1, voxel.z + 1),
            (voxel.x + 1, voxel.y + 1, voxel.z),
            (voxel.x, voxel.y + 1, voxel.z),
            (voxel.x, voxel.y + 1, voxel.z + 1)
        )
    def _objExposed(self, voxel):
        """ --> a set of [0, 6) representing which voxel faces are shown
            for the meaning of 0-5, see AAQuad.normals
            get the sick truth about these voxels' dirty secrets...
        """
        # check left 0
        side = self.getVoxel(voxel.x - 1, voxel.y, voxel.z)
        s0 = side is None or side.colorIndex == 0
        # check right 1
        side = self.getVoxel(voxel.x + 1, voxel.y, voxel.z)
        s1 = side is None or side.colorIndex == 0
        # check top 2
        side = self.getVoxel(voxel.x, voxel.y, voxel.z + 1)
        s2 = side is None or side.colorIndex == 0
        # check bottom 3
        side = self.getVoxel(voxel.x, voxel.y, voxel.z - 1)
        s3 = side is None or side.colorIndex == 0
        # check front 4
        side = self.getVoxel(voxel.x, voxel.y - 1, voxel.z)
        s4 = side is None or side.colorIndex == 0
        # check back 5
        side = self.getVoxel(voxel.x, voxel.y + 1, voxel.z)
        s5 = side is None or side.colorIndex == 0
        return s0, s1, s2, s3, s4, s5

class Voxel:
    def __init__(self, x, y, z, colorIndex):
        self.x = x
        self.y = y
        self.z = z
        self.colorIndex = colorIndex

def genNormals(self, aaQuads, overwrite=False):
    # compute CCW normal if it doesn't exist
    for face in aaQuads:
        if overwrite or face.normal is None:
            side_a = (face.vertices[1][0] - face.vertices[0][0],
                      face.vertices[1][1] - face.vertices[0][1],
                      face.vertices[1][2] - face.vertices[0][2])
            side_b = (face.vertices[-1][0] - face.vertices[0][0],
                      face.vertices[-1][1] - face.vertices[0][1],
                      face.vertices[-1][2] - face.vertices[0][2])
            # compute the cross product
            face.normal = (side_a[1]*side_b[2] - side_a[2]*side_b[1],
                           side_a[2]*side_b[0] - side_a[0]*side_b[2],
                           side_a[0]*side_b[1] - side_a[1]*side_b[0])

def importObj(stream):
    vertices = []
    faces = []
    uvs = []
    normals = []
    for line in stream:
        # make sure there's no new line or trailing spaces
        l = line.strip().split(' ')
        lineType = l[0].strip()
        data = l[1:]
        if lineType == 'v':
            # vertex
            v = tuple(map(float, data))
            vertices.append(v)
        elif lineType == 'vt':
            # uv
            uvs.append( tuple(map(float, data)) )
        elif lineType == 'vn':
            # normal
            normals.append( tuple(map(float, data)) )
        elif lineType == 'f':
            # face (assume all verts/uvs/normals have been processed)
            faceVerts = []
            faceUvs = []
            faceNormals = []
            for v in data:
                result = v.split('/')
                print(result)
                # recall that everything is 1 indexed...
                faceVerts.append(vertices[int(result[0]) - 1])
                if len(result) == 1:
                    continue # there is only a vertex index
                if result[1] != '':
                    # uvs may not be present, ex: 'f vert//normal ...'
                    faceUvs.append(uvs[int(result[1]) - 1])
                if len(result) <= 2:
                    # don't continue if only vert and uv are present
                    continue
                faceNormals.append(normals[int(result[2]) - 1])
            faces.append( GeoFace(faceVerts, faceUvs, faceNormals) )
        else:
            # there could be material specs, smoothing, or comments... ignore!
            pass
    return faces

def exportObj(stream, aaQuads):
    # gather some of the needed information
    faces = aaQuads
    # copy the normals from AAQuad (99% of cases will use all directions)
    normals = list(AAQuad.normals)
    uvs = set()
    for f in faces:
        if f.uv is not None:
            uvs.add(f.uv)
    # convert this to a list because we need to get their index later
    uvs = list(uvs)
    # we will build a list of vertices as we go and then write everything
    # in bulk, disadvantage that MANY verts will be duplicated in the OBJ file
    fLines = []
    vertices = []
    indexOffset = 0
    for f in faces:
        # recall that OBJ files are 1 indexed
        n = 1 + normals.index(f.normal) if f.normal is not None else ''
        uv = 1 + uvs.index(f.uv) if f.uv is not None else ''
        # this used to be a one liner ;)
        fLine = ['f']
        for i, vert in enumerate(f.vertices):
            # for each vertex of this face
            v = 1 + indexOffset + f.vertices.index(vert)
            fLine.append(str(v) + '/' + str(uv) + '/' + str(n))
        vertices.extend(f.vertices)
        indexOffset += len(f.vertices)
        fLines.append(' '.join(fLine) + '\n')
    # write to the file
    stream.write('# shivshank\'s .obj optimizer\n')
    stream.write('\n')
    if len(normals) > 0:
        stream.write('# normals\n')
        for n in normals:
            stream.write('vn ' + ' '.join(list(map(str, n))) + '\n')
        stream.write('\n')
    if len(uvs) > 0:
        stream.write('# texcoords\n')
        for i in uvs:
            stream.write('vt ' + ' '.join(list(map(str, i))) + '\n')
        stream.write('\n')
    # output the vertices and faces
    stream.write('# verts\n')
    for v in vertices:
        stream.write('v ' + ' '.join(list(map(str, v))) + '\n')
    stream.write('\n')
    stream.write('# faces\n')
    for i in fLines:
        stream.write(i)
    stream.write('\n')
    stream.write('\n')
    return len(vertices), len(fLines)

DEFAULT_PALETTE = [
    0x00000000, 0xffffffff, 0xffccffff, 0xff99ffff, 0xff66ffff, 0xff33ffff, 0xff00ffff, 0xffffccff, 0xffccccff, 0xff99ccff, 0xff66ccff, 0xff33ccff, 0xff00ccff, 0xffff99ff, 0xffcc99ff, 0xff9999ff,
    0xff6699ff, 0xff3399ff, 0xff0099ff, 0xffff66ff, 0xffcc66ff, 0xff9966ff, 0xff6666ff, 0xff3366ff, 0xff0066ff, 0xffff33ff, 0xffcc33ff, 0xff9933ff, 0xff6633ff, 0xff3333ff, 0xff0033ff, 0xffff00ff,
    0xffcc00ff, 0xff9900ff, 0xff6600ff, 0xff3300ff, 0xff0000ff, 0xffffffcc, 0xffccffcc, 0xff99ffcc, 0xff66ffcc, 0xff33ffcc, 0xff00ffcc, 0xffffcccc, 0xffcccccc, 0xff99cccc, 0xff66cccc, 0xff33cccc,
    0xff00cccc, 0xffff99cc, 0xffcc99cc, 0xff9999cc, 0xff6699cc, 0xff3399cc, 0xff0099cc, 0xffff66cc, 0xffcc66cc, 0xff9966cc, 0xff6666cc, 0xff3366cc, 0xff0066cc, 0xffff33cc, 0xffcc33cc, 0xff9933cc,
    0xff6633cc, 0xff3333cc, 0xff0033cc, 0xffff00cc, 0xffcc00cc, 0xff9900cc, 0xff6600cc, 0xff3300cc, 0xff0000cc, 0xffffff99, 0xffccff99, 0xff99ff99, 0xff66ff99, 0xff33ff99, 0xff00ff99, 0xffffcc99,
    0xffcccc99, 0xff99cc99, 0xff66cc99, 0xff33cc99, 0xff00cc99, 0xffff9999, 0xffcc9999, 0xff999999, 0xff669999, 0xff339999, 0xff009999, 0xffff6699, 0xffcc6699, 0xff996699, 0xff666699, 0xff336699,
    0xff006699, 0xffff3399, 0xffcc3399, 0xff993399, 0xff663399, 0xff333399, 0xff003399, 0xffff0099, 0xffcc0099, 0xff990099, 0xff660099, 0xff330099, 0xff000099, 0xffffff66, 0xffccff66, 0xff99ff66,
    0xff66ff66, 0xff33ff66, 0xff00ff66, 0xffffcc66, 0xffcccc66, 0xff99cc66, 0xff66cc66, 0xff33cc66, 0xff00cc66, 0xffff9966, 0xffcc9966, 0xff999966, 0xff669966, 0xff339966, 0xff009966, 0xffff6666,
    0xffcc6666, 0xff996666, 0xff666666, 0xff336666, 0xff006666, 0xffff3366, 0xffcc3366, 0xff993366, 0xff663366, 0xff333366, 0xff003366, 0xffff0066, 0xffcc0066, 0xff990066, 0xff660066, 0xff330066,
    0xff000066, 0xffffff33, 0xffccff33, 0xff99ff33, 0xff66ff33, 0xff33ff33, 0xff00ff33, 0xffffcc33, 0xffcccc33, 0xff99cc33, 0xff66cc33, 0xff33cc33, 0xff00cc33, 0xffff9933, 0xffcc9933, 0xff999933,
    0xff669933, 0xff339933, 0xff009933, 0xffff6633, 0xffcc6633, 0xff996633, 0xff666633, 0xff336633, 0xff006633, 0xffff3333, 0xffcc3333, 0xff993333, 0xff663333, 0xff333333, 0xff003333, 0xffff0033,
    0xffcc0033, 0xff990033, 0xff660033, 0xff330033, 0xff000033, 0xffffff00, 0xffccff00, 0xff99ff00, 0xff66ff00, 0xff33ff00, 0xff00ff00, 0xffffcc00, 0xffcccc00, 0xff99cc00, 0xff66cc00, 0xff33cc00,
    0xff00cc00, 0xffff9900, 0xffcc9900, 0xff999900, 0xff669900, 0xff339900, 0xff009900, 0xffff6600, 0xffcc6600, 0xff996600, 0xff666600, 0xff336600, 0xff006600, 0xffff3300, 0xffcc3300, 0xff993300,
    0xff663300, 0xff333300, 0xff003300, 0xffff0000, 0xffcc0000, 0xff990000, 0xff660000, 0xff330000, 0xff0000ee, 0xff0000dd, 0xff0000bb, 0xff0000aa, 0xff000088, 0xff000077, 0xff000055, 0xff000044,
    0xff000022, 0xff000011, 0xff00ee00, 0xff00dd00, 0xff00bb00, 0xff00aa00, 0xff008800, 0xff007700, 0xff005500, 0xff004400, 0xff002200, 0xff001100, 0xffee0000, 0xffdd0000, 0xffbb0000, 0xffaa0000,
    0xff880000, 0xff770000, 0xff550000, 0xff440000, 0xff220000, 0xff110000, 0xffeeeeee, 0xffdddddd, 0xffbbbbbb, 0xffaaaaaa, 0xff888888, 0xff777777, 0xff555555, 0xff444444, 0xff222222, 0xff111111
]

def importVox(file):
    """ --> a VoxelStruct from this .vox file stream """
    # in theory this could elegantly be many functions and classes
    # but this is such a simple file format...
    # refactor: ? should probably find a better exception type than value error
    vox = VoxelStruct()
    palette = [((c >> 24) & 0xFF, (c >> 16) & 0xFF, (c >> 8) & 0xFF, c & 0xFF) for c in DEFAULT_PALETTE]

    magic = file.read(4)
    if magic != b'VOX ':
        print('magic number is', magic)
        if userAborts('This does not appear to be a VOX file. Abort?'):
            raise ValueError("Invalid magic number")
    # the file appears to use little endian consistent with RIFF
    version = int.from_bytes(file.read(4), byteorder='little')
    if version != 150:
        if userAborts('Only version 150 is supported; this file: '
                      + str(version) + '. Abort?'):
            raise ValueError("Invalid file version")

    mainHeader = _readChunkHeader(file)
    if mainHeader['id'] != b'MAIN':
        print('chunk id:', mainId)
        if userAborts('Did not find the main chunk. Abort?'):
            raise ValueError("Did not find main VOX chunk. ")
    #assert mainHeader['size'] == 0, "main chunk should have size 0"

    nextHeader = _readChunkHeader(file)
    while nextHeader:
        if nextHeader['id'] == b'XYZI':
            seekPos = file.tell()
            voxelHeader = nextHeader
            _processXYZIChunk(voxelHeader, vox)
            # assert that we've read the entire voxel chunk
            assert file.tell() - seekPos == voxelHeader['size']

        elif nextHeader['id'] == b'RGBA':
            seekPos = file.tell()
            voxelHeader = nextHeader
            _processRGBAChunk(voxelHeader, palette)
            # assert that we've read the entire voxel chunk
            assert file.tell() - seekPos == voxelHeader['size']

        else:
            print(f"Skipping {nextHeader['id'].decode('utf8')} ({nextHeader['size']} bytes)")
            file.read(nextHeader['size'] + nextHeader['childrenSize'])

        try:
            nextHeader = _readChunkHeader(file)
        except ValueError:
            nextHeader = None

    return vox, palette

def _processXYZIChunk(voxelHeader, vox):
    print(f"{voxelHeader['id'].decode('utf8')} ({voxelHeader['size']} bytes)")
    assert voxelHeader['id'] == b'XYZI', 'this should be literally impossible'
    assert voxelHeader['childrenSize'] == 0, 'why voxel chunk have children?'
    totalVoxels = int.from_bytes(file.read(4), byteorder='little')
    ### READ THE VOXELS ###
    for i in range(totalVoxels):
        # n.b., byte order should be irrelevant since these are all 1 byte
        x = int.from_bytes(file.read(1), byteorder='little')
        y = int.from_bytes(file.read(1), byteorder='little')
        z = int.from_bytes(file.read(1), byteorder='little')
        color = int.from_bytes(file.read(1), byteorder='little')
        vox.setVoxel(Voxel(x, y, z, color))

def _processRGBAChunk(voxelHeader, palette):
    print(f"{voxelHeader['id'].decode('utf8')} ({voxelHeader['size']} bytes)")
    assert voxelHeader['id'] == b'RGBA', 'this should be literally impossible'
    assert voxelHeader['childrenSize'] == 0, 'why voxel chunk have children?'
    for i in range(256):
        # n.b., byte order should be irrelevant since these are all 1 byte
        r = int.from_bytes(file.read(1), byteorder='little')
        g = int.from_bytes(file.read(1), byteorder='little')
        b = int.from_bytes(file.read(1), byteorder='little')
        a = int.from_bytes(file.read(1), byteorder='little')
        if i < 255:
            palette[i + 1] = (r, g, b, a)

def _readChunkHeader(buffer):
    id = buffer.read(4)
    if id == b'':
        raise ValueError("Unexpected EOF, expected chunk header")
    size = int.from_bytes(buffer.read(4), byteorder='little')
    childrenSize = int.from_bytes(buffer.read(4), byteorder='little')
    return {
        'id': id, 'size': size, 'childrenSize': childrenSize
    }

def userAborts(msg):
    print(msg + ' (y/n)')
    u = input()
    if u.startswith('n'):
        return False

    return True

def exportAll():
    """ Uses a file to automatically export a bunch of files!
        See this function for details on the what the file looks like.
    """
    import os, os.path

    with open('exporter.txt', mode='r') as file:
        # use this as a file "spec"
        fromSource = os.path.abspath(file.readline().strip())
        toExportDir = os.path.abspath(file.readline().strip())
        optimizing = file.readline()
        if optimizing.lower() == 'true':
            optimizing = True
        else:
            optimizing = False

    print('exporting vox files under', fromSource)
    print('\tto directory', toExportDir)
    print('\toptimizing?', optimizing)
    print()

    # export EVERYTHING (.vox) walking the directory structure
    for p, dirList, fileList in os.walk(fromSource):
        pathDiff = os.path.relpath(p, start=fromSource)
        outDir = os.path.join(toExportDir, pathDiff)
        # REFACTOR: the loop should be moved to a function
        for fileName in fileList:
            # only take vox files
            if os.path.splitext(fileName)[1] != '.vox':
                print('ignored', fileName)
                continue
            print('exporting', fileName)
            # read/import the voxel file
            with open(os.path.join(p, fileName), mode='rb') as file:
                try:
                    vox, palette = importVox(file)
                except ValueError as exc:
                    print('aborted', fileName, str(exc))
                    continue
            # mirror the directory structure in the export folder
            if not os.path.exists(outDir):
                os.makedirs(outDir)
                print('\tcreated directory', outDir)
            # export a non-optimized version
            objName = os.path.splitext(fileName)[0]
            rawQuads = vox.toQuads()
            with open(os.path.join(outDir, objName + '.obj'), mode='w') as file:
                vCount, qCount = exportObj(file, rawQuads)
            print('\texported', vCount, 'vertices,', qCount, 'quads')
            if optimizing:
                # TODO
                continue
                optiFaces = optimizedGreedyMesh(rawQuads)
                bucketHash(optiFaces, *vox.getBounds())
                with open(os.path.join(outDir, objName + '.greedy.obj'),
                          mode='w') as file:
                    exportObj(file, optiFaces)

if __name__ == "__main__":
    import os, os.path, sys
    from glob import glob

    u = os.path.abspath(sys.argv[0]).strip(os.path.basename(sys.argv[0]))
    print(u)

    for i in sys.argv:
        if i != sys.argv[0]:
            print(i)

    while not os.path.exists(u):
        print('That path does not exist.')
        print('Enter an output path:')
        u = input('> ').strip()
    outRoot = os.path.abspath(u)

    u = sys.argv
    for f in u:
        if f != sys.argv[0]:
            print('reading VOX file', f)
            with open(f, mode='rb') as file:
                try:
                    vox, palette = importVox(file)
                except ValueError:
                    print('\tfile reading aborted')
                    continue
            outFile = os.path.splitext(os.path.basename(f))[0]
            outPath = os.path.join(outRoot, outFile + '.obj')
            print('exporting VOX to OBJ at path', outPath)
            with open(outPath, mode='w') as file:
                exportObj(file, vox.toQuads())
