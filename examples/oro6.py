#
# This example shows forming packets and communicating with
# a very simple memory-like device.
#
# All stimuli tasks *assume* they are called on the falling
# edge of the setup clock.
#

from oroboro import *

#
# A cycle waits one posedge and one negedge, to leave the user
# aligned on a negedge.
#

def cycle(sclk):

    taskmsg("Cycle")

    yield posedge(sclk)
    yield negedge(sclk)


#
# This task asserts a command packet for two cycles.
#

def cmdpacket(sclk, cmdsig_d, val):

    taskmsg("Cmd Packet: %s" % val)

    cmdsig_d.set(val)
    yield posedge(sclk)
    yield negedge(sclk)
    yield posedge(sclk)
    yield negedge(sclk)
    cmdsig_d.set(BV(0,5))


#
# A write function asserts the command packet and then the write
# data at the appropriate time.
#

def writefn(sclk, cmdsig_d, datasig_d, addr, data):

    taskmsg("WriteFn")

    # Form command from 2'b10 and address bits
    cmd = BV("2'b10") + addr[2:0]

    # assert the command packet with the address
    yield status(task(cmdpacket, sclk, cmdsig_d,cmd))

    # wait tCWD
    for i in range(2):
        yield status(task(cycle, sclk))

    # assert the data
    datasig_d.set(data[0])
    yield posedge(sclk)
    datasig_d.set(data[1])
    yield negedge(sclk)
    datasig_d.set(BV("8'bzzzzzzzz"))


def readfn(sclk, cmdsig_d, datasig, addr, data):

    taskmsg("ReadFn")

    # Form command from 2'b11 and address bits
    cmd = BV("2'b11") + addr[2:0]

    # assert the command packet
    yield status(task(cmdpacket, sclk, cmdsig_d, cmd))

    # wait tCAC
    for i in range(3):
        yield status(task(cycle, sclk))

    # wait for next posedge, to precede data
    yield posedge(sclk)
        
    data0 = datasig.get()
    taskmsg("Got Data0: %s" % data0)
    if not data0.cmp(data[0]):
        error("Data0 miscompare, expected %s" % data[0])
    

    yield negedge(sclk)

    data1 = datasig.get()
    taskmsg("Got Data1: %s" % data1)
    if not data1.cmp(data[1]):
        error("Data1 miscompare, expected %s" % data[1])


def mainfn(systf_x):

    # traceoff()

    sclk = signal("top.sclk")
    cmdsig_d = signal("top.cmd_d")
    datasig = signal("top.data")
    datasig_d = signal("top.data_d")

    for i in range(5):
        yield status(task(cycle, sclk))

    print "RIGHT BEFORE WRITE"
    data = [BV(17, 8), BV(9, 8)]
    yield status(task(writefn, sclk, cmdsig_d, datasig_d, BV(5), data))
    for i in range(5):
        yield status(task(cycle, sclk))

    print "RIGHT BEFORE READ"
    yield status(task(readfn, sclk, cmdsig_d, datasig, BV(5), data))

    yield timeout(0)                    # to make this a task

