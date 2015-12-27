#
# This is an example that generates random traffic to a memory
# device.  It shows using a Python diction to store expected data.
#
# This example also generates random errors on expect data to
# illustrate the error reporting mechanism.  Thus, this test
# always reports miscompares and the error count at the end.
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

    while 1:
        for i in range(5):
            yield status(task(cycle, sclk))

        print "RIGHT BEFORE WRITE"

        addr = random.randint(0, 7)
        d0 = random.randint(0, 63)
        d1 = random.randint(0, 63)

        memdict[addr] = (d0, d1)
        
        yield status(task(writefn, sclk, cmdsig_d, datasig_d,
                          BV(addr), ( BV(d0), BV(d1) )))

        for i in range(5):
            yield status(task(cycle, sclk))

        print "RIGHT BEFORE READ"

        addr = random.randint(0, 7)

        if (random.randint(0, 49) == 0):
            # introduce random errors on reads
            expect = ( BV("8'b00000000"), BV("8'b00000000") )
        else:
            if memdict.has_key(addr):
                # look up in dict
                expectints = memdict[addr]
                data0 = BV(expectints[0], 8)
                data1 = BV(expectints[1], 8)
                expect = ( data0, data1 )
            else:
                # else, don't care values
                expect = ( BV("8'bxxxxxxxx"), BV("8'bxxxxxxxx"))

        yield status(task(readfn, sclk, cmdsig_d, datasig, BV(addr), expect))

    yield timeout(0)                    # to make this a task

