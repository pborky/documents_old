# vim: syntax=python 

## resources
M = list('a%d'%i for i in range(5))
M += ('b%d'%i for i in range(4) )
M += ('c%d'%i for i in range(3) )
M += ('d%d'%i for i in range(5) )
M += ('f%d'%i for i in range(1,3) )

## worktimes
W = dict([
 ('a0', 1),('a1', 10),('a2', 1), ('a3', 15), ('a4', 1), 
 ('b0', 1), ('b1', 15), ('b2', 1), ('b3', 1), 
 ('c0', 1), ('c1', 15), ('c2', 1), 
 ('d0', 1),('d1', 10),('d2', 1), ('d3', 15), ('d4', 1), 
 ('f1', 10), ('f2', 1), 
])

## precedence operator
prec_dict = dict([
 ('a0','a1'),('a1','a4'),('a2','a3'),('a3','a4'),
 ('b0','b1'),('b1','b2'),('b2','b3'),
 ('c0','c1'),('c1','c2'),
 ('d0','d1'),('d1','d4'),('d2','d4'),('d3','d4'),
 ('f1','f2'),
 ('a4','d2'), ('b3','c2'),('c2','d3'),('d4','f1')
 ])
prec = lambda x,y: prec_dict.has_key(x) and prec_dict[x] == y

def prec_t(x,y): #transitive closure of prec
    if prec(x,y):
        return True
    return prec_dict.has_key(x) and prec_t(prec_dict[x],y)

same_block = lambda x,y: x in M and y in M and x[0]==y[0]

def get_jobshopdata(Njobs):
    ## jobs
    # model, quantity, deadline
    J = [('Model%s'%s[0],s[1],s[2]) 
        for s in [
                 ('A',50,5000),
                 ('B',100,45000),
                 ('C',20,10000),
                 ('D',10, 20000),
                 ('E',5,500),
                 ('F',1,300),
                 ('G',5,3000),
                 ('H',500, 80000),
                 ('I',500, 80000)

             ]][:Njobs]
    ## operations
    O = set((j,o) for j,qty,dl in J  for o in M)
    ## processtimes
    p = dict(((j,o),qty*W[o]) for j,qty,dl in J  for o in M)
    ## release times
    r = dict([('a0', 0),('a2', 10),('b0',50),('c0',0), ('d0',1) ])
    r = dict(((j,o),(lambda x:(r.has_key(x) or 0) and r[x])(o)) for j,qty,dl in J  for o in M)
    ## deadlines
    d = dict(((j,o),dl) for j,qty,dl in J  for o in M)
    ## setuptimes
    #s = dict((((j,i),(j,k)),0) for i in M for j,qty,dl in J for k in M)
    s = dict(((i,j),5) for i in O for j in O if i[0]==j[0])
    s.update(dict(((i,j),100) for i in O for j in O if i[0]!=j[0]))
    return J,O,d,p,r,s


def problemLR_dual(prob, lp, Njobs):
    J,O,d,p,r,s = get_jobshopdata(Njobs)
    #define vars
    Cmax = lp.LpVariable('Cmax',0)
    D = lp.LpVariable.dicts("D",O,0)
    b = lp.LpVariable.dicts("b",O)
    x = lp.LpVariable.dicts( 'x',
            set( (i,j)
                for i in O 
                    for j in O 
                        if i!=j and i[1]==j[1]) ,0,1)
    pi = lp.LpVariable.dicts('pi',
            set( (i,j)
                for i in O 
                    for j in O 
                        if i!=j and i[1]==j[1]) )

    lamb = lp.LpVariable.dicts('lambda',
            set( (i,j)
                for i in O 
                    for j in O 
                        if i[0] == j[0] and prec(i[1],j[1]) ) )

    # rename vars
    for k,v in D.items(): v.setName('D_%s_%s' % k )
    for k,v in b.items(): v.setName('b_%s_%s' % k )
    for k,v in x.items(): v.setName('x_%s_%s_%s_%s' % (k[0]+k[1]))
    for k,v in lamb.items(): v.setName('lambda_%s_%s_%s_%s' % (k[0]+k[1]))
    for k,v in pi.items(): v.setName('pi_%s_%s_%s_%s' % (k[0]+k[1]))
    
    ## lowerBound (10)
    for k,v in b.items(): v.lowBound = r[k]
    
    ## uperBound (11)
    for k,v in b.items(): v.upBound = d[k]-p[k]

    ## capacity (13)
    constr = [x[i,j]+x[j,i] == 1
                for i in O 
                    for j in O 
                        if i!=j and i[1]==j[1]]

    ## precedence (12)
    obj = [ lamb[i,j] *(-b[j] + b[i] + p[i] + s[i,j])
                for i in O 
                    for j in O
                        if i[0] == j[0] and prec(i[1],j[1])]

    ## capacity (14)
    obj += [ (pi[i,j]*(-b[j] + b[i] + x[i,j]*(p[i] + s[i,j]) - (1-x[i,j])*d[i]))
                for i in O
                    for j in O 
                        if i!=j and i[1]==j[1] ] #(prec_t(i[1], j[1]) or i[1]==j[1])]
    
    ## Cmax + sum(D) (9)
    constr += [Cmax>=b[o]+p[o] for o in O]
    constr += [D[i] == b[i]+p[i]+s[i,j]-b[j]
                for i in O 
                    for j in O
                        if prec(i[1],j[1]) and i[0]==j[0] and same_block(i[1], j[1])]
    
    oo = 0
    for o in obj: oo = oo+o

    # add all to problem
    for k in constr:
        prob += k
    # and objective too
    prob += lp.lpSum(D+Cmax+oo)
    
    # return vars and problem
    return prob,lamb,pi

