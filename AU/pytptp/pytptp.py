__author__ = 'Peter Boraros'
__email__ = 'pborky@pborky.sk'

def isiterable(something):
    from collections import Iterable
    return isinstance(something,Iterable)

## Exceptions
class NotImplementedYet (Exception):
    def __init__(self, msg = ''):
        Exception.__init__(self,'Not implemented yet. %s' % msg)
class IllegalArgument(TypeError):
    def __init__(self, msg=''):
        TypeError.__init__(self, 'Illegal argument. %s' % msg)

## Input checks
class Checks:
    @staticmethod
    def checkOperands(op,cls, fail=True):
        if isiterable(cls):
            for c in cls:
                if not Checks.checkOperands(op,c,fail=False): return False
        elif isiterable(op):
            for o in op:
                if not Checks.checkOperands(o,cls,fail=False): return False
        else:
            if not isinstance(op,cls):
                if not fail: return False
                raise IllegalArgument('Unsupported operand type: \'%s\'. Expecting \'%s\'' % (op.__class__,cls))
    @staticmethod
    def checkUpperWord(data):
        if not isinstance(data,str):
            raise IllegalArgument('Expecting string.')
        import re
        if not re.match(r'[A-Z][a-zA-Z0-9_]*', data):
            raise IllegalArgument('Must start with uppercase character and contain only alfanumerics and underscore (_).')
    @staticmethod
    def checkAtomicWord(data):
        if not isinstance(data,str):
            raise IllegalArgument('Expecting string.')
        import re
    
        if not re.match(r'[a-z][a-zA-Z0-9_]*', data) and \
           not re.match(r'\'[\40-\46\50-\133\135-\176]+\'', data):
            raise IllegalArgument('Must be single quoted or start with lowercase character and contain only alfanumerics and underscore (_).')
    @staticmethod
    def checkArity(arity):
        if arity < 0:
            raise IllegalArgument('Arity must be > 0.')
    @staticmethod    
    def checkSameArity(arity,args):
        if len(args) != arity:
            raise IllegalArgument('Must be same arity (= %d) as defined.' % arity)
    @staticmethod
    def checkArgs(args):
        Checks.checkOperands(args, Term)
    @staticmethod
    def checkNameOrForm(name,form):
        if name is None:
            if form is None:
                raise IllegalArgument('Name is not provided.')
            if isiterable(form):
                for f in form: Checks.checkOperands(f,Formula)
            else: Checks.checkOperands(form,Formula)
    @staticmethod
    def checkCompoudArity(inst,args):
        Checks.checkOperands(inst, Compoud)
        Checks.checkSameArity(inst.arity, args)
    @staticmethod
    def checkIfFormula(form):
        Checks.checkOperands(form, Formula)
    @staticmethod
    def checkIfFormulas(form):
        Checks.checkOperands(form,(Formula,FOLFormula))
    @staticmethod
    def checkVars(vars):
        Checks.checkOperands(vars,Variable)
    @staticmethod
    def checkAnnontation(annot):
        import re
        if re.search(r'(?:[/][*]|[*][/])',annot):
            raise IllegalArgument('Annotation cannot containt \'/*\' or \'*/\'.')
    @staticmethod
    def checkIfAnnotation(annot):
        if not isinstance(annot,Annotation):
            raise IllegalArgument('Unsupported operand type: \'%s\'. Expecting \'%s\'' % (annot.__class__,Annotation))
    @staticmethod
    def checkUpperWordOrInteger(thing):
        if not isinstance(thing,str):
            if not isinstance(thing,int):
                raise IllegalArgument('Expecting string or integer.')
            else:
                try: int(thing)
                except ValueError:
                    import re
                    if not re.match(r'[A-Z][a-zA-Z0-9_]*', thing):
                        raise IllegalArgument('Expecting string or integer.')
    @staticmethod
    def checkPredicate(pred):
        Checks.checkOperands(pred,Predicate)
    @staticmethod
    def checkFunctor(func):
        Checks.checkOperands(func,Functor)

