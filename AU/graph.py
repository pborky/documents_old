
class Vertex:
    def __init__(self, name, kind, edgesIn, edgesOut):
        self.name = name
        self.kind = kind
        for i in edgesIn:
            if i.end == None:
                i.end = self
            else:
                raise Exception('fooka')
        for i in edgesOut:
            if i.start == None:
                i.start = self
            else:
                raise Exception('fooka')
        self.edgesIn = edgesIn
        self.edgesOut = edgesOut

    def dot(self):
        return unicode(self.name)

class Edge:
    def __init__(self, name):
        self.name = name
        self.start = None
        self.end = None

    def dot(self):
        if self.start == None or self.end == None:
            raise Exception('fooka')
        return self.start.dot() + u' -> ' + self.end.dot() + u' [label="'+unicode(self.name)+'"]'


class Graph:
    def __init__(self, name):
        self.name = name
        self.edges = {}
        self.verticles = {}

    def getEdge(self, name):
        if name in self.edges:
            return self.edges[name]
        else:
            e = Edge(name)
            self.edges[name] = e
            return e

    def add(self, name, kind, edgesIn, edgesOut):
        ei = []
        eo = []

        for i in edgesIn:
            ei.append(self.getEdge(i))

        for i in edgesOut:
            eo.append(self.getEdge(i))

        if name in self.verticles:
            raise Exception('fooka')
        v = Vertex(name, kind, ei, eo)
        self.verticles[name] = v
        return v

    def dot(self):
        s = u'digraph '+self.name+u' { '
        for e in self.edges.values():
            s = s+e.dot()+u'; '
        for v in self.verticles.values():
            if v.kind in ['SIGNAL','INPUT', 'DIVERGING', 'CONNECTING']:
                s = s+unicode(v.name)+u' [shape=hexagon]; ';
        s = s+u'rankdir=LR; }'
        return s