def problem(prob, lp, Njobs):
    J,O,d,p,r,s = get_jobshopdata(Njobs)
    #define vars
    Cmax = lp.LpVariable('Cmax',0)
    D = lp.LpVariable.dicts("D",O,0)
    b = lp.LpVariable.dicts("b",O)
    x = lp.LpVariable.dicts( 'x',
            set( (i,j)
                for i in O 
                    for j in O 
                        if i!=j and i[1]==j[1]) ,0,1,lp.LpInteger)
    # rename vars
    for k,v in D.items(): v.setName('D_%s_%s' % k )
    for k,v in b.items(): v.setName('b_%s_%s' % k )
    for k,v in x.items(): v.setName('x_%s_%s_%s_%s' % (k[0]+k[1]))
    
    ## lowerBound (10)
    for k,v in b.items(): v.lowBound = r[k]
    
    ## uperBound (11)
    for k,v in b.items(): v.upBound = d[k]-p[k]

    ## precedence (12)
    constr = [ b[j] >= b[i] + p[i] + s[i,j]
                for i in O 
                    for j in O
                        if i[0] == j[0] and prec(i[1],j[1])]

    ## capacity (13)
    constr += [x[i,j]+x[j,i] == 1 
                for i in O 
                    for j in O 
                        if i!=j and i[1]==j[1]]

    ## capacity (14)
    constr += [b[j] >= b[i] + x[i,j]*(p[i] + s[i,j]) - (1-x[i,j])*d[i]
                for i in O
                    for j in O 
                        if i!=j and i[1]==j[1]] #(prec_t(i[1], j[1]) or i[1]==j[1])]
    
    ## Cmax + sum(D) (9)
    constr += [Cmax>=b[o]+p[o] for o in O]
    constr += [D[i] == b[i]+p[i]+s[i,j]-b[j]
                for i in O 
                    for j in O
                        if prec(i[1],j[1]) and i[0]==j[0] and same_block(i[1], j[1])]
    # add all to problem
    for k in constr:
        prob += k
    # and objective too
    prob += lp.lpSum(D+Cmax)
    
    # return vars and problem
    return prob,Cmax,b,x,D,j

def dippy(Njobs, conf = None):
    # pass the problem to Dippy
    import  coinor.pulp as lp
    import coinor.dippy as dippy
    from time import time
    prob,Cmax,b,x,D,J = problem(dippy.DipProblem("Job Shop", lp.LpMinimize), lp, Njobs)
    tic = time()
    if conf is not None:
        try: dippy.Solve(prob, conf)
        except: pass
    else:
        try: dippy.Solve(prob)
        except: pass
    toc = time()
    return prob,Cmax,b,x,D,J,toc-tic

def pulp(Njobs):
    # use default GLPK method
    import pulp as lp
    from time import time
    prob,Cmax,b,x,D,J = problem(lp.LpProblem('Job Shop',lp.LpMinimize), lp, Njobs)
    tic = time()
    prob.solve()
    toc = time()
    return prob,Cmax,b,x,D,J,toc-tic

