#
# This file defines a family of self-checking tests of the temporal
# expression package.  Each test is data-driven by arrays 'avals', 'bvals'
# a 'cvals', which are driven onto signals 'asig', 'bsig' and 'csig'.
#
# The expected match or failure state is stored in array.  These values
# are used to make the tests self-checking.
#

from oroboro import *
from te import *
from pprint import pprint

#
# Apply a sequence of values to a signal.
#  apply on neg edge
#

def applyvals(clk, values, sig):

    for v in values:
        yield posedge(clk)
        sig.set(BV(v))


#
# Define an empty cycle.
#

def __ok(d):
    return True

ok = pred(__ok)

#
# To make these tests self checking, the expected value of the match (1)
# or failure (2) at each cycle is stored in an array mvals.
# A value of 0 means that neither match or failure is expected beginning
# at the cycle.
#

mvals = None                            # matchvals array - set by test

def checkmatch(tup):

    global mvals
    idx = tetrace_scycle(tup) - 1

    if idx < len(mvals):
        expect = mvals[idx]

        print "Checking expected match is 1:", expect

        if expect != 1:
            error("Match expected, got " + str(expect))


def checkfail(tup):

    global mvals
    idx = tetrace_scycle(tup) - 1

    if idx < len(mvals):
        expect = mvals[idx]

        print "Checking expected failure is 2:", expect

        if expect != 2:
            error("Failure expected, got " + str(expect))

#
# Simple alternation test
#
#  teexpr = ok + a + b | b + ok + a + c
#

def test_alt0(clk, asig, bsig, csig):

    print "***"
    print "*** Beginning test test_alt0"
    print "***"

    # cycle= 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
    avals = [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0]
    bvals = [0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]
    cvals = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

    # set expected match results at each cycle
    global mvals
    mvals = [2, 1, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2]

    ta = task(applyvals, clk, avals, asig)
    tb = task(applyvals, clk, bvals, bsig)
    tc = task(applyvals, clk, cvals, csig)
    
    # set up our TE
    psmplr = negedgesampler(clk)

    def preda(d, asig=asig):
        return int(asig.get()) == 1

    def predb(d, bsig=bsig):
        return int(bsig.get()) == 1

    def predc(d, csig=csig):
        return int(csig.get()) == 1

    teexpr = (ok + pred(preda) + pred(predb) |
              pred(predb) + ok + pred(preda) + pred(predc))
    print "Pretty Print", teexpr

    always(psmplr, teexpr, printmatches=1, printfails=1,
               onmatch=checkmatch, onfail=checkfail)

    return



#
# Simple conjunction test
#
#  teexpr = (ok + a + b + ok)  &  (b + ok + a + c)
#
# match at 2 detected at 5
# match at 8 detected at 11
# interesting failure at 9 detected at 12
# 
#

def test_conj0(clk, asig, bsig, csig):

    print "***"
    print "*** Beginning test test_conj0"
    print "***"

    # cycle= 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
    avals = [0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]
    bvals = [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0]
    cvals = [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1]

    # set expected match results at each cycle
    global mvals
    mvals = [2, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2]

    ta = task(applyvals, clk, avals, asig)
    tb = task(applyvals, clk, bvals, bsig)
    tc = task(applyvals, clk, cvals, csig)
    
    # set up our TE
    psmplr = negedgesampler(clk)

    def preda(d, asig=asig):
        return int(asig.get()) == 1

    a = pred(preda)

    def predb(d, bsig=bsig):
        return int(bsig.get()) == 1

    b = pred(predb)

    def predc(d, csig=csig):
        return int(csig.get()) == 1

    c = pred(predc)

    teexpr = (ok + a + b + ok) & (b + ok + a + c)
    print "Pretty Print", teexpr

    always(psmplr, teexpr, printmatches=1, printfails=1,
           onmatch=checkmatch, onfail=checkfail)

    return



#
# Conjunction test with variable length operands.
#
#  teexpr = (a + (ok * (1,8))) & ((ok * (1,8)) + b)
#
# Recall that both sides of & must start and end at the same cycle
# for a match to succeed.  This pattern finds a followed by b after
# 1 to 8 cycles.
#

