#
# This example is an experiment with the simreset() function.
#

from oroboro import *
import random

#
# This is like oro6 except that it loops forever
#
from oro6 import cycle
from oro6 import cmdpacket
from oro6 import writefn
from oro6 import readfn

from oro8 import readwrite              # random read/write traffic

def test(systf_x):

    # traceoff()

    sclk = signal("top.sclk")
    cmdsig_d = signal("top.cmd_d")
    datasig = signal("top.data")
    datasig_d = signal("top.data_d")

    # this dict tracks memory for expected data
    #   { loc0: (d0, d1), ... }
    #
    memdict = { }

    # initialize the transaction generator
    g = readwrite(memdict, sclk, cmdsig_d, datasig, datasig_d)

    for i in range(5):

        # wait 5 clock cycles
        for i in range(5):
            yield status(task(cycle, sclk))

        # get the next random transaction
        trans = g.next()

        # start the transaction and wait for it to finish
        yield(status(trans))


# Under CVER, this did in deed reset and stop the simulator
# ... leaving us at an interactive prompt.  Successful use of $reset
# will require the Oro side clearing the memdict{} (as it does) and
# resetting the main APVM error counter.  Sigchange callbacks may need
# to be re-registered.

def mainfn(systf_x):

    for i in range(2):

        yield status(task(test, systf_x))
        print "*** RESET VERILOG"
        simreset()

    yield timeout(0)



