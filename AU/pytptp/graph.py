# coding=utf-8
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

class Inc:
    def __init__(self, i, prefix):
        self.i = i
        self.prefix = prefix
    def __pos__(self):
        self.i += 1
        return '%s%d' %(self.prefix,self.i)

class Wrapper:
    def __init__(self,d):
        if isinstance(d,dict):
            self.__dict__.update(d)
        if isinstance(d,list) or isinstance(d,tuple):
            self.__dict__.update((i,None) for i in d)

class Graph:
    def __init__(self, name, dot):
        import re
        from pytptp import Predicate,Variable,Functor
        edge = Predicate('edge',2)
        i = Inc(0,'')
        if isinstance(dot,str):
            (name, body), = re.findall(r'digraph\s+([\w_]+)\s*\{\s*(.*)\s*\}', dot, re.DOTALL)
            edges = [(Edge(name),src,dst) for name, src, dst in ( (+i, src,dst) for src,dst in re.findall(r'(\w+)\s*->\s*(\w+)\s*',body, re.DOTALL) )]
        else:
            pt = re.compile(r'([a-zA-Z0-9]+)')
            #print [(e.get_source(), e.get_destination()) for e in dot.get_edges()]
            edges = [(Edge(name),src,dst) for name, src, dst in
                        ( (((e.get_label() is None and +i) or pt.search(e.get_label()).group(1)), e.get_source(), e.get_destination()) for e in dot.get_edges() )]
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

        w = Wrapper([
                'edge','input','output', 'flop',
                'diverge','signal','branch', 'path',
                'at','want','crit','succ','less',
                'X','Y','Z','U','V','T','T1','T2','A','B'
            ])
        w.path = Predicate('path',2)
        w.edge = edge
        w.input = Predicate('input',1)
        w.output = Predicate('output',1)
        w.diverge = Predicate('diverge',1)
        w.signal = Predicate('signal',2)
        w.branch = Predicate('branch',3)
        w.at = Predicate('at',3)
        w.want = Predicate('want',2)
        w.flop = Predicate('flop',2)
        w.crit = Predicate('crit',1)
        w.block = Predicate('block',2)
        w.succ = Functor('succ',1)
        w.pred = Functor('pred',1)
        w.less = Predicate('less',2)
        w.X,w.Y,w.Z,w.U,w.V = Variable('X'),Variable('Y'),Variable('Z'),Variable('U'),Variable('V')
        w.T,w.T1,w.T2 = Variable('T'),Variable('T1'),Variable('T2')
        w.A,w.B = Variable('A'),Variable('B')
        self.symbols = w

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

    def writef(self,out,fn,data):
        f = open('%s/%s.tpt'%(out,fn),'w')
        try: f.write(str(data));
        finally: f.close();
        return data
    def functions(self):
        return (self.ltlAxioms,self.ltlAxiomsNoModel,self.graphAxioms,self.controlAxioms,self.controlAxiomsAsap,self.controlAxiomsAsapNoClock,self.test1Conjectures,self.test2Conjectures,self.test3Conjectures)
    def functions2(self):
        return (self.ltlAxioms,self.graphAxioms,self.controlAxioms,self.test1Conjectures,self.test2Conjectures,self.test3Conjectures)
    def tp(self):
        out = 'out/'
        for fnc in self.functions():
            fn,data = fnc()
            self.writef(out,fn,data)
        return str(self.getFormulae())
    def uni(self):
        return unicode(self.getFormulae())
    def tex(self):
        from pytptp import tex
        return tex(self.getFormulae())
    def getFormulae(self):
        from pytptp import tex
        f = None
        for fnc in self.functions2():
            fn,data=fnc()
            if f is None: f = data
            else: f+= data
        return f
    def ltlAxioms(self):
        from pytptp import all,axiom,annot,annotate
        s  = self.symbols
        less,succ,pred,X,Y,T,Z =  s.less,s.succ,s.pred,s.X,s.Y,s.T,s.Z
        f =  annot('')
        f +=  annot('Linear temporal logic axioms')
        f += axiom('less_antisym',all(X,Y)  * ((X==Y) <= (less(X,Y) & less(Y,X)))  )
        f += axiom('less_trans',  all(X,Y,Z)* (less(X,Z) <= (less(X,Y) & less(Y,Z)))  )
        f += axiom('less_total',  all(X,Y)  * (less(X,Y) | less(Y,X)) )
        f += axiom('succ',        all(X)    * (less(X,succ(X)) & all(Y) * (less(Y,X) | less(succ(X),Y))),  )
        #f += axiom('succ_neq',    all(X)    * (succ(X) != X) )
        #f += axiom('pred',        all(X)    * ((pred(succ(X)) == X) & (succ(pred(X)) == X)) )
        return 'ltl',f
    def ltlAxiomsNoModel(self):
        from pytptp import all,axiom,annot,annotate
        s  = self.symbols
        less,succ,pred,X,Y,T,Z =  s.less,s.succ,s.pred,s.X,s.Y,s.T,s.Z
        f =  annot('')
        f +=  annot('Linear temporal logic axioms')
        f += axiom('less_antisym',all(X,Y)  * ((X==Y) <= (less(X,Y) & less(Y,X)))  )
        f += axiom('less_trans',  all(X,Y,Z)* (less(X,Z) <= (less(X,Y) & less(Y,Z)))  )
        f += axiom('less_total',  all(X,Y)  * (less(X,Y) | less(Y,X)) )
        f += axiom('succ',        all(X)    * (less(X,succ(X)) & all(Y) * (less(Y,X) | less(succ(X),Y))),  )
        f += axiom('succ_neq',    all(X)    * (succ(X) != X) )
        #f += axiom('pred',        all(X)    * ((pred(succ(X)) == X) & (succ(pred(X)) == X)) )
        return 'ltl_full',f
    def graphAxioms(self):
        from pytptp import axiom,annot,all,any
        s  = self.symbols
        less,succ,pred,X,Y,T,Z,U,V =  s.less,s.succ,s.pred,s.X,s.Y,s.T,s.Z,s.U,s.V
        path,edge,input,output,diverge,signal,branch,at,want,crit,block,flop = s.path,s.edge,s.input,s.output,s.diverge,s.signal,s.branch,s.at,s.want,s.crit,s.block,s.flop
        T,T1,T2,A,B = s.T,s.T1,s.T2,s.A,s.B

        posEdges = set(self.edges.values())
        inputNodes = [X==v for v in self.vertices.values() if v.isInput()]
        outputNodes = [X==v for v in self.vertices.values() if v.isOutput()]
        divergentNodes = [X==v for v in self.vertices.values() if v.isDivergent()]

        f =  annot('')

        f +=  annot('*** Axiomy nadrazi ***')
        f +=  annot('Graf')
        f += axiom('graph', reduce(lambda x,y:x&y,(((e in posEdges) and e) or ~e for e in (edge(a,b) for a in self.vertices.values() for b in self.vertices.values()) )))
        f +=  annot('Cesty v grafu')
        f += axiom('path_trans', all(X,Y,Z) * ( ( path(X,Z) & path(Z,Y) ) >= path(X,Y) ))
        f += axiom('path', all(X,Y) * ( ( path(X,Y) ) <= edge(X,Y) ))
        f +=  annot('Enumerace vstupu, vystupu a divergentnich spoju')
        if len(inputNodes)>0:
            f += axiom('input', all(X) * (input(X) == reduce(lambda x,y:x|y, inputNodes ) ) )
        else:
            f +=  axiom('diverge', all(X) * (~input(X) ) )
        if len(outputNodes)>0:
            f += axiom('output', all(X) * (output(X) == reduce(lambda x,y:x|y, outputNodes ) ) )
        else:
            f +=  axiom('diverge', all(X) * (~output(X) ) )
        if len(divergentNodes)>0:
            f += axiom('diverge', all(X) * (diverge(X) == reduce(lambda x,y:x|y, divergentNodes ) ) )
        else:
            f +=  axiom('diverge', all(X) * (~diverge(X) ) )
        f += annot('*** Pohyb vlaku ***')
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

        f += annot('"Vule" strojvudce')
        #f += axiom('want', all(T,X,U) * ( at(T,X,U) >= (input(X) & want(T,X)) | (any(T1) * (less(T,T1) & (all(T2) * (less(T1,T2) &  want(T2,X))) )) ) )
        f += axiom('want1', all(T,X,U) * ( (at(T,X,U)&input(X)&signal(T,X)) >= want(T,X) ) )
        f += axiom('want2', all(T,X,U) * ( (at(T,X,U)&~input(X)) >= (any(T1) * (less(T,T1) & want(T1,X) )) ) )

        f += annot('*** Kriticke stavy ***')
        f += annot('Srazka dvou nebo vice vlaku')
        f += axiom('crit1', all(T) *(
            ( any(X,Y) * (
                at(T,X,U) & (~want(T,X) | (input(Y) & ~signal(T,Y) )) &
                any(Y,V) * (
                    at(T,Y,V) & edge(Y,X) & want(T,Y) &
                    ((input(Y) & signal(T,Y))|(diverge(Y) & branch(T,Y,X))|(~input(Y)&~diverge(Y)))
                    )
                )) >= crit(succ(T))
            ) )

        f += annot('Zmena stavu vyhyby po prijezdu vlaku')
        f += axiom('crit2', all(T) * ( ( any(X,U) * ( diverge(X) & at(T,X,U) & (any(Y,Z) * ((Z!=Y) & branch(T,X,Y) & branch(succ(T),X,Z) ) ) ) ) >= crit(succ(T))) )

        f += annot('Uviznuti vlaku na vstupu')
        f += axiom('crit3', all(T)*( crit(T) <= any(X,U) * ( input(X) & at(T,X,U) & ~ (any(T1) * ( less(T,T1) & signal(T1,X) ) ) ) ) )


        return 'graph',f

    def controlAxioms(self):
        from pytptp import axiom,annot,all,any
        s  = self.symbols
        less,succ,pred,X,Y,T,Z,U,V =  s.less,s.succ,s.pred,s.X,s.Y,s.T,s.Z,s.U,s.V
        path,edge,input,output,diverge,signal,branch,at,want,crit,block,flop = s.path,s.edge,s.input,s.output,s.diverge,s.signal,s.branch,s.at,s.want,s.crit,s.block,s.flop
        T,T1,T2,A,B = s.T,s.T1,s.T2,s.A,s.B

        inNodes = [v  for v in self.vertices.values() if v.isInput()]

        f =  annot('')
        f += annot('Axiomy rizeni')

        f += annot('Blokace vstupu jinym vlakem')
        f += axiom('block', all(T,Z) * ((( input(Z) & (any(X,U) * ( at(T,X,U) & ~input(X) & (Z != X) & ~(any(Y) * (path(X,Y) & path(Y,Z)))) )) >= block(T,Z))))

        f += annot('Casovac - je povolen pouze jeden vstup')
        f += axiom('clock',all(T) * reduce(lambda x,y:x|y, ( reduce(lambda x,y:x&y,(~flop(T,u) for u in inNodes if u is not v),flop(T,v)) for v in inNodes) ))

        f += annot('Casovac - posunuti signalu na dalsi vstup')
        if len(inNodes) > 1:
            a = inNodes[1:]+inNodes[:1]
            k = Inc(0,'clock_')
            #f +=  [ axiom(
            #    +k, all(T) * ( (reduce(lambda x,y:x&y,(~flop(succ(T),u) for u in inNodes if u is not j),flop(succ(T),j))) <= (flop(T,i)) )
            # for i,j in ( (inNodes[i],a[i]) for i in range(len(inNodes)) ) ]

            f +=  [ axiom( +k, all(T) * ( flop(succ(T),j) <= (flop(T,i)) ) ) for i,j in ( (inNodes[i],a[i]) for i in range(len(inNodes)) ) ]


        f += annot('Povoleni k vstupu ')
        f += axiom('signal', all(T,X) *  ( input(X) & flop(T,X) & ~block(T,X) ) >= signal(T,X) )

        f += annot('Vyhybka')
        f += axiom('branch',
            all(T,Z,Y) * (( diverge(Z) & edge(Z,Y) & any(X,U) * (output(U) & at(T,X,U) & (path(X,Z)|(X==Z)) & (path(Y,U)|(Y==U)) ) ) >= branch(T,Z,Y))
        )
        return 'control',f

    def controlAxiomsAsap(self):
        from pytptp import axiom,annot,all,any
        s  = self.symbols
        less,succ,pred,X,Y,T,Z,U,V =  s.less,s.succ,s.pred,s.X,s.Y,s.T,s.Z,s.U,s.V
        path,edge,input,output,diverge,signal,branch,at,want,crit,block,flop = s.path,s.edge,s.input,s.output,s.diverge,s.signal,s.branch,s.at,s.want,s.crit,s.block,s.flop
        T,T1,T2,A,B = s.T,s.T1,s.T2,s.A,s.B

        inNodes = [v  for v in self.vertices.values() if v.isInput()]

        f =  annot('')
        f += annot('Axiomy rizeni')

        f += annot('Formalizace neni sporna i kdyz vyjede hned jak to je mozne')
        f += axiom('want2', all(T,X,U) * ((at(T,X,U) & ~input(X) ) >= want(T,X)) )

        f += annot('Blokace vstupu jinym vlakem')
        f += axiom('block', all(T,Z) * ((( input(Z) & (any(X) * ( any(U)*at(T,X,U) & ~input(X) & (Z != X) & ~(any(Y) * (path(X,Y) & path(Y,Z)))) )) >= block(T,Z))))

        f += annot('Casovac - je povolen pouze jeden vstup')
        f += axiom('clock',all(T) * reduce(lambda x,y:x|y, ( reduce(lambda x,y:x&y,(~flop(T,u) for u in inNodes if u is not v),flop(T,v)) for v in inNodes) ))

        f += annot('Casovac - posunuti signalu na dalsi vstup')
        if len(inNodes) > 1:
            a = inNodes[1:]+inNodes[:1]
            k = Inc(0,'clock_')
            #f +=  [ axiom(
            #    +k, all(T) * ( (reduce(lambda x,y:x&y,(~flop(succ(T),u) for u in inNodes if u is not j),flop(succ(T),j))) <= (flop(T,i)) )
            # for i,j in ( (inNodes[i],a[i]) for i in range(len(inNodes)) ) ]

            f +=  [ axiom( +k, all(T) * ( flop(succ(T),j) <= (flop(T,i)) ) ) for i,j in ( (inNodes[i],a[i]) for i in range(len(inNodes)) ) ]


        f += annot('Povoleni k vstupu ')
        f += axiom('signal', all(T,X) *  ( input(X) & flop(T,X) & ~block(T,X) ) >= signal(T,X) )

        f += annot('Vyhybka')
        f += axiom('branch',
            all(T,Z,Y) * (( diverge(Z) & edge(Z,Y) & any(X,U) * ( at(T,X,U) & (path(X,Z)|(X==Z)) & (path(Y,U)|(Y==U)) ) ) >= branch(T,Z,Y))
        )
        return 'control_asap', f
    def controlAxiomsAsapNoClock(self):
        from pytptp import axiom,annot,all,any
        s  = self.symbols
        less,succ,pred,X,Y,T,Z,U,V =  s.less,s.succ,s.pred,s.X,s.Y,s.T,s.Z,s.U,s.V
        path,edge,input,output,diverge,signal,branch,at,want,crit,block,flop = s.path,s.edge,s.input,s.output,s.diverge,s.signal,s.branch,s.at,s.want,s.crit,s.block,s.flop
        T,T1,T2,A,B = s.T,s.T1,s.T2,s.A,s.B

        inNodes = [v  for v in self.vertices.values() if v.isInput()]

        f =  annot('')
        f += annot('Axiomy rizeni')

        f += annot('Formalizace neni sporna i kdyz vyjede hned jak to je mozne')
        f += axiom('want2', all(T,X,U) * ((at(T,X,U) & ~input(X) ) >= want(T,X)) )

        f += annot('Blokace vstupu jinym vlakem')
        f += axiom('block', all(T,Z) * ((( input(Z) & (any(X) * ( any(U)*at(T,X,U) & ~input(X) & (Z != X) & ~(any(Y) * (path(X,Y) & path(Y,Z)))) )) >= block(T,Z))))

        f += annot('Casovac - je povolen pouze jeden vstup')
        f += axiom('clock',all(T) * reduce(lambda x,y:x|y, ( reduce(lambda x,y:x&y,(~flop(T,u) for u in inNodes if u is not v),flop(T,v)) for v in inNodes) ))

        if len(inNodes) > 1:
            a = inNodes[1:]+inNodes[:1]
            k = Inc(0,'clock_')
            f += annot('Casovac - posunuti signalu na dalsi vstup')
            #f +=  [ axiom(
            #    +k, all(T) * ( (reduce(lambda x,y:x&y,(~flop(succ(T),u) for u in inNodes if u is not j),flop(succ(T),j))) <= (flop(T,i)) )
            # for i,j in ( (inNodes[i],a[i]) for i in range(len(inNodes)) ) ]

            #f +=  [ axiom( +k, all(T) * ( flop(succ(T),j) <= (flop(T,i)) ) ) for i,j in ( (inNodes[i],a[i]) for i in range(len(inNodes)) ) ]

        f += annot('Povoleni k vstupu ')
        f += axiom('signal', all(T,X) *  ( input(X) & flop(T,X) & ~block(T,X) ) >= signal(T,X) )

        f += annot('Vyhybka')
        f += axiom('branch',
            all(T,Z,Y) * (( diverge(Z) & edge(Z,Y) & any(X,U) * ( at(T,X,U) & (path(X,Z)|(X==Z)) & (path(Y,U)|(Y==U)) ) ) >= branch(T,Z,Y))
        )
        return 'control_noclock',f

    def test1Conjectures(self):
        from pytptp import conjecture,annot,all,any
        s  = self.symbols
        less,succ,pred,X,Y,T,Z,U,V =  s.less,s.succ,s.pred,s.X,s.Y,s.T,s.Z,s.U,s.V
        path,edge,input,output,diverge,signal,branch,at,want,crit,block,flop = s.path,s.edge,s.input,s.output,s.diverge,s.signal,s.branch,s.at,s.want,s.crit,s.block,s.flop
        T,T1,T2,A,B = s.T,s.T1,s.T2,s.A,s.B

        f =  annot('')
        f += annot('Test 1')
        f += annot('Vlak sa vzdy dostane zo vstupu (X) na definovany vystup (U)')
        #f += conjecture('t1', all(T,X,U) * (( input(X) & output(U) & at(T,X,U) & (all(Y) * (input(Y) | ~ (any(V) * ( at(T,Y,V) )))) ) >=
        #                                    (any(T1) * ( less(T,T1) &  at(T1,U,U) ) ) ))
        f += conjecture('t1', all(T,X,U) * (( input(X) & output(U) & path(X,U) & at(T,X,U)  ) >= (any(T1) * ( less(T,T1) &  at(T1,U,U) ) ) ))
        return 't1',f


    def test2Conjectures(self):
        from pytptp import conjecture,annot,all,any
        s  = self.symbols
        less,succ,pred,X,Y,T,Z,U,V =  s.less,s.succ,s.pred,s.X,s.Y,s.T,s.Z,s.U,s.V
        path,edge,input,output,diverge,signal,branch,at,want,crit,block,flop = s.path,s.edge,s.input,s.output,s.diverge,s.signal,s.branch,s.at,s.want,s.crit,s.block,s.flop
        T,T1,T2,A,B = s.T,s.T1,s.T2,s.A,s.B

        f =  annot('')
        f += annot('Test 2')
        f += annot('Nenastane kriticky stav')
        f += conjecture('t2', all(T) * ( all(X,U)*(at(T,X,U) & input(X) & output(U)) >= ~( any(T1)*(less(T,T1) & crit(T1)) )   ) )
        return 't2',f

    def test3Conjectures(self):
        from pytptp import conjecture,annot,all,any
        s  = self.symbols
        less,succ,pred,X,Y,T,Z,U,V =  s.less,s.succ,s.pred,s.X,s.Y,s.T,s.Z,s.U,s.V
        path,edge,input,output,diverge,signal,branch,at,want,crit,block,flop = s.path,s.edge,s.input,s.output,s.diverge,s.signal,s.branch,s.at,s.want,s.crit,s.block,s.flop
        T,T1,T2,A,B = s.T,s.T1,s.T2,s.A,s.B

        f =  annot('')
        f += annot('Test 3')
        f += annot('Tento test funguje len pre nadrazie s 1 vstupom - flop je potom stale v platnosti')
        f += conjecture('t3', all(T,X) * ( (input(X) & any(U,V) * (output(U) & output(V) & at(T,X,U) & at(T,V,V) & path(X,V))) >= (signal(succ(T),X)) ))
        #f += conjecture('t3', all(T,X) * ( (input(X) & any(U,V) * (output(U) & output(V) & at(T,X,U) & at(T,V,V) & path(X,V))) >= (any(T1) * (less(T,T1) & signal(T1,X))) ))
        #f += conjecture('t3', all(T,X) * ( (input(X) & any(U,V) * (output(U) & output(V) & at(T,X,U) & at(T,V,V) & path(X,V) & ~ (any(Y,Z) * (at(T,Y,Z) & (X!=Y)& (V!=Y))))) >=( signal(succ(T),X) )  ))

        #f += conjecture('t3', all(T) * ( any(X) * ( (any(U,V)*(at(T,X,U) & input(X) & output(U) & at(T,V,U) & output(V) & block(T,X) & ~ (any(Y,Z) * (~input(Y) & ~output(Y) & at(T,Y,Z) ) ) )) >= ( signal(succ(T),X) )   ) )  )

        return 't3',f
