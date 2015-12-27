#
# An example of timers and events.
# Both tasks will listen to the clock and notify the
# other that it saw an edge.
#

from oroboro import *

def PosTask(c, e):

    taskmsg("Starting PosTask")

    while 1:

        # wait for either the posedge of clock or the event
        yield posedge(c), waitevent(e)

        # determine which was signaled
        if currentreasonindex() == 0:
            taskmsg("PosTask - saw Posedge")
            e.post()                    # notify other task

        if currentreasonindex() == 1:
            taskmsg("PosTask - saw Event")

        
def NegTask(c, e):

    taskmsg("Starting NegTask")

    while 1:

        # wait for either the posedge of clock or the event
        yield negedge(c), waitevent(e)

        # determine which was signaled
        if currentreasonindex() == 0:
            taskmsg("NegTask - saw Negedge")
            e.post()                    # notify other task

        if currentreasonindex() == 1:
            taskmsg("NegTask - saw Event")


def mainfn(tf):

    # traceoff()
    taskmsg("Starting Main Task")

    c = signal("top.clk")
    e = event()

    # start the two subordinates
    t1 = task(PosTask, c, e)
    t2 = task(NegTask, c, e)

    yield timeout(0)                    # MAIN MUST BE A GENERATOR!!!


        
