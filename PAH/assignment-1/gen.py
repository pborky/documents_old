import random
import sys

col = [ 'blue', 'yellow', 'red', 'green']
shp = ['trigon', 'circle', 'square' ]
cnt = int(sys.argv[1])
print '''
(define (problem big-problem%d)
    (:domain signs)
    (:objects
        heap - buffer
        place1 place2 - workplace
        trigon circle square - shape
        blue yellow red green - color
        %s - board
    )
    (:init
        (empty place1)
        (empty place2)
        (hand-free)
        (= (total-cost) 0)

%s
    )
    (:goal
        (and
%s

%s

%s
        )
    )
    (:metric minimize (total-cost))
)
''' % (
cnt-1,
' '.join( 'board%d' % i for i in range(cnt) ),
'\n'.join('        (at board%d heap)' % i for i in range(cnt)),
'\n'.join('            (at board%d heap)' % i for i in range(cnt)),
'\n'.join('            (has-color board%d %s)' % ( i, random.choice(col))  for i in range(cnt)),
'\n'.join('            (has-shape board%d %s)' % ( i, random.choice(shp))  for i in range(cnt))
)


