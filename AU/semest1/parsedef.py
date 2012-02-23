
import ply.lex as lex
import ply.yacc as yacc
from graph import Graph

node_type = {
    '-' : 'DIRECT',
    '|' : 'SIGNAL',
    '<' : 'DIVERGENT',
    '>' : 'CONVERGENT',
    'I' : 'INPUT',
    'O' : 'OUTPUT'
}

tokens = ['ID', 'NODETYPE', 'WHITESPACE'] + list(node_type.values());

t_ID = r'([a-z0-9][^\s]*)'
t_WHITESPACE = r'\s+'

def t_NODETYPE(t):
    r'(-|[|]|<|>|I|O)'
    t.type = node_type.get(t.value,'NODETYPE')  
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

graph = Graph('Default')

def p_node_direct(p):
    'node : ID WHITESPACE DIRECT WHITESPACE ID WHITESPACE ID'
    p[0] = (graph.add(p[1], 'DIRECT', [p[5],], [p[7],]),graph)

def p_node_signal(p):
    'node : ID WHITESPACE SIGNAL WHITESPACE ID WHITESPACE ID'
    p[0] = (graph.add(p[1], 'SIGNAL', [p[5],], [p[7],]),graph)

def p_node_diverging(p):
    'node : ID WHITESPACE DIVERGENT WHITESPACE ID WHITESPACE ID WHITESPACE ID'
    p[0] = (graph.add(p[1], 'DIVERGENT', [p[5],], [p[7], p[9]]),graph)

def p_node_connecting(p):
    'node : ID WHITESPACE CONVERGENT WHITESPACE ID WHITESPACE ID WHITESPACE ID'
    p[0] = (graph.add(p[1], 'CONVERGENT', [p[5], p[7]], [p[9],]),graph)

def p_node_input(p):
    'node : ID WHITESPACE INPUT WHITESPACE ID'
    p[0] = (graph.add(p[1], 'INPUT', [], [p[5],]),graph)

def p_node_output(p):
    'node : ID WHITESPACE OUTPUT WHITESPACE ID'
    p[0] = (graph.add(p[1], 'OUTPUT', [p[5],], []),graph)

def p_node_w(p):
    'node : node WHITESPACE'
    p[0] = p[1]

def p_node_node(p):
    'node : node node'
    p[0] = graph

def p_error(p):
    raise Exception('Syntax error near token: "'+p.value+'" ('+p.type+').' )

# Build the lexer
lexer = lex.lex()
parser = yacc.yacc()


