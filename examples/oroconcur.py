#
# Ensure that task concurrency (to a basic degree) functions
# appropriately.
#

from oroboro import *
import apvm

avals = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
bvals = [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1]
cvals = [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1]


#
# Apply a sequence of values to a signal
#

def applyvals(clk, values, sig):

    for v in values:
        yield posedge(clk)
        sig.set(BV(v))

    return


#
# Check a sequence of values on a signal edge
#

def checkvals(clk, values, sig):

    print "Checking signal", sig

    for v in values:
        yield posedge(clk)
        yield vpireason(apvm.cbReadOnlySynch)

        expect = BV(v, 1)               # only one bit wide!
        actual = sig.get()

        print "Comparing actual ", actual, "with expect ", expect

        if not actual.cmp(expect):
            apvm.error("compare error")

    return


        
        
def mainfn(systf_x):

    clk = signal("top.clk")

    asig = signal("top.a")
    bsig = signal("top.b")
    csig = signal("top.c")

    # Compute our complicated expect function
    resultvals = [ ]
    for i in range(len(avals)):
        res = avals[i] ^ bvals[i] ^ cvals[i]
        resultvals.append(res)
    print "Result vals:", resultvals

    rsig = signal("top.res")

    at = task(applyvals, clk, avals, asig)
    bt = task(applyvals, clk, bvals, bsig)
    ct = task(applyvals, clk, cvals, csig)

    rt = task(checkvals, clk, resultvals, rsig)

    yield timeout(0)
    return

    
