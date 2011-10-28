#!/usr/bin/python
from xml.dom.minidom import parse, parseString
from sys import stdin
import json

files = stdin.readlines()

def parseFile(f):
    dom = parse(f)
    filt = dom.firstChild
    if filt.nodeName != 'filter': raise ValueError('Fooka!!')
    child = filt.firstChild
    r = {}
    while child is not None:
        if child.nodeType == filt.ELEMENT_NODE:
            name = child.nodeName
            items = child.getElementsByTagName('item')
            if len(items) > 0:
                r[name] = [ i.firstChild.nodeValue for i in items ]
                try:
                    r[name] = [ int(i) for i in r[name] ]
                except ValueError:
                    pass
            else:
                r[name] = child.firstChild.nodeValue
                try:
                    r[name] = int(r[name])
                except ValueError:
                    pass
        try:
            child = child.nextSibling            
        except AttributeError: 
            break

    for key in ['type', 'annotation' ]:
        if key not in r:
            r[key] = ''
    for key in ['srcPorts', 'dstPorts', 'protocols', 'srcIPs', 'dstIPs']:
        if key not in r:
            r[key] = []
    r['fileName'] = f
    
    return r


print json.dumps([ parseFile(f.strip()) for f in files ])


