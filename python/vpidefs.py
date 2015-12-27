#!/usr/local/bin/python
#
# Program to extract VPI #defines from vpi_user.h
#
# Comments to the right of defines are collected so they can become
# Python docstrings later.
#


import re
import sys

regx1s = r"""^#define ((vpi|cb)[A-Za-z0-9_]*)\s*([x0-9]*)"""
regx2s = r"""^#define ((vpi|cb)[A-Za-z0-9_]*)\s*([x0-9]*) \s* /\*(.*)\*/"""

regx1 = re.compile(regx1s)
regx2 = re.compile(regx2s)


fname = sys.argv[1]

f = open(fname, "r")

ll = f.readlines()

for l in ll:

    x = regx2.match(l)
    if x:
	g = x.groups()
	print "    {\"%s\", %s, 0, \"%s\"}," % (g[0], g[0], g[2])
    else:
	x = regx1.match(l)
	if x:
	    g = x.groups()
	    print "    {\"%s\", %s, 0, \"%s\"}," % (g[0], g[0], "")
    
	

    

