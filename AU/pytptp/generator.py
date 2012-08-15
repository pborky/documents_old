#!/usr/bin/env python

def getGraph(stream):
    from graph import Graph
    try:
        return Graph('Default','\n'.join(stream.readlines()))
    finally:
        stream.close()

EQ_FMT = u'''
\\begin{equation}
\\begin{split}
%s
\\end{split}
\\end{equation}
'''
TEX_FMT = u'''
\\documentclass[landscape,a4paper]{article}

\\usepackage[cmex10]{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\interdisplaylinepenalty=2500

\\usepackage[margin=15mm]{geometry}

\\usepackage{eqparbox}

\\usepackage[utf8x]{inputenc}
\\usepackage{ucs}

\\renewcommand{\\labelitemi}{$\\bullet$}
\\renewcommand{\\labelitemii}{$\\circ$}
\\renewcommand{\\labelitemiii}{$\\ast$}


\\begin{document}

\\title{Automatick\\'e uva\\v zov\\'an\\'i - formalizace probl\\'emu v logice 1. \\v r\\'adu}
\\date{%s}
\\author{Peter~Bor\\'aros}

\\maketitle

%s

%% that's all folks
\\end{document}

'''
MONTHS = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
if __name__ == "__main__":
    import sys
    g = getGraph(sys.stdin)
    if len(sys.argv) > 1 :
        if sys.argv[1] == 'dot':
            print g.dot()
        elif sys.argv[1] == 'tpt':
            print g.tp()
        elif sys.argv[1] == 'uni':
            print g.uni()
        elif sys.argv[1] == 'tex':
            from datetime import date
            d = date.today()
            d = '%s %d, %d' % (MONTHS[d.month-1], d.day, d.year)
            #print '\n'.join(g.tex())
            print  TEX_FMT % (d, u'\n'.join(t and EQ_FMT%t or '' for t in g.tex()))




