
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
            if v.kind in ['CONNECTING',]:
                s = s+unicode(v.name)+u' [shape=hexagon,fillcolor=lightslateblue,style=filled]; '
            if v.kind in ['INPUT','SIGNAL']:
                s = s+unicode(v.name)+u' [shape=hexagon,fillcolor=salmon,style=filled]; '
            if v.kind in ['DIVERGING',]:
                s = s+unicode(v.name)+u' [fillcolor=lightskyblue,style=filled]; '

        s = s+u'rankdir=LR; }'
        return s

    def getTimeAxiom(self,time, s):
        if time == 0:
            if s == None:
                return u'T'
            else:
                return s
        elif time > 0:
            if s == None:
                return self.getTimeAxiom(time-1, u'succ(T)')
            else:
                return self.getTimeAxiom(time-1, u'succ({})'.format(s))
        elif time < 0:
            if s == None:
                return self.getTimeAxiom(time+1, u'pred(T)')
            else:
                return self.getTimeAxiom(time+1, u'pred({})'.format(s))

    def getIsHereAxiom(self, edge, time):        
        return u'ishere({},{})'.format(self.getTimeAxiom(time, None),edge.name)

    def getCanPassAxiom(self, vertex, time, inv):
        if inv:
            return u'~{}'.format(self.getCanPassAxiom(vertex, time, False))
        return u'signal({},{})'.format(self.getTimeAxiom(time, None), vertex.name)

    def getBehaviorAxioms(self):
        ax = {}
        for e in self.edges.values():
            n = u'ishere{}'.format(e.name)
            s = None

            # Backward
            a = []
            if e.start.kind == 'SIGNAL':
                a.append(self.getIsHereAxiom(e.start.edgesIn[0], 0))
                a.append(self.getCanPassAxiom(e.start, 0, False))
                s = u'{} & {}'.format(*a)
            elif e.start.kind == 'INPUT':
                a.append(self.getCanPassAxiom(e.start, 0, False))
                s = u'{}'.format(*a)
            elif e.start.kind == 'DIRECT':
                a.append(self.getIsHereAxiom(e.start.edgesIn[0], 0))
                s = u'{}'.format(*a)
            elif e.start.kind == 'CONNECTING':
                a.append(self.getIsHereAxiom(e.start.edgesIn[0], 0))
                a.append(self.getCanPassAxiom(e.start, 0, False))
                a.append(self.getIsHereAxiom(e.start.edgesIn[1], 0))
                a.append(self.getCanPassAxiom(e.start, 0, True))
                s = u'{} & {} | {} & {}'.format(*a)
            elif e.start.kind == 'DIVERGING':
                a.append(self.getIsHereAxiom(e.start.edgesIn[0], 0))
                if e.start.edgesOut[0] == e:
                    a.append(self.getCanPassAxiom(e.start, 0, False))
                elif e.start.edgesOut[1] == e:
                    a.append(self.getCanPassAxiom(e.start, 0, True))
                s = u'{} & {}'.format(*a)
            else:
                raise Exception('fooka')

            # Forward
            a = []
            if e.end.kind == 'SIGNAL':
                a.append(s)
                a.append(self.getIsHereAxiom(e, 0))
                a.append(self.getCanPassAxiom(e.end, 0, True))
                s = u'{} | {} & {}'.format(*a)
            elif e.end.kind == 'CONNECTING':
                a.append(s)
                a.append(self.getIsHereAxiom(e, 0))
                if e.end.edgesIn[0] == e:
                    a.append(self.getCanPassAxiom(e.end, 0, False))
                elif e.end.edgesIn[1] == e:
                    a.append(self.getCanPassAxiom(e.end, 0, True))
                s = u'{} | {} & {}'.format(*a)

            # Final
            a = []
            a.append(self.getIsHereAxiom(e, 1))
            a.append(s)
            ax[n] = u'![T]: ( {} <=> ( {} ) )'.format(*a)
        return ax

    def getSignalingAxioms(self):
        ax = {}
        return ax

    def tp(self):
        ax = {}
        ax.update(self.getBehaviorAxioms())
        ax.update(self.getSignalingAxioms())
        s = None
        k = ax.keys()
        k.sort()
        for i in k:
            a = ax[i]
            if s == None:
                s = u'fof( {}, axiom, ( {} )).'.format(i,a)
            else:
                s = u'{}\nfof( {}, axiom, ( {} )).'.format(s, i, a)

        return s
            


