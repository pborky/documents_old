
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
            if v.kind in ['CONVERGENT',]:
                s = s+unicode(v.name)+u' [shape=hexagon,fillcolor=lightslateblue,style=filled]; '
            if v.kind in ['INPUT','SIGNAL']:
                s = s+unicode(v.name)+u' [shape=hexagon,fillcolor=salmon,style=filled]; '
            if v.kind in ['DIVERGENT',]:
                s = s+unicode(v.name)+u' [fillcolor=lightskyblue,style=filled]; '

        s = s+u'rankdir=LR; }'
        return s

    def getTimeTerm(self,time, s=None, literal=u'T'):
        if time == 0:
            if s == None:
                return u'{}'.format(literal)
            else:
                return s
        elif time > 0:
            if s == None:
                return self.getTimeTerm(time-1, u'succ({})'.format(literal))
            else:
                return self.getTimeTerm(time-1, u'succ({})'.format(s))
        elif time < 0:
            if s == None:
                return self.getTimeTerm(time+1, u'pred({})'.format(literal))
            else:
                return self.getTimeTerm(time+1, u'pred({})'.format(s))

    def getIsHereClause(self, edge, time, neg=False, target=u'X'):
        if neg:
            return u'~{}'.format(self.getIsHereClause(edge, time))
        return u'ishere({},{},{})'.format(self.getTimeTerm(time),edge.name, target)

    def getCollisionClause(self, edge, time, neg=False):
        if neg:
            return u'~{}'.format(self.getCollisionClause(edge, time))
        return u'collision({},{})'.format(self.getTimeTerm(time),edge.name)

    def getCanPassClause(self, vertex, time, neg=False):
        if neg:
            return u'~{}'.format(self.getCanPassClause(vertex, time))
        return u'signal({},{})'.format(self.getTimeTerm(time), vertex.name)

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
        elif e.start.kind == 'CONVERGENT':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            a.append(self.getCanPassClause(e.start, 0))
            a.append(self.getIsHereClause(e.start.edgesIn[1], 0))
            a.append(self.getCanPassClause(e.start, 0, True))
            return u'({} & {}) | ({} & {})'.format(*a)
        elif e.start.kind == 'DIVERGENT':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            if e.start.edgesOut[0] == e:
                a.append(self.getCanPassClause(e.start, 0))
            elif e.start.edgesOut[1] == e:
                a.append(self.getCanPassClause(e.start, 0, True))
            return u'{} & {}'.format(*a)
        else:
            raise Exception('fooka')

    def getLeaveClause(self, e, cannotleave=False,target=u'X'):
        a = []
        if e.end.kind == 'SIGNAL':
            a.append(self.getIsHereClause(e, 0,target=target))
            a.append(self.getCanPassClause(e.end, 0, not cannotleave))
        elif e.end.kind == 'CONVERGENT':
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
            n = u'ishere_{}'.format(e.name)
            a = []
            a.append(self.getIsHereClause(e, 1))
            a.append(self.getEnterClause(e))
            c = self.getLeaveClause(e)
            if c == None:
                ax[n] = u'![T,X]:( {} <=> ( {} ) )'.format(*a)
            else:
                a.append(c)
                ax[n] = u'![T,X]:( {} <=> ( ({}) | ({}) ) )'.format(*a)
        return ax 

    def getCollisionAxioms(self):
        ax = {}
        for e in self.edges.values():
            n = u'collision_{}'.format(e.name)

            a = []
            a.append(self.getCollisionClause(e, 1))
            a.append(self.getEnterClause(e))
            c = self.getLeaveClause(e,target = u'Y')
            if c == None:
                continue
            else:
                a.append(c)
                ax[n] = u'![T]:(?[X,Y]:( {} <=> ( ({}) & ({}) ) ))'.format(*a)
        return ax

    def getTPTPfof(self, kind, ax):
        k = ax.keys()
        if len(k) == 0:
            s = '% None'
        else:
            s = None 
            k.sort()
            for i in k:
                a = ax[i]
                if s == None:
                    s = u'fof( {}, {}, ( {} )).'.format(i,kind,a)
                else:
                    s = u'{}\nfof( {}, {}, ( {} )).'.format(s, i, kind, a)
        return s
    
    def getTrainOnInput(self):
        ax = {}
        iverticles = []
        overticles = []
        for v in self.verticles.values():
            if v.kind in ['INPUT']:
                iverticles.append(v)
        for v in self.verticles.values():
            if v.kind in ['OUTPUT']:
                overticles.append(v)
        s = None
        for v in iverticles:
            c = []
            fmt = []
            fmt2 = []
            for o in overticles:
                c.append(u'ishere(T,{},{})'.format(v.name, o.name))
                fmt.append(u'~ {} & ')
                fmt2.append(u'{} | ')
            l = len(overticles)
            fmt[l-1] = u'~ {}'
            fmt2[l-1] = u'{}'
            s = []
            for i in range(l):
                f = fmt[:]
                f[i] = f[i][2:]
                f = u'({})'.format(''.join(f))
                s.append(f.format(*c))
            f =  ''.join(fmt2)
            s = f.format(*s)
            n = u'input_{}'.format(v.name)
            ax[n] = u'?[T]:({})'.format(s)
        ax[u'zzz'] = u'ishere(t,06,o1) & ishere(t,07,o3) & ishere(t,11,o3) '
        return ax


    def traverse(self, edge, nodeset=None, edgeset=None, back=False, targets=['INPUT','SIGNAL']):
        node = (back and [edge.start] or [edge.end])[0]
        if node.kind in targets:
            if nodeset <> None:
                nodeset.add(node)
            if edgeset <> None:
                edgeset.add(edge)
        else:
            edges = (back and [node.edgesIn] or [node.edgesOut])[0]
            for e in edges:
                es = set()
                self.traverse(e, nodeset, edgeset=es, back=back,targets=targets)
                if len(es) > 0:
                    if edgeset <> None:
                        edgeset.add(edge)
                        edgeset |= es

    def getSignalingByEdges(self, node, edges):
        i = 0
        s = None
        q = None
        for e in edges:
            if s == None:
                s = u'~ishere(T,{},Y{})'.format(e.name,i)
            else:
                s = u'{} & ~ishere(T,{},Y{})'.format(s,e.name,i)
            if q == None:
                q = u'Y{}'.format(i)
            else:
                q = u'{},Y{}'.format(q,i)
            i += 1
        if s <> None:
            return u'![T,{}]:( signal(T,{}) <=> ({}) )'.format(q,node.name,s)

    def getSignalingByNodes(self, node, nodes):
        s = None
        for n in nodes:
            if s == None:
                s = u'~signal(T,{})'.format(n.name)
            else:
                s = u'{} & ~signal(T,{})'.format(s,n.name)
        if s <> None:
            return u'![T]:( signal(T,{}) => ({}) )'.format(node.name,s)

    def getSubgraph(self, node):
        edgeset = set()
        nodeset = set()
        nodeset2 = set()
        for e in node.edgesOut:
            self.traverse(e, nodeset=nodeset2)
        for n in nodeset2:
            for e in n.edgesIn:
                self.traverse(e, nodeset=nodeset, edgeset=edgeset, back=True)
        if node in nodeset:
            nodeset.remove(node)
        return (nodeset, edgeset)

    def getSignalingAxioms(self):
        ax = {}
        for node in self.verticles.values():
            if node.kind in ['CONVERGENT']:
                n = u'signal_{}'.format(node.name)
                ax[n] = u'![T,X]:(ishere(T,{},X) => signal(T,{}))'.format(node.edgesIn[0].name, node.name)
            elif node.kind in ['DIVERGENT']:
                nodeset0 = set()
                nodeset1 = set()
                self.traverse(node.edgesOut[0], nodeset=nodeset0, targets=['OUTPUT'])
                self.traverse(node.edgesOut[1], nodeset=nodeset1, targets=['OUTPUT'])
                same = nodeset0 & nodeset1
                diff0 = nodeset0 - nodeset1
                diff1 = nodeset1 - nodeset0
                for n in same | diff0: 
                    s = u'![T]:(ishere(T,{},{}) => signal(T,{}))'.format(node.edgesIn[0].name, n.name, node.name)
                    n = u'signal_{}_{}'.format(node.name,n.name)
                    ax[n] = s
                for n in diff1:
                    s = u'![T]:(ishere(T,{},{}) => ~signal(T,{}))'.format(node.edgesIn[0].name, n.name, node.name)
                    n = u'signal_{}_{}'.format(node.name,n.name)
                    ax[n] = s
            elif node.kind in ['INPUT','SIGNAL']:
                (nodeset, edgeset) = self.getSubgraph(node)
                n = u'signal_{}_exclusive'.format(node.name)
                s = self.getSignalingByNodes(node, nodeset)
                if s <> None:
                    ax[n] = s
                n = u'signal_{}'.format(node.name)
                s = self.getSignalingByEdges(node, edgeset)
                if s <> None:
                    ax[n] = s
                else:
                    ax[n] = u'![T]:( signal(T,{}) )'.format(node.name)
        return ax

    def getConjectures(self):
        ax = {}
        ax['test'] = u'?[T,X]:(collision(T,X))'
        return ax

    def getNegConjectures(self):
        ax = {}
        #ax['test'] = u'?[T,X]:(collision(T,X))'
        return ax

    def tp(self):
        fmt = u'% Train movement axioms \n{}\n\
            \n% Collision axioms \n{}\n\
            \n% Signaling control \n{}\n\
            \n% Train on input \n{}\n\
            \n% Conjectures \n{}\n\
            \n% Negated conjectures \n{}';
        return fmt.format(
            self.getTPTPfof('axiom', self.getBehaviorAxioms()),
            self.getTPTPfof('axiom', self.getCollisionAxioms()),
            self.getTPTPfof('axiom', self.getSignalingAxioms()),
            self.getTPTPfof('axiom', self.getTrainOnInput()),
            self.getTPTPfof('conjecture', self.getConjectures()),
            self.getTPTPfof('negated_conjecture', self.getNegConjectures()))
