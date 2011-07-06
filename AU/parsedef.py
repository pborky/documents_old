
import ply.lex as lex
import ply.yacc as yacc
from graph import Graph

node_type = {
    '-' : 'DIRECT',
    '|' : 'SIGNAL',
    '<' : 'DIVERGING',
    '>' : 'CONNECTING',
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
    p[0] = 'direct: ' + p[1] + '('+ p[5] + ',' + p[7] +')'
    graph.add(p[1], 'DIRECT', [p[5],], [p[7],])

def p_node_signal(p):
    'node : ID WHITESPACE SIGNAL WHITESPACE ID WHITESPACE ID'
    p[0] = 'signal: ' + p[1] + '('+ p[5] + ',' + p[7] +')'
    graph.add(p[1], 'SIGNAL', [p[5],], [p[7],])

def p_node_diverging(p):
    'node : ID WHITESPACE DIVERGING WHITESPACE ID WHITESPACE ID WHITESPACE ID'
    p[0] = 'diverging: ' + p[1] + '('+ p[5] + ',' + p[7] + ',' + p[9]  +')'
    graph.add(p[1], 'DIVERGING', [p[5],], [p[7], p[9]])

def p_node_connecting(p):
    'node : ID WHITESPACE CONNECTING WHITESPACE ID WHITESPACE ID WHITESPACE ID'
    p[0] = 'connecting: ' + p[1] + '('+ p[5] + ',' + p[7] + ',' + p[9]  +')'
    graph.add(p[1], 'CONNECTING', [p[5], p[7]], [p[9],])

def p_node_input(p):
    'node : ID WHITESPACE INPUT WHITESPACE ID'
    p[0] = 'input: ' + p[1] + '('+ p[5]  +')'
    graph.add(p[1], 'INPUT', [], [p[5],])

def p_node_output(p):
    'node : ID WHITESPACE OUTPUT WHITESPACE ID'
    p[0] = 'output: ' + p[1] + '('+ p[5]  +')'
    graph.add(p[1], 'OUTPUT', [p[5],], [])

def p_node_w(p):
    'node : node WHITESPACE'
    p[0] = p[1];

def p_node_node(p):
    'node : node node'
    p[0] = p[1]+'\n'+p[2];

# Build the lexer
lexer = lex.lex()
parser = yacc.yacc()