def test_conj1(clk, asig, bsig, csig):

    print "***"
    print "*** Beginning test test_conj1"
    print "***"

    # cycle= 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
    avals = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    bvals = [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0]

    # set expected match results at each cycle
    global mvals
    mvals = [2, 2, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2]

    ta = task(applyvals, clk, avals, asig)
    tb = task(applyvals, clk, bvals, bsig)
    
    # set up our TE
    psmplr = negedgesampler(clk)

    def preda(d, asig=asig):
        return int(asig.get()) == 1

    a = pred(preda)

    def predb(d, bsig=bsig):
        return int(bsig.get()) == 1

    b = pred(predb)

    teexpr = (a + (ok * (1,8))) & ((ok * (1,8)) + b)
    print "Pretty Print", teexpr

    always(psmplr, teexpr, printmatches=1, printfails=1,
           onmatch=checkmatch, onfail=checkfail)

    return



#
# repeat test
#
#  teexpr = ((ok+a) | b) * (2,3)
#
# If you run this test, you can look at the output log and examine the
# traces of the matches to see how multiple matches at the same end time
# were found by the expression.
#

def test_repeat0(clk, asig, bsig, csig):

    print "***"
    print "*** Beginning test test_repeat0"
    print "***"

    # cycle= 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
    avals = [0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0]
    bvals = [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0]

    # expected vals on the completion cycle
    global mvals
    mvals = [1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 2, 2, 2]

    ta = task(applyvals, clk, avals, asig)
    tb = task(applyvals, clk, bvals, bsig)
    

    # set up our TE
    psmplr = negedgesampler(clk)

    def preda(d, asig=asig):
        d['a'] = currenttask().id
        return int(asig.get()) == 1

    def predb(d, bsig=bsig):
        d['b'] = currenttask().id
        return int(bsig.get()) == 1

    teexpr = ((ok + pred(preda)) | pred(predb)) * (2,3)
    print "Pretty Print", teexpr

    always(psmplr, teexpr, printmatches=1, printfails=1,
           onmatch=checkmatch, onfail=checkfail)
    
    return

#
# Test expression
#    a + ok * (3,7) + b
# to find a pair of markers separated by an interval.
#
# match at 2 succeeds
# match at 7 succeeds twice
# failure starting at 10 is detected at 18
#