def pulpLR(Njobs):
    # use default GLPK method
    import pulp as lp
    from time import time
    prob,lamb,pi = problemLR_dual(lp.LpProblem('Job Shop',lp.LpMaximize), lp, Njobs)
    tic = time()
    prob.solve()
    toc = time()
    return prob,lamb,pi,toc-tic


def print_results(a,j):
    # print wonderfull unicode table
    J,O,d,p,r,s = get_jobshopdata(j)
    a = list(a)
    a.sort()
    tables = { 
            'topleft': u'\u256d',
            'topright': u'\u256e',
            'botleft': u'\u2570',
            'botright': u'\u256f',
            'horz': u'\u2500',
            'vert': u'\u2502',
            'cross': u'\u253c',
            'topT': u'\u252c',
            'botT': u'\u2534',
            'leftT': u'\u251c',
            'rightT': u'\u2524'
        }
    # top
    print ('%(topleft)s'+('%(horz)s'*11)+('%(topT)s'+('%(horz)s'*11))*2+ '%(topright)s') % tables 
    # head
    print '%(vert)s Operation %(vert)s Start     %(vert)s Duration  %(vert)s' % tables
    # sep
    print ('%(leftT)s'+('%(horz)s'*11)+('%(cross)s'+('%(horz)s'*11))*2+ '%(rightT)s') % tables
    # values
    for i in a: print ('%(vert)s %%s %%s %(vert)s %%9.1F %(vert)s %%9d %(vert)s'%tables) % i
    # bottom
    print ('%(botleft)s'+('%(horz)s'*11)+('%(botT)s'+('%(horz)s'*11))*2+ '%(botright)s') % tables 

def draw_gantt(a,nj,name):
    # draw nice graph
    j,O,d,p,r,s = get_jobshopdata(nj)
    a = list(a)
    a.sort()
    import numpy as np
    import matplotlib.pyplot as plt
    import pylab
    j = [i for i,x,y in j]
    fig = plt.figure(name,figsize=(9,7))
    ax1 = fig.add_subplot(111)
    pos = np.arange(len(j))+0.5
    ax1.axis([0,max(s+d for m,o,s,d in a),0,len(j)])
    rects = []
    colors = ['r','b','g','c','m']
    yticks = {'a':.85,'b':.7,'c':.6,'d':.4,'f':.2}
    ys = {'a0':.9,'a1':.9, 'a2':.8,'a3':.8,'a4':.85, 
          'b0':.7,'b1':.7,'b2':.7,'b3':.7,
          'c0':.6, 'c1':.6,'c2':.6,
          'd2': .5, 'd0':.4, 'd1': .4,'d4': .4, 'd3':.3,
          'f1':.2, 'f2':.2}
    for m in M:
        # prepare rectangles
        rects += ax1.barh(pos,[0]*len(j),align='center',height=0.5, color= colors[int(m[1])] )
    for mod,op,start,dur in a:
        # modify how they look
        r=rects[ j.index(mod)+M.index(op)*len(j)  ]; 
        r.set_x(start); 
        r.set_width(dur);
        r=rects[ j.index(mod)+M.index(op)*len(j)  ];
        r.set_y(j.index(mod)+ys[op]); 
        r.set_height(.1)
    # anotate y axis
    pylab.yticks(pos, j)
    fig.show()

if __name__=='__main__':
    probs = []
    for nj in range(1,7):
        #prob,Cmax,b,x,D,j,t = dippy(nj,conf={'PRICE_AND_CUT': {'LogDumpModel': '10'}})
        #prob,Cmax,b,x,D,j,t = dippy(nj)
        #probs += ('dip',nj,b,t,prob),
        J,O,d,p,r,s = get_jobshopdata(nj)
        #print_results((o+(v.value(),p[o]) for o,v in b.items()),nj)
        #draw_gantt((o+(v.value(),p[o]) for o,v in b.items()),nj,'dip-%d'%nj)
        prob,Cmax,b,x,D,j,t = pulp(nj)
        probs += ('glpk',nj,b,t,prob),
        fn = 'jobshop-%d.cpxlp'%nj
        prob.writeLP(fn)
        #print_results((o+(v.value(),p[o]) for o,v in b.items()),nj)
        draw_gantt((o+(v.value(),p[o]) for o,v in b.items()),nj,'glpk-%d'%nj)

