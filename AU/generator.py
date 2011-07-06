
import parsedef  as  p
import readline

#p.lexer.input(data)

# Tokenize
#for tok in parsedef.lexer:
#    print tok

data = ''
while True:
   try:
       s = raw_input()
   except EOFError:
       break
   if not s: continue
   data = data+ '\n' + s

result = p.parser.parse(data)

print p.graph

