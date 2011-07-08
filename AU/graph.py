
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

    def getTimeTerm(self,time, s):
        if time == 0:
            if s == None:
                return u'T'
            else:
                return s
        elif time > 0:
            if s == None:
                return self.getTimeTerm(time-1, u'succ(T)')
            else:
                return self.getTimeTerm(time-1, u'succ({})'.format(s))
        elif time < 0:
            if s == None:
                return self.getTimeTerm(time+1, u'pred(T)')
            else:
                return self.getTimeTerm(time+1, u'pred({})'.format(s))

    def getIsHereClause(self, edge, time, neg=False, target='X'):
        if neg:
            return u'~{}'.format(self.getIsHereClause(edge, time))
        return u'ishere({},{},{})'.format(self.getTimeTerm(time, None),edge.name, target)

    def getCollisionClause(self, edge, time, neg=False):
        if neg:
            return u'~{}'.format(self.getCollisionClause(edge, time))
        return u'collision({},{})'.format(self.getTimeTerm(time, None),edge.name)

    def getCanPassClause(self, vertex, time, neg=False):
        if neg:
            return u'~{}'.format(self.getCanPassClause(vertex, time))
        return u'signal({},{})'.format(self.getTimeTerm(time, None), vertex.name)

    def getEnterClause(self, e):
        a = []
        if e.start.kind == 'SIGNAL':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            a.append(self.getCanPassClause(e.start, 0))
            return u'{} & {}'.format(*a)
        elif e.start.kind == 'INPUT':
            a.append(self.getIsHereClause(e.start, 0))
            a.append(self.getCanPassClause(e.start, 0))
            return u'{} & {}'.format(*a)
        elif e.start.kind == 'DIRECT':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            return u'{}'.format(*a)
        elif e.start.kind == 'CONNECTING':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            a.append(self.getCanPassClause(e.start, 0))
            a.append(self.getIsHereClause(e.start.edgesIn[1], 0))
            a.append(self.getCanPassClause(e.start, 0, True))
            return u'{} & {} | {} & {}'.format(*a)
        elif e.start.kind == 'DIVERGING':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            if e.start.edgesOut[0] == e:
                a.append(self.getCanPassClause(e.start, 0))
            elif e.start.edgesOut[1] == e:
                a.append(self.getCanPassClause(e.start, 0, True))
            return u'{} & {}'.format(*a)
        else:
            raise Exception('fooka')

    def getLeaveClause(self, e, cannotleave=False,target='X'):
        a = []
        if e.end.kind == 'SIGNAL':
            a.append(self.getIsHereClause(e, 0,target=target))
            a.append(self.getCanPassClause(e.end, 0, not cannotleave))
        elif e.end.kind == 'CONNECTING':
            a.append(self.getIsHereClause(e, 0,target=target))
            if e.end.edgesIn[0] == e:
                a.append(self.getCanPassClause(e.end, 0, not cannotleave))
            elif e.end.edgesIn[1] == e:
                a.append(self.getCanPassClause(e.end, 0, cannotleave))
        else:
            return None

        return u'{} & {}'.format(*a)

    def getBehaviorAxioms(self):
        ax = {}
        for e in self.edges.values():
            n = u'ishere{}'.format(e.name)
            a = []
            a.append(self.getIsHereClause(e, 1))
            a.append(self.getEnterClause(e))
            c = self.getLeaveClause(e)
            if c == None:
                ax[n] = u'![T,X]:( {} <=> ( {} ) )'.format(*a)
            else:
                a.append(c)
                ax[n] = u'![T,X]:( {} <=> ( {} | {} ) )'.format(*a)
        return ax

    def getCollisionAxioms(self):
        ax = {}
        for e in self.edges.values():
            n = u'collision{}'.format(e.name)

            a = []
            a.append(self.getCollisionClause(e, 1))
            a.append(self.getEnterClause(e))
            c = self.getLeaveClause(e,target = 'Y')
            if c == None:
                continue
            else:
                a.append(c)
                ax[n] = u'![T]:(?[X,Y]:( {} <=> ( ({}) & ({}) ) ))'.format(*a)
        return ax

    def getSignalingAxioms(self):
        ax = {}
        return ax

    def getTPTPfof(self, kind, ax):
        s = None
        k = ax.keys()
        k.sort()
        for i in k:
            a = ax[i]
            if s == None:
                s = u'fof( {}, {}, ( {} )).'.format(i,kind,a)
            else:
                s = u'{}\nfof( {}, {}, ( {} )).'.format(s, i, kind, a)

        return s


    def tp(self):
        return '% Train movement axioms \n{}\n\n% Collision axioms \n{}\n\n% Signaling control \n{}\n\n'.format(
            self.getTPTPfof('axiom', self.getBehaviorAxioms()), 
            self.getTPTPfof('axiom', self.getCollisionAxioms()), 
            self.getTPTPfof('axiom', self.getSignalingAxioms()))