## Classes
class Base:
    def __init__(self,name):
        self.name = name
    def __repr__(self):
        return '<TPTP `%s`>'%str(self)
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unicode(self.name)
    def __tex__(self):
        return tex(self.name)
    def __hash__(self):
        return hash((self.__class__,self.name))
class FOLFormula(Base):
    def __init__(self,name,role,form=None):
        Base.__init__(self,name)
        Checks.checkUpperWordOrInteger(name)
        Checks.checkAtomicWord(role)
        self.role = role
        if form is not None:
            Checks.checkIfFormulas(form)
            if isinstance(form,FOLFormula) or isinstance(form,Annotation): self.formulaList = [form]
            else: self.formulaList = [(name,role,form)]
        else:
            self.formulaList = []
    def __repr__(self):
        if not self.formulaList:
            return '<FOLFormula `None`>'
        else:
            elipsis = ''
            f = self.formulaList
            if len(f) > 1: elipsis = ' ...'
            f = self.format(f[0]); f = f.split('\n')
            if len(f) > 1: elipsis = ' ...'
            f = f[0]
            return '<FOLFormula `%s%s`>' % (f,elipsis)
    def __unicode__(self):
        return u'\n'.join( self.format(f,unicode) for f in self.formulaList )
    def __str__(self):
        return '\n'.join( self.format(f) for f in self.formulaList )
    def __tex__(self):
        result = []
        for f in self.formulaList:
            result += self.format(f,tex)
        return result
    def __add__(self, form):
        Checks.checkIfFormulas(form)
        if isiterable(form):
            f = None
            for ff in form:
                if f is None: f = self+ff
                else: f += ff
            return f
        if form.formulaList:
            f = FOLFormula(form.name, form.role)
        else:
            f = FOLFormula(self.name, self.role)
        if self.formulaList:
            f.formulaList.append(self)
        if isinstance(form,FOLFormula):
            if form.formulaList:
                f.formulaList.append(form)
        elif isinstance(form,Annotation):
            f.formulaList.append(form)
        else:
            f.formulaList.append((self.name,self.role,form))
        return f
    def format(self,form,uni=str):
        if isinstance(form,FOLFormula) or isinstance(form,Annotation):
            return uni(form)
        else:
            if uni is tex: return [u'%s' % uni(form[2])]
            elif uni is unicode: return u'> %s' % uni(form[2])
            else: return 'fof( %s, %s,\n\t%s\n).' % tuple(uni(f) for f in form)
class Annotation(FOLFormula):
    def __init__(self, annotation):
        FOLFormula.__init__(self, 'noname', 'annot')
        Checks.checkAnnontation(annotation)
        self.annot = annotation
    def __str__(self):
        return '/* %s */' % self.annot
    def __unicode__(self):
        return u'/* %s */' % self.annot
    def __tex__(self):
        return u'/* %s */' % tex(self.annot)

class Compoud(Base):
    def __init__(self, name, arity):
        Base.__init__(self, self.getSingleQuotedOrAtomicWord(name))
        Checks.checkAtomicWord(self.name)
        Checks.checkArity(arity)
        self.arity = arity
        # to reuse instances
        self.instances = {}
    def __str__(self):
        return '%s/%d' % (self.name,self.arity)
    def __unicode__(self):
        return u'%s/%d' % (self.name,self.arity)
    def __tex__(self):
        return u'%s/%d' % (tex(self.name),tex(self.arity))
    def __hash__(self):
        return hash((Base.__hash__(self),self.arity))
    def getInstance(self,args):
        raise NotImplementedYet('To be implemented in subclasses.')
    def getSingleQuotedOrAtomicWord(self,word):
        try: Checks.checkAtomicWord(word)
        except IllegalArgument:
            import re
            if not re.match(r"'.*'", word):
                return "'%s'"% word
        return word
    def __call__(self, *args, **kwargs):
        args = tuple(args)
        if args in self.instances:
            return self.instances[args]
        else:
            inst = self.getInstance(args)
            self.instances[args] = inst
            return inst