def test_repeat1(clk, asig, bsig, csig):

    print "***"
    print "*** Beginning test test_repeat1"
    print "***"

    # cycle= 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
    avals = [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    bvals = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

    # expected vals on the completion cycle
    global mvals
    mvals = [2, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

    ta = task(applyvals, clk, avals, asig)
    tb = task(applyvals, clk, bvals, bsig)
    

    # set up our TE
    psmplr = negedgesampler(clk)

    def preda(d, asig=asig):
        return int(asig.get()) == 1

    a = pred(preda)

    def predb(d, bsig=bsig):
        return int(bsig.get()) == 1

    b = pred(predb)

    teexpr = a + (ok * (3,7)) + b
    print "Pretty Print", teexpr

    always(psmplr, teexpr, printmatches=1, printfails=1,
           onmatch=checkmatch, onfail=checkfail)

    return

    

#
# Simple intersection test, with dictionaries
#
#  teexpr = a ^ (ok * (2,5) + b)
#
# match at 3 detected at 6 and 7
# match at 9 detected at 13 and 14 (an not 15)
# 
#

def test_int0(clk, asig, bsig, csig):

    print "***"
    print "*** Beginning test test_int0"
    print "***"

    # cycle= 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
    avals = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    bvals = [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0]
    cvals = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]

    # set expected match results at each cycle
    global mvals
    mvals = [2, 2, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2]

    ta = task(applyvals, clk, avals, asig)
    tb = task(applyvals, clk, bvals, bsig)
    tc = task(applyvals, clk, cvals, csig)
    
    # set up our TE
    psmplr = negedgesampler(clk)

    def preda(d):
        d['a'] = int(csig.get())
        return int(asig.get()) == 1

    a = pred(preda)

    def predb(d):
        d['b'] = int(csig.get())
        return int(bsig.get()) == 1

    b = pred(predb)

    teexpr = a ^ (ok*(2,5) + b)
    print "Pretty Print", teexpr

    always(psmplr, teexpr, printmatches=1, printfails=1,
           onmatch=checkmatch, onfail=checkfail)

    return


#
# Simple conditional test
#   a >> b+b+b
#
# match starting at 3 is interesting
# failure starting at 9 is interesting
#

def test_cond0(clk, asig, bsig, csig):

    print "***"
    print "*** Beginning test test_cond0"
    print "***"

    # cycle= 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
    avals = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    bvals = [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]

    # set expected match results at each cycle
    global mvals
    mvals = [1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1]

    ta = task(applyvals, clk, avals, asig)
    tb = task(applyvals, clk, bvals, bsig)
    
    # set up our TE
    psmplr = negedgesampler(clk)

    def preda(d):
        return int(asig.get()) == 1

    a = pred(preda)

    def predb(d):
        return int(bsig.get()) == 1

    b = pred(predb)

    teexpr = a >> (b+b+b)
    print "Pretty Print", teexpr

    always(psmplr, teexpr, printmatches=1, printfails=1,
           onmatch=checkmatch, onfail=checkfail)

    return


#
# Simple once test.
#   once(a+a | b+b | c+c)
#
#

def test_once0(clk, asig, bsig, csig):

    print "***"
    print "*** Beginning test test_once0"
    print "***"

    # cycle= 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
    avals = [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    bvals = [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    cvals = [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]

    # set expected match results at each cycle
    global mvals
    mvals = [2, 2, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2]

    ta = task(applyvals, clk, avals, asig)
    tb = task(applyvals, clk, bvals, bsig)
    tc = task(applyvals, clk, cvals, csig)
    
    # set up our TE
    psmplr = negedgesampler(clk)

    def preda(d):
        return int(asig.get()) == 1

    a = pred(preda)

    def predb(d):
        return int(bsig.get()) == 1

    b = pred(predb)

    def predc(d):
        return int(csig.get()) == 1

    c = pred(predc)

    teexpr = once((a+a) | (b+b) | (c+c))
    # If you rerun the test with this expr, you will see same matches,
    # but multiple of them at each success.
    #
    # teexpr = ((a+a) | (b+b) | (c+c))
    print "Pretty Print", teexpr

    always(psmplr, teexpr, printmatches=1, printfails=1,
           onmatch=checkmatch, onfail=checkfail)

    return


#
# Simple inv test.
# Same stimuli as test_once0, but inverted match.
#
#

def test_inv0(clk, asig, bsig, csig):

    print "***"
    print "*** Beginning test test_inv0"
    print "***"

    # cycle= 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
    avals = [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    bvals = [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    cvals = [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]

    # set expected match results at each cycle
    global mvals
#   mvals = [2, 2, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2]
    mvals = [1, 1, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1]

    ta = task(applyvals, clk, avals, asig)
    tb = task(applyvals, clk, bvals, bsig)
    tc = task(applyvals, clk, cvals, csig)
    
    # set up our TE
    psmplr = negedgesampler(clk)

    def preda(d):
        return int(asig.get()) == 1

    a = pred(preda)

    def predb(d):
        return int(bsig.get()) == 1

    b = pred(predb)

    def predc(d):
        return int(csig.get()) == 1

    c = pred(predc)

    teexpr = ~((a+a) | (b+b) | (c+c))
    always(psmplr, teexpr, printmatches=1, printfails=1,
           onmatch=checkmatch, onfail=checkfail)

    return


#
# This main function runs one of the tests.
#
    


def mainfn(systf_x):

    print "In Main Function"

    clk = signal("top.clk")
    asig = signal("top.a")
    bsig = signal("top.b")
    csig = signal("top.c")

    testname = systf_x.my_config_param_string("test")

    if testname == None:
        testname = ""

    if testname == "alt0" or 0:
        test_alt0(clk, asig, bsig, csig)
        return

    if testname == "conj0" or 0:
        test_conj0(clk, asig, bsig, csig)
        return

    if testname == "conj1" or 0:
        test_conj1(clk, asig, bsig, csig)
        return

    if testname == "repeat0" or 0:
        test_repeat0(clk, asig, bsig, csig)
        return

    if testname == "repeat1" or 0:
        test_repeat1(clk, asig, bsig, csig)
        return

    if testname == "int0" or 0:
        test_int0(clk, asig, bsig, csig)
        return

    if testname == "cond0" or 0:
        test_cond0(clk, asig, bsig, csig)
        return

    if testname == "once0" or 0:
        test_once0(clk, asig, bsig, csig)
        return

    if testname == "inv0" or 0:
        test_inv0(clk, asig, bsig, csig)
        return

    yield timeout(0)
    return

        
