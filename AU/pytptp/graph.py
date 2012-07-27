from pytptp import Constant,Predicate

## Exceptions
class MyException(Exception): pass
class NotImplementedYet (MyException):
    def __init__(self, msg = ''):
        Exception.__init__(self,'Not implemented yet. %s' % msg)
class IllegalArgument(MyException):
    def __init__(self, msg=''):
        Exception.__init__(self, 'Illegal argument. %s' % msg)
class IllegalState(MyException):
    def __init__(self, msg=''):
        Exception.__init__(self, 'Illegal state. %s' % msg)

class Vertex(Constant):
    def __init__(self, name, kind, edgesIn, edgesOut):
        Constant.__init__(self, name)
        if edgesIn is None: edgesIn = []
        if edgesOut is None: edgesOut = []
        if kind is not None and \
           kind in ('DUMMY','INPUT','OUTPUT','DIVERGENT','CONVERGENT','DIRECT'):
            self.kind = kind
        elif len(edgesIn) == 0 and len(edgesOut) == 0:
            self.kind = 'DUMMY'
        elif not len(edgesIn):
            self.kind = 'INPUT'
        elif not len(edgesOut):
            self.kind = 'OUTPUT'
        elif len(edgesIn) == 1 and len(edgesOut) > 1:
            self.kind = 'DIVERGENT'
        elif len(edgesOut) == 1 and len(edgesIn) > 1:
            self.kind = 'CONVERGENT'
        elif len(edgesOut) == 1 and len(edgesIn) == 1:
            self.kind = 'DIRECT'
        self.edgesIn = set()
        self.edgesOut = set()
        for i in edgesIn:
            self.addEdge(i,'in')
        for i in edgesOut:
            self.addEdge(i,'out')
    def addEdge(self,edge,kind):
        if kind == 'in':
            if edge.end is None:
                edge.end = self
                self.edgesIn.add(edge)
            else:
                raise IllegalArgument('Edge must not be adjanced to other node.')
        elif kind == 'out':
            if edge.start is None:
                edge.start = self
                self.edgesOut.add(edge)
            else:
                raise IllegalArgument('Edge must not be adjanced to other node.')
        else:
            raise IllegalArgument('Kind argument must be "in" or "out".')
    def replaceEdge(self,eOld,eNew):
        if eOld in self.edgesIn:
            if eNew.terms[1] is not self: raise IllegalArgument()
            self.edgesIn.remove(eOld)
            self.edgesIn.add(eNew)
        if eOld in self.edgesOut:
            if eNew.terms[0] is not self: raise IllegalArgument()
            self.edgesOut.remove(eOld)
            self.edgesOut.add(eNew)
    def isOutput(self):
        return self.kind == 'OUTPUT'
    def isInput(self):
        return self.kind == 'INPUT'
    def isDivergent(self):
        return self.kind == 'DIVERGENT'
    def isConvergent(self):
        return self.kind == 'CONVERGENT'
    def isDirect(self):
        return self.kind == 'DIRECT'
    def isDummy(self):
        return self.kind == 'DUMMY'
    def dot(self):
        return unicode(self.name)

class Edge:
    def __init__(self, name):
        self.start = None
        self.end = None
        self.name = name
    def dot(self):
        if self.start is None or self.end is None:
            raise IllegalState()
        return u'%s -> %s [label="%s"]' % (self.start.dot(),self.end.dot(),unicode(self.name))
    def replace(self, pred):
        edge = pred(self.start,self.end)
        self.start.replaceEdge(self,edge)
        self.end.replaceEdge(self,edge)
        return edge

