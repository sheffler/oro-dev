#
# This example shows how to use generators as pseudo-random
# sequence generators.
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

#
# This generator randomly produces read and write tasks.
#  This function is *not* an Oroboro task, but is a "task factory."
#
def readwrite(memdict, sclk, cmdsig_d, datasig, datasig_d):

    while 1:

        x = random.randint(0, 99)

        if x < 50:
            # select write

            print "RIGHT BEFORE WRITE"
            addr = random.randint(0, 7)
            d0 = random.randint(0, 63)
            d1 = random.randint(0, 63)

            memdict[addr] = (d0, d1)

            trans = task(writefn, sclk, cmdsig_d, datasig_d,
                       BV(addr), ( BV(d0), BV(d1) ))
            # yield with a new write transaction task
            yield trans

        else:
            # select read

            print "RIGHT BEFORE READ"
            addr = random.randint(0, 7)

            if memdict.has_key(addr):
                # look up in dict
                expectints = memdict[addr]
                data0 = BV(expectints[0], 8)
                data1 = BV(expectints[1], 8)
                expect = ( data0, data1 )
            else:
                # else, don't care values
                expect = ( BV("8'bxxxxxxxx"), BV("8'bxxxxxxxx"))

            # yield with a new read transaction task
            trans = task(readfn, sclk, cmdsig_d, datasig, BV(addr), expect)
            yield trans


def mainfn(systf_x):

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

    while 1:

        # wait 5 clock cycles
        for i in range(5):
            yield status(task(cycle, sclk))

        # get the next random transaction
        trans = g.next()

        # start the transaction and wait for it to finish
        yield(status(trans))

    yield timeout(0)                    # to make this a task