class Predicate(Compoud):
    def __init__(self, name, arity):
        Compoud.__init__(self, name, arity)
    def getInstance(self,args):
        return PredicateInstance(self,args)
class Functor(Compoud):
    def __init__(self, name, arity):
        Compoud.__init__(self, name, arity)
    def getInstance(self,args):
        return FunctorInstance(self,args)

class Formula(Base):
    def __init__(self, name, form = None):
        Base.__init__(self, name)
        Checks.checkNameOrForm(name, form)
        if isiterable(form):
            self.formulas = tuple(form)
            self.name = form[0].name
        elif form is not None:
            self.formulas = (form,)
        if name is not None:
            self.name = name
    def __invert__(self):
        return Not(self)
    def __and__(self, other):
        Checks.checkOperands(other,Formula)
        return And(self,other)
    def __or__(self, other):
        Checks.checkOperands(other,Formula)
        return Or(self,other)
    def __le__(self, other):
        Checks.checkOperands(other,Formula)
        return Implication(other,self)
    def __ge__(self, other):
        Checks.checkOperands(other,Formula)
        return Implication(self,other)
    def __le__(self, other):
        Checks.checkOperands(other,Formula)
        return Implication(other,self)
    def __eq__(self, other):
        Checks.checkOperands(other,Formula)
        return Equivalence(self,other)
    def __ne__(self, other):
        Checks.checkOperands(other,Formula)
        return Inequivalence(self,other)
    def __mod__(self, vars):
        Checks.checkOperands(vars,Variable)
        return Existential(vars, self)
    def __div__(self, vars):
        Checks.checkOperands(vars,Variable)
        return Universal(vars, self)

class AnnotatedFormula(Formula):
    def __init__(self, form, annotation):
        Formula.__init__(self, None, form)
        Checks.checkIfFormulas(form)
        Checks.checkIfAnnotation(annotation)
        self.form = form
        self.annot = annotation
    def __str__(self):
        return '/* %s */ %s' % (self.annot,self.form)
    def __unicode__(self):
        return u'/* %s */ %s' % (self.annot,self.form)
    def __tex__(self):
        return u'/* %s */ %s' % (tex(self.annot),tex(self.form))
class Atom(Formula):
    def __init__(self, name, form=None):
        Formula.__init__(self, name, form)
class PredicateInstance(Atom):
    def __init__(self, predicate, arguments):
        Atom.__init__(self, predicate.name)
        Checks.checkCompoudArity(predicate, arguments)
        Checks.checkPredicate(predicate)
        Checks.checkArgs(arguments)
        self.compoud = predicate
        self.terms = tuple(arguments)
    def __hash__(self):
        return hash((Atom.__hash__(self),self.terms))
    def __str__(self):
        if not self.terms: return self.name
        else: return '%s(%s)' % (self.name, ','.join(str(a) for a in self.terms))
    def __unicode__(self):
        if not self.terms: return unicode(self.name)
        else: return u'%s(%s)' % (self.name, u','.join(unicode(a) for a in self.terms))
    def __tex__(self):
        if not self.terms: return unicode(self.name)
        else: return u'%s\\left(%s\\right)' % (tex(self.name), u','.join(tex(a) for a in self.terms))
class Proposition(PredicateInstance):
    def __init__(self, name):
        PredicateInstance.__init__(self, Predicate(name, 0),())

class Term(Base):
    def __init__(self, name):
        Base.__init__(self, name)
    def __eq__(self, other):
        Checks.checkOperands(other,Term)
        return InfixEq((self,other))
    def __ne__(self, other):
        Checks.checkOperands(other,Term)
        return InfixNe((self,other))
class Variable(Term):
    def __init__(self, name):
        Term.__init__(self, name)
        Checks.checkUpperWord(name)