class Graph:
    def __init__(self, name, dot):
        import re
        from pytptp import Predicate
        edge = Predicate('edge',2)
        pt = re.compile(r'([a-zA-Z0-9]+)')
        edges = [(Edge(name),src,dst) for name, src, dst in
                    ( (pt.search(e.get_label()).group(1), e.get_source(), e.get_destination()) for e in dot.get_edges() )]
        srcs = dict()
        dsts = dict()
        nodes = set()
        fnc = lambda d,k,e: (d.has_key(k) and d[k]+(e,)) or (e,)
        srcs.update( (src,fnc(srcs,src,e)) for e,src,dst in edges )
        dsts.update( (dst,fnc(dsts,dst,e)) for e,src,dst in edges )
        nodes.update( src for e,src,dst in edges )
        nodes.update( dst for e,src,dst in edges )
        self.name = name
        self.vertices = dict( (n, Vertex(n,None,dsts.get(n),srcs.get(n)) )  for n in nodes )
        self.edges = dict( (e.name,e.replace(edge)) for e,src,dst in edges )

    def dot(self):
        nodes = []
        nodes += (u'%s [shape=hexagon,fillcolor=lightslateblue,style=filled]' % n.dot()
                    for n in self.vertices.values() if n.isConvergent())
        nodes += (u'%s [shape=hexagon,fillcolor=salmon,style=filled]' % n.dot()
                    for n in self.vertices.values() if n.isInput())
        nodes += (u'%s [fillcolor=lightskyblue,style=filled]' % n.dot()
                    for n in self.vertices.values() if n.isDivergent())
        nodes = u';'.join(nodes)

        edges = []
        edges += (u'%s -> %s [label="%s"]' % (e.terms+(n,)) for n,e in self.edges.iteritems())
        edges = u';'.join(edges)

        return u'digraph %(name)s { %(edges)s; %(nodes)s; rankdir=LR; }' % {
            'name': self.name,
            'edges': edges,
            'nodes': nodes
        }

    def tp(self):
        return str(self.getFormulae())
    def uni(self):
        return unicode(self.getFormulae())
    def tex(self):
        from pytptp import tex
        return tex(self.getFormulae())
    def getFormulae(self):
        from pytptp import Predicate,Functor,Variable,all,axiom
        X,Y,T,Z = Variable('X'),Variable('Y'),Variable('T'),Variable('Z')
        # vertices are constants, and edgs are predicates

        at = Predicate('at',3)  # <time>, <edge>, <node>
        go = Predicate('go',1)  # <time>, <edge>
        crit = Predicate('crit',2)  # <time>, <edge>
        signal = Predicate('signal',2) # <time>, <node>

        #print reduce(lambda x,y:x&y, (crit(succ(T),e) for n,e in self.edges.iteritems() ))

        fmt = u'% Train movement axioms \n{0}\n\
            \n% Collision axioms \n{1}\n\
            \n% Signaling control \n{2}\n\
            \n% Train on input \n{3}\n\
            \n% Conjectures \n{4}\n\
            \n% Negated conjectures \n{5}'
        #return  self.ltlAxioms()+ self.graphAxioms()
        return self.ltlAxioms()+self.graphAxioms()

    def ltlAxioms(self):
        from pytptp import Predicate,Functor,Variable,all,axiom
        less = Predicate('less',2)
        succ = Functor('succ',1)
        pred = Functor('pred',1)
        X,Y,T,Z = Variable('X'),Variable('Y'),Variable('T'),Variable('Z')
        from pytptp import all,axiom,annot
        f =  annot('\n\tLinear temporal logic axioms\n')
        f += axiom('less_antisym',all(X,Y)  * ((X==Y) <= (less(X,Y) & less(Y,X)))   )
        f += axiom('less_trans',  all(X,Y,Z)* (less(X,Z) <= (less(X,Y) & less(Y,Z)))  )
        f += axiom('les_total',   all(X,Y)  * (less(X,Y) | less(Y,X)) )
        f += axiom('succ',        all(X)    * (less(X,succ(X)) & all(Y) * (less(Y,X) | less(succ(X),Y))),  )
        f += axiom('succ_neq',    all(X)    * (succ(X) != X) )
        #f += axiom('pred',        all(X)    * ((pred(succ(X)) == X) & (succ(pred(X)) == X)) )
        return f
    def graphAxioms(self):
        from pytptp import axiom,conjecture,annot,all,any,Predicate,Variable,Functor,negConjecture
        path = Predicate('path',2)
        edge = Predicate('edge',2)

        input = Predicate('input',1)
        diverge = Predicate('diverge',1)

        signal = Predicate('signal',2)
        branch = Predicate('branch',3)

        at = Predicate('at',3)
        want = Predicate('want',2)
        flop = Predicate('want',2)
        crit = Predicate('crit',1)
        block = Predicate('block',2)
        succ = Functor('succ',1)
        pred = Functor('pred',1)
        p = Functor('p',2)
        less = Predicate('less',2)
        X,Y,Z,U,V = Variable('X'),Variable('Y'),Variable('Z'),Variable('U'),Variable('V')
        T,T1,T2 = Variable('T'),Variable('T1'),Variable('T2')
        A,B = Variable('A'),Variable('B')
        a1 = self.vertices['a1']
        a2 = self.vertices['a2']
        e2 = self.vertices['e2']
        b = self.vertices['b']
        d = self.vertices['d']
        c = self.vertices['c']
        e1 = self.vertices['e1']
        #d = self.vertices['d']

        posEdges = set(self.edges.values())
        #signal_in = [signal(T,v,u.terms[1]) for v in self.vertices.values() if v.isInput() for u in v.edgesOut ]
        #signal_div = [signal(T,v,u.terms[1]) | ~ signal(T,v,u.terms[1])
        #              for v in self.vertices.values() if v.isDivergent() for u in v.edgesOut ]
        #signal_con = [signal(T,v,u.terms[1]) for v in self.vertices.values() if v.isConvergent() for u in v.edgesOut ]
        #signal_dir = [signal(T,v,u.terms[1]) for v in self.vertices.values() if v.isDirect() for u in v.edgesOut ]

        conj = lambda x,y:x&y
        f =  annot('\n\tGraph axioms\n')
        f += axiom('graph', reduce(lambda x,y:x&y,(((e in posEdges) and e) or ~e for e in (edge(a,b) for a in self.vertices.values() for b in self.vertices.values()) )))
        f += axiom('path_trans', all(X,Y,Z) * ( ( path(X,Z) & path(Z,Y) ) >= path(X,Y) ))
        f += axiom('path', all(X,Y) * ( ( path(X,Y) ) <= edge(X,Y) ))
        f += axiom('input', all(X) * (input(X) == reduce(lambda x,y:x|y, ( X==v for v in self.vertices.values() if v.isInput() ) ) ) )
        #f += axiom('output', all(X) * (output(X) == reduce(lambda x,y:x|y, ( X==v for v in self.vertices.values() if v.isOutput() ) ) ) )
        f += axiom('diverge', all(X) * (diverge(X) == reduce(lambda x,y:x|y, ( X==v for v in self.vertices.values() if v.isDivergent() ) ) ) )

        f += annot('\n\tMovement axioms')
        f += axiom('at', all(T,Y,U)*(
            at(succ(T),Y,U) == (
                (at(T,Y,U) & (~want(T,Y) | (input(Y) & ~signal(T,Y) ))) |
                (any(X) * (
                    edge(X,Y) & at(T,X,U) & want(T,X) & (
                        (input(X) & signal(T,X))|
                        (diverge(X) & branch(T,X,Y))|
                        (~input(X)&~diverge(X))
                    )
                ))
            ))
        )

        f += axiom('crit', all(T) *(
            ( any(X,Y) * (
                at(T,X,U) & (~want(T,X) | (input(Y) & ~signal(T,Y) )) &
                any(Y,V) * (
                    at(T,Y,V) & edge(Y,X) & want(T,Y) &
                    ((input(Y) & signal(T,Y))|(diverge(Y) & branch(T,Y,X))|(~input(Y)&~diverge(Y)))
                )
            )) >= crit(succ(T))
        ) )

        f += annot('\n\tControl axioms')
        #f += axiom('want', all(T,X,U) * (
        #    at(T,X,U) >= (any(T1) * (less(T,T1) & (all(T2) * ( less(T1,T2) & want(T2,X) )) ))
        #   )
        #)
        f += axiom('want', all(T,X,U) * ( at(T,X,U) >= want(T,X) ) )
        #f += axiom('signal', all(T,X) * ( signal(T,X) ))
        #f += axiom('block', all(T,X) * (
        #    (input(X) & ~(any(Y,Z,U) * ( ~input(Y) & at(T,Y,U) & path(Y,Z) & path(X,Z)))) >= ~block(T,X)
        #))
        f += axiom('block', all(T,Z) * ((( input(Z) & (any(X) * ( any(U)*at(T,X,U) & ~input(X) & (Z != X) & ~(any(Y) * (path(X,Y) & path(Y,Z)))) )) >= block(T,Z))))

        f += axiom('signal_a1', all(T) * ( (~block(T,a1) & (any(U) * at(T,a1,U))) >= signal(T,a1) ))
        f += axiom('signal_a2', all(T) * ( (~block(T,a2) & ~(any(U) * at(T,a1,U)) & (any(U) * at(T,a2,U))) >= signal(T,a2) ))
        #f += axiom('signal', all(T,X) * ( block(T,X) == ~ signal(T,X) ))
        f += axiom('branch',
            all(T,Z,Y) * (( diverge(Z) & edge(Z,Y) & any(X,U) * ( at(T,X,U) & (path(X,Z)|(X==Z)) & (path(Y,U)|(Y==U)) ) ) >= branch(T,Z,Y))
        )



        f += annot('\n\tConjectures')
        f += conjecture('c1', all(T) * ( (at(T,a1,e2) & ~block(T,a1) ) >= (any(T1) * ( less(T,T1) & (T != T1) & any(U) * at(T1,e2,U) ) ) ))
        f += conjecture('c2', all(T) * ( (at(T,a2,e2) & ~block(T,a2) & ~(any(U)*at(T,a1,U)) ) >= (any(T1) * ( less(T,T1) & (T != T1) & any(U) * at(T1,e2,U) ) ) ))
        f += conjecture('c3', all(T) * ( any(X,U)*(at(T,X,U) & input(X)) >= ~( any(T1)*(less(T,T1) & crit(T1)) )   ) )
        #f += conjecture('c2', all(T) * ( (at(T,a2,e2) & ~block(T,a2) & ~ (any(U)*at(T,a1,U))) >= (any(T1) * ( less(T,T1) & (T != T1) & any(U) * at(T1,e2,U) ) ) ))

        #f += conjecture('c1', all(T) * ( (at(T,a2,e2) & ~block(T,a2) & ~ (any(U)*at(T,a1,U))) >= (any(T1) * ( less(T,T1) & (T != T1) & signal(T1,a2) ) ) ))
        #f += conjecture('c1', all(T) * ( (at(T,a1,e2) & ~ (any(X,U) * ( (X==a1) &at(T,X,U))) ) >= (any(T1) * ( less(T,T1) & (T != T1) & at(T1,e2,e2)))  ) )
        #f += conjecture('c1', all(T) * ( (at(T,a1,e2) & (all(X,U) * ( (X!=a1) >= ~at(T,X,U))) ) >= signal(T,a1) ) )
        #f += conjecture('c1', all(T) * ( (at(T,a1,e2) & (all(X,U) * ( (X!=a1) >= ~at(T,X,U))) ) >= signal(T,a1) ) )
        #f += conjecture('c1', all(T) * ( (at(T,a1,e2) & (all(X,U) * ( (X==a1)  | ~at(T,X,U))) ) >=
        #                                 (any(T1) * ( less(T,T1) & (T != T1) & any(U) * at(T1,d,U)))  ) )
        #f += conjecture('c1', all(T) * ( at(T,a1,e2) >= branch(T,d,c)  ) )
        #f += conjecture('c1', path(a1,e2))

        #f += axiom('approved_div', all(T) * reduce(conj, signal_div))
        #f += axiom('approved_in', all(T) * reduce(conj, signal_in))
        #f += axiom('approved_con', all(T) * reduce(conj, signal_con))
        #f += axiom('approved_dir', all(T) * reduce(conj, signal_dir))
        #f += axiom('graph', reduce(lambda x,y:x&y,(e for e in self.edges.values())))
        #f += axiom('graph', reduce(lambda x,y:x&y,(((e in posEdges) and e) or ~e for e in (edge(a,b) for a in self.vertices.values() for b in self.vertices.values()) )))
        #f += axiom('path', all(X,Y,Z) * ( path(X,Y) <= ( path(X,Z) & edge(Z,Y) ) ))
        #f += axiom('path_tran', all(X,Y,Z) * ( path(X,Y) <= ( path(X,Z) & path(Z,Y) ) ))
        #f += axiom('path', all(X,Y) * ( path(X,Y) <= edge(X,Y)))

        #f += axiom('input', input(X) == reduce(lambda x,y:x|y, ( X==v for v in self.vertices.values() if v.isInput() ) ) )
        #f += axiom('output', output(X) == reduce(lambda x,y:x|y, ( X==v for v in self.vertices.values() if v.isOutput() ) ) )

        #f += axiom('want', all(T,X,Y) * (signal(T,Y,X) <= want(T,Y,X)) )
        #f += axiom('at', all(T,Y,X,U) * ( at(succ(T),Y,U) == ( ( at(T,X,U) & edge(X,Y) & want(T,X) & signal(T,X) ) | ( at(T,Y,U) & ( ~want(T,Y) | ~signal(T,Y))) ) ) )
        #f += axiom('signal', all('c1', any(T,Y) * (at(succ(T),d,Y) <= at(T,a1,Y)  )  T,Y,X) * ( signal(T,Y,X) ))
        #f += axiom('want', all(T,X) * ( want(T,X)| (~want(T,X) & ( any(T1) * ( less(T,T1) & want(T1,X) ) ) ) )   )
        #f += axiom('want', all(T,X,U) * ( ( ( any(T1) * ( less(T,T1) & want(T1,X) ) ) == (any(Y)*signal(T,X,Y) & at(T,X,U)) ) ) )
        #f += axiom('want', all(T,X,U) * ( ( ( any(T1) * ( less(T,T1) & want(T1,X) ) ) <= (at(T,X,U)) ) ) )
        #f += axiom('want', all(T,X,U) * (want(T,X) <= (at(T,X,U)) ) )
        #for s in signal_in: f += axiom('signal_%s'%(s.terms[1]), all(T) * ( ~want(T,s.terms[1]) <= ~s ) )
        #f += axiom('signal_excl', all(T)* ~reduce(lambda x,y:x&y,(e for e in signal_in)))
        #f += axiom('signal_exist', any(T) * reduce(lambda x,y:x|y,(e for e in signal_in)))
        #f += axiom('signal_always', all(T) * signal(T,a1,b))

        #f += axiom('crit', all(T,X,Y,U,V) * ( crit(T,Y) <= ( at(T,X,U) & at(T,Y,V) & edge(Y,X) & want(T,Y) & ~want(T,X) ) )  )
        #f += axiom('block', all(T,X,Z,U) * ( any(U) * ( (at(T,X,U) & path(X,U) & path(Z,U) & ~ ( any(V) * edge(V,Z) )) >= (block(T,Z)) ) ) )

        #f += axiom('signal1', all(T,X,Y) * ( ~(path(Y,) & edge(X,Y)) >= ~signal(T,X,Y) ))
        #f += axiom('signal_neg', all(T,X) * ( ~ ( any(Y) * edge(X,Y) ) >= ~signal(T,X) ))
        #f += axiom('signal1', all(T,X,Y,Z,U) * ( ~edge(Y,Z) >= ~signal(T,Y,Z) ))
        #f += axiom('signal2', all(T,X,Y,Z,U) * ( ( at(T,X,U) & path(X,Y) & edge(Y,Z) & path(Z,U)) >= signal(T,Y,Z) ))

        #f += axiom('sinal',  )
        #f += negConjecture('c1', all(T) * ( at(T,a1,e1) >= (any(T1,U) * ( less(T,T1) & (T != T1) & at(T1,e1,U)))  ) )
        #f += conjecture('c1', all(T) * ( at(T,a1,e2) >= (any(T1) * ( less(T,T1) & (T != T1) & at(T1,c,e2)))  ) )
        #f += negConjecture('c1', all(T,U) * (   (all(T1) * ( less(T1,T) & (T != T1) & at(T1,e2,U))) <= at(T,a1,U) ) )
        #f += conjecture('c1', all(T,U) * ( (any(T1) * at(T1,e1,U)) <= at(T,a1,U)  )  )
        #f += conjecture('c1', all(T,U) * ( (any(T1) * at(T1,d,U)) <= at(T,b,U)  )  )

        #f += conjecture('c2', all(T,X,U) * ( ( ~ (any(T1,Y) * (less(T,T1) & crit(T1,Y) ))) <= at(T,X,U) )  )
        #f += conjecture('c2', any(T,X,U,V) * ( (any(T1,Y) * ( crit(T1,Y) ) ) <= (at(T,b,U) & at(T,d,V)) )  )

        #f += conjecture('c1', any(X) * (path(a1,e2)))
        #f += conjecture('c1', any(T) * (  )  )
        return f
    def getEnterClause(self, e):
        a = []
        if e.start.kind == 'SIGNAL':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            a.append(self.getCanPassClause(e.start, 0))
            return u'{0} & {1}'.format(*a)
        elif e.start.kind == 'INPUT':
            a.append(self.getIsHereClause(e.start, 0))
            a.append(self.getCanPassClause(e.start, 0))
            return u'{0} & {1}'.format(*a)
        elif e.start.kind == 'DIRECT':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            return u'{0}'.format(*a)
        elif e.start.kind == 'CONVERGENT':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            a.append(self.getCanPassClause(e.start, 0))
            a.append(self.getIsHereClause(e.start.edgesIn[1], 0))
            a.append(self.getCanPassClause(e.start, 0, True))
            return u'({0} & {1}) | ({2} & {3})'.format(*a)
        elif e.start.kind == 'DIVERGENT':
            a.append(self.getIsHereClause(e.start.edgesIn[0], 0))
            if e.start.edgesOut[0] == e:
                a.append(self.getCanPassClause(e.start, 0))
            elif e.start.edgesOut[1] == e:
                a.append(self.getCanPassClause(e.start, 0, True))
            return u'{0} & {1}'.format(*a)
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

        return u'{0} & {1}'.format(*a)

    def getBehaviorAxioms(self):
        ax = {}
        for e in self.edges.values():
            n = u'ishere_{0}'.format(e.name)
            a = []
            a.append(self.getIsHereClause(e, 1))
            a.append(self.getEnterClause(e))
            c = self.getLeaveClause(e)
            if c == None:
                ax[n] = u'![T,X]:( {0} <=> ( {1} ) )'.format(*a)
            else:
                a.append(c)
                ax[n] = u'![T,X]:( {0} <=> ( ({1}) | ({1}) ) )'.format(*a)
        return ax 

    def getCollisionAxioms(self):
        ax = {}
        for e in self.edges.values():
            n = u'collision_{0}'.format(e.name)

            a = []
            a.append(self.getCollisionClause(e, 1))
            a.append(self.getEnterClause(e))
            c = self.getLeaveClause(e,target = u'Y')
            if c == None:
                continue
            else:
                a.append(c)
                ax[n] = u'![T]:(?[X,Y]:( {0} <=> ( ({1}) & ({2}) ) ))'.format(*a)
        return ax
    
    def getTrainOnInput(self):
        ax = {}
        iverticles = []
        overticles = []
        for v in self.vertices.values():
            if v.kind in ['INPUT']:
                iverticles.append(v)
            if v.kind in ['OUTPUT']:
                overticles.append(v)
        s = None
        for v in iverticles:
            c = []
            fmt = []
            fmt2 = []
            for o in overticles:
                c.append(u'ishere_{0}(T,{1})'.format(v.name, o.name))
                fmt.append(u'{0} | ')
            l = len(overticles)
            fmt[l-1] = u'{%d}' % (l-1)
            f =  ''.join(fmt)
            s = f.format(*c)
            n = u'input_{0}'.format(v.name)
            ax[n] = u'?[T]:({0})'.format(s)
            n = u'input_{0}_ex'.format(v.name)
            ax[n] = u'![T,X]:( ishere_{0}(T,X) => (~ ?[Y]:( (X != Y) & ishere_{0}(T,Y) ) ) )'.format(v.name)

        #ax[u'zzz0'] = u'ishere(t,06,o1) & ishere(t,07,o3) & ishere(t,11,o3) '
        s = None
        for v in self.edges.values():
            if s == None:
                s = u'~ ?[Y]:ishere_{0}(T,Y)'.format(v.name)
            else:
                s = u'{0} & ~ ?[Y]:ishere_{1}(T,Y)'.format(s,v.name)
        ax[u'empty'] = u'?[T]:({0})'.format(s)
        return ax


    def traverse(self, edge, nodeset=None, edgeset=None, back=False, targets=('INPUT')):
        node = (back and [edge.start] or [edge.end])[0]
        if node.kind in targets:
            if nodeset is not None:
                nodeset.add(node)
            if edgeset is not None:
                edgeset.add(edge)
        else:
            edges = (back and [node.edgesIn] or [node.edgesOut])[0]
            for e in edges:
                es = set()
                self.traverse(e, nodeset, edgeset=es, back=back,targets=targets)
                if len(es) > 0:
                    if edgeset is not None:
                        edgeset.add(edge)
                        edgeset |= es

    def getSignalingByEdges(self, node, edges):
        s = None
        q = None
        for e in edges:
            if s is None:
                s = u'![Y]:ishere_{0}(T,Y)'.format(e.name)
            else:
                s = u'{0} | ![Y]:ishere_{1}(T,Y)'.format(s,e.name)
        if s is not None:
            return u'![T]:( ({0}) => ~signal_{1}(T) )'.format(s,node.name)

    def getSignalingByNodes(self, node, nodes):
        s = None
        for n in nodes:
            if s is None:
                s = u'~signal_{0}(T)'.format(n.name)
            else:
                s = u'{0} & ~signal_{1}(T)'.format(s,n.name)
        if s is not None:
            return u'![T]:( signal_{0}(T) => ({1}) )'.format(node.name,s)

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
        return nodeset, edgeset

    def getSignalingAxioms(self):
        ax = {}
        for node in self.vertices.values():
            if node.kind in ['CONVERGENT']:
                s = u'![T,X]:((ishere_{0}(T,X) => signal_{2}(T)) & ((~ishere_{0}(T,X) & ishere_{1}(T,X)) => ~signal_{2}(T)))'.format(
                        node.edgesIn[0].name, node.edgesIn[1].name, node.name)
                n = u'signal_{0}'.format(node.name)
                ax[n] = s
            elif node.kind in ['DIVERGENT']:
                nodeset0 = set()
                nodeset1 = set()
                self.traverse(node.edgesOut[0], nodeset=nodeset0, targets=['OUTPUT'])
                self.traverse(node.edgesOut[1], nodeset=nodeset1, targets=['OUTPUT'])
                same = nodeset0 & nodeset1
                diff0 = nodeset0 - nodeset1
                diff1 = nodeset1 - nodeset0
                for n in same | diff0: 
                    s = u'![T]:(ishere_{0}(T,{1}) => signal_{2}(T))'.format(node.edgesIn[0].name, n.name, node.name)
                    n = u'signal_{0}_{1}'.format(node.name,n.name)
                    ax[n] = s
                for n in diff1:
                    s = u'![T]:(ishere_{0}(T,{1}) => ~signal_{2}(T))'.format(node.edgesIn[0].name, n.name, node.name)
                    n = u'signal_{0}_{1}'.format(node.name,n.name)
                    ax[n] = s
            elif node.kind in ['INPUT','SIGNAL']:
                (nodeset, edgeset) = self.getSubgraph(node)
                n = u'signal_{0}_exclusive'.format(node.name)
                s = self.getSignalingByNodes(node, nodeset)
                if s is not None:
                    ax[n] = s
                n = u'signal_{0}'.format(node.name)
                s = self.getSignalingByEdges(node, edgeset)
                if s is not None:
                    ax[n] = s
                else:
                    ax[n] = u'![T]:( signal_{0}(T) )'.format(node.name)
        return ax

    def getConjectures(self):
        ax = {}
        #ax['test'] = u'?[T,X]:(collision(T,X))'
        #ax['test'] = u'![T,X]:(~collision(T,X))'
        return ax

    def getNegConjectures(self):
        ax = {}
        #ax['test'] = u'?[T,X]:(collision(T,X))'
        #ax['test'] = u'![T,X]:(~collision(T,X))'
        return ax

