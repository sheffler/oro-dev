#
# Simple Oroboro program illustrating basic concepts.
#
# Tom Sheffler
# June 2004
#


from oroboro import *

#
# Beginning of example code
#

def timergen():

    print "-- TIMER -- START ", currenttime()

    for i in range(20):
        yield timeout(3)
        print "-- TIMER -- ", currenttime()

    return


def watchsig(sig):

    print "-- Watching signal %s" % sig

    while 1:
        yield sigchange(sig)
        print "Signal %s changed: %s" % (sig, sig.get())

    return

def setsig(sig):

    print "-- Setting signal %s" % sig

    for i in range(10):
        taskmsg("XX YIELDING")
        yield timeout(15)
        taskmsg("XX TIMINGOUT")
        sig.set(apvm.BV(i), 1)          # this set is done with a delay of 1

#
# The main userfunction always receives exactly one argument -
# a reference to the apvm.systf instance which invoked it.
# In this way, the user can get command line arguments and
# configuration file parameters using standard APVM conventions.
#
#   systf_h.my_config_param_string("paramname")
#

def exampleuserfn(systf_h):

    c = signal("top.clk")
    o_d = signal("top.oro_d")

    timer = task(timergen)              # spawn timer

    watcher = task(watchsig, c)         # spawn watcher

    setter = task(setsig, o_d)          # spawn setter

    taskmsg("EXAMPLE - before YIELD")

    for i in range(10):

        taskmsg("YIELD")

        yield timeout(17), status(timer)

        print "Current reason", currentreason(), currentreasonindex()

        if currentreasonindex() == 1:
            print "MY TIMER ENDED!"

            timer = task(timergen)

        taskmsg("TIMEOUT")
        o_d.set(apvm.BV(i), 0)          # this set is done with a delay of 0


    taskmsg("DONE")
    timer.kill()
    taskmsg("DISPATCH " + str(apvm._dispatchdict.keys()) + " " + str(apvm._dispatchdict))

    return