class FunctorInstance(Term):
    def __init__(self, functor, arguments):
        Term.__init__(self, functor.name)
        Checks.checkCompoudArity(functor, arguments)
        Checks.checkFunctor(functor)
        Checks.checkArgs(arguments)
        self.compoud = functor
        self.terms = tuple(arguments)
    def __hash__(self):
        return hash((Term.__hash__(self),self.terms))
    def __str__(self):
        if not self.terms: return self.name
        else: return '%s(%s)' % (self.name, ','.join(str(a) for a in self.terms))
    def __unicode__(self):
        if not self.terms: return unicode(self.name)
        else: return u'%s(%s)' % (self.name, u','.join(unicode(a) for a in self.terms))
    def __tex__(self):
        if not self.terms: return unicode(self.name)
        else: return u'%s\\left(%s\\right)' % (tex(self.name), u','.join(tex(a) for a in self.terms))
class Constant(FunctorInstance):
    def __init__(self, name):
        FunctorInstance.__init__(self, Functor(name, 0),())

class Operator(Formula):
    def __init__(self, form):
        Formula.__init__(self, None, form)
class Unary(Operator):
    def __init__(self, form):
        Operator.__init__(self, form)
class Not(Unary):
    def __init__(self, form):
        Unary.__init__(self, form)
        Checks.checkIfFormula(form)
    def __str__(self):
        return '~ %s'  % self.formulas
    def __unicode__(self):
        return u'\xAC%s' % self.formulas
    def __tex__(self):
        return u'\\neg %s' % tuple(tex(f) for f in self.formulas)
class Quantifier(Unary):
    def __init__(self, vars, form):
        Unary.__init__(self, form)
        self.vars = self.getVarsTuple(vars)
        Checks.checkVars(self.vars)
    def getVarsTuple(self, vars):
        result = []
        if isiterable(vars):
            for v in vars:
                if isinstance(v,Quantifier):result += v.vars
                else: result.append(v)
            return tuple(result)
        else: return (isinstance(vars,Quantifier) and vars.vars) or (vars,)
class Universal(Quantifier):
    def __init__(self, vars, form):
        Quantifier.__init__(self, vars, form)
    def simplify(self):
        form = self.formulas[0]
        if isinstance(form,Universal):
            var,form = form.simplify()
            return self.vars+var,form
        else:
            return self.vars,form
    def __str__(self):
        var,form = self.simplify()
        return '(![%s]:(%s))' % (','.join(str(v) for v in var),form )
    def __unicode__(self):
        var,form = self.simplify()
        return u'(\u2200%s)(%s)' % (u','.join(unicode(v) for v in var),form )
    def __tex__(self):
        var,form = self.simplify()
        return u'\\forall %s:\\left(%s\\right)' % (u','.join(tex(v) for v in var),tex(form))
class Existential(Quantifier):
    def __init__(self, vars, form):
        Quantifier.__init__(self, vars, form)
    def simplify(self):
        form = self.formulas[0]
        if isinstance(form,Existential):
            var,form = form.simplify()
            return self.vars+var,form
        else:
            return self.vars,form
    def __str__(self):
        var,form = self.simplify()
        return '(?[%s]:(%s))' % (','.join(str(v) for v in var),form )
    def __unicode__(self):
        var,form = self.simplify()
        return u'(\u2203%s)(%s)' % (u','.join(unicode(v) for v in var),form )
    def __tex__(self):
        var,form = self.simplify()
        return u'\\exists %s:\\left(%s\\right)' % (u','.join(tex(v) for v in var),tex(form))

class Binary(Operator):
    def __init__(self, form1, form2):
        Operator.__init__(self, (form1,form2))
class And(Binary):
    def __init__(self, form1, form2):
        Binary.__init__(self, form1, form2)
    def simplify(self):
        formulas = []
        for f in self.formulas:
            if isinstance(f,And): formulas += f.simplify()
            else: formulas.append(f)
        return formulas
    def __str__(self):
        return '(%s)' % ' & '.join(str(s) for s in self.simplify())
    def __unicode__(self):
        return u'(%s)' % u' \u2227 '.join(unicode(s) for s in self.simplify())
    def __tex__(self):
        return u'(%s)' % u' \\wedge '.join(tex(s) for s in self.simplify())
