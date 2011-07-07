#!/usr/bin/env python
import parsedef
import sys

data = ''
while True:
   try:
       s = raw_input()
   except EOFError:
       break
   if not s: continue
   data = data+ '\n' + s

result = parsedef.parser.parse(data)

if __name__ == "__main__" and len(sys.argv) > 1:
    if sys.argv[1] == 'dot':
        print result.dot()
    else:
        raise Exception('unknown argument: '+sys.argv[1])
else:
    raise Exception('expected argument')

