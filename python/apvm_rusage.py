
import resource
import socket
from apvm import *

#
# This PLI "Application" prints the Unix resource usage
# of the Verilog program at the end of execution.
#

class printrusage(systf):

    # Print resource usage at end of simulation
    def eoscb(self):

        host = socket.gethostname()

        (utime,		# time in user mode (float)
         stime,		# time in system mode (float)
         maxrss,	# maximum resident set size
         ixrss,		# shared memory size
         idrss,		# unshared memory size
         srss,		# unshared stack size
         minflt,	# page faults not requiring I/O
         majflt,	# page faults requiring I/O
         nswap,		# number of swap outs
         inblock,	# block input operations
         oublock,	# block output operations
         msgsnd,	# messages sent
         msgrcv,	# messages received
         nsignals,	# signals received
         nvcsw,		# voluntary context switches
         nivcsw		# involuntary context switches
         ) = resource.getrusage(resource.RUSAGE_SELF)

        vpi_print("*** GETRUSAGE Report ***\n")
        vpi_print("%30s: %s\n" % ("Hostname", host))
        vpi_print("%30s: %g\n" % ("Time in User Mode", utime))
        vpi_print("%30s: %g\n" % ("Time in System Mode", stime))
        vpi_print("%30s: %d\n" % ("Maximum Resident Set Size", maxrss))
        vpi_print("%30s: %d\n" % ("Shared Memory Size", ixrss))
        vpi_print("%30s: %d\n" % ("Unshared Memory Size", idrss))
        vpi_print("%30s: %d\n" % ("Unshared Stack Size", srss))
        vpi_print("%30s: %d\n" % ("Page Faults Not Requiring I/O", minflt))
        vpi_print("%30s: %d\n" % ("Page Faults Requiring I/O", majflt))
        vpi_print("%30s: %d\n" % ("Number of swap Outs", nswap))
        vpi_print("%30s: %d\n" % ("Block Input Operations", inblock))
        vpi_print("%30s: %d\n" % ("Block Output Operations", oublock))
        vpi_print("%30s: %d\n" % ("Messages Sent", msgsnd))
        vpi_print("%30s: %d\n" % ("Messages Received", msgrcv))
        vpi_print("%30s: %d\n" % ("Signals received", nsignals))
        vpi_print("%30s: %d\n" % ("Voluntary Context Switches", nvcsw))
        vpi_print("%30s: %d\n" % ("Involuntary Context Switches", nivcsw))
        

