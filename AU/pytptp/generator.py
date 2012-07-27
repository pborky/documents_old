#!/usr/bin/env python

def getGraph(stream):
    from pydot import graph_from_dot_data
    from graph import Graph
    data = '\n'.join(stream.readlines())
    dot = graph_from_dot_data(data)
    return Graph('Default',dot)

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
\\date{Jun 1, 2012}
\\author{Peter~Bor\\'aros}

\\maketitle

%s

%% that's all folks
\\end{document}

'''

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
            print  TEX_FMT % u'\n'.join(EQ_FMT%t for t in g.tex())