class Or(Binary):
    def __init__(self, form1, form2):
        Binary.__init__(self, form1, form2)
    def simplify(self):
        formulas = []
        for f in self.formulas:
            if isinstance(f,Or): formulas += f.simplify()
            else: formulas.append(f)
        return formulas
    def __str__(self):
        return '(%s)' % ' | '.join(str(s) for s in self.simplify())
    def __unicode__(self):
        return u'(%s)' % u' \u2228 '.join(unicode(s) for s in self.simplify())
    def __tex__(self):
        return u'(%s)' % u' \\vee '.join(tex(s) for s in self.simplify())
class Implication(Binary):
    def __init__(self, head, tail):
        Binary.__init__(self, head, tail)
    def __str__(self):
        return '(%s => %s)' % self.formulas
    def __unicode__(self):
        return u'(%s \u21D2 %s)' % self.formulas
    def __tex__(self):
        return u'(%s \\Rightarrow %s)' % tuple(tex(f) for f in self.formulas)
class Equivalence(Binary):
    def __init__(self, head, tail):
        Binary.__init__(self, head, tail)
    def __str__(self):
        return '(%s <=> %s)' % self.formulas
    def __unicode__(self):
        return u'(%s \u21D4 %s)' % self.formulas
    def __tex__(self):
        return u'(%s \\Leftrightarrow %s)' % tuple(tex(f) for f in self.formulas)
class Inequivalence(Binary):
    def __init__(self, head, tail):
        Binary.__init__(self, head, tail)
    def __str__(self):
        return '(%s <~> %s)' % self.formulas
    def __unicode__(self):
        return u'\u00AC(%s \u21D4 %s)' % self.formulas
    def __tex__(self):
        return u'\\neg(%s \\Leftrightarrow %s)' % tuple(tex(f) for f in self.formulas)

## Some special predicate instances for infix aritmetic (in)equality - equal/2, inequal/2
class InfixEq(PredicateInstance):
    def __init__(self, arguments):
        PredicateInstance.__init__(self, Predicate('equal',2), arguments)
    def __str__(self):
        return '(%s = %s)' % self.terms
    def __unicode__(self):
        return u'(%s = %s)' % self.terms
    def __tex__(self):
        return u'(%s = %s)' % tuple(tex(f) for f in self.terms)
class InfixNe(PredicateInstance):
    def __init__(self, arguments):
        PredicateInstance.__init__(self, Predicate('inequal',2), arguments)
    def __str__(self):
        return '(%s != %s)' % self.terms
    def __unicode__(self):
        return u'(%s \u2260 %s)' % self.terms
    def __tex__(self):
        return u'(%s \\neq %s)' % tuple(tex(f) for f in self.terms)

## useful methods
class all(Base):
    def __init__(self, *vars):
        Base.__init__(self, 'UniversalQuantifierHelper')
        Checks.checkVars(vars)
        self.vars = vars
    def __mul__(self, formula):
        return self(formula)
    def __call__(self, formula):
        Checks.checkIfFormula(formula)
        return formula / self.vars
class any(Base):
    def __init__(self, *vars):
        Base.__init__(self, 'ExistentialQuantifierHelper')
        Checks.checkVars(vars)
        self.vars = vars
    def __mul__(self, formula):
        return self(formula)
    def __call__(self, formula):
        Checks.checkIfFormula(formula)
        return formula % self.vars
def annotate(form,annot):
    return AnnotatedFormula(form,annot)
def axiom(name, form):
    return FOLFormula(name,'axiom',form)
def conjecture(name,form):
    return FOLFormula(name,'conjecture',form)
def negConjecture(name,form):
    return FOLFormula(name,'negated_conjecture',form)
def annot(annot):
    return Annotation(annot)
def sanity(form):
    pass
def tex(obj):
    if isinstance(obj,str) or isinstance(obj,int): return unicode(obj)
    else: return obj.__tex__()