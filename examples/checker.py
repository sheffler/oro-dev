#
# Write a simple sequence detector using python generators
#
#  This checker looks for a fixed sequence
#

from __future__ import generators
from apvm import *

seq = [3,4,0,1]

def newchecker(systfinst, starttime):

    f = pack_s_vpi_value(vpiIntVal, 99)
    print f
    h = systfinst.vobjs[0]
    t = starttime

    vpi_print("Start Checker: %d\n" % t)

    for i in range(len(seq)):
	(format, val) = get_value_like(h, f)
	print t, val
	if seq[i] == val:
	    # so far, so good.
	    yield None
	else:
	    # didn't match.  abort.
	    return

    vpi_print("Found the SEQUENCE! %d\n" % t)


class checker(systf):

    def soscb(self):
	self.clist = [ ]		# checker list
	self.done = [ ]
	self.tcounter = 0

    def call_checkers(self):

	done = [ ]

	for c in self.clist:
	    try:
		c.next()
	    except:
		vpi_print("Checker done\n")
		done.append(c)

	for c in done:
	    self.clist.remove(c)
	

    def calltf(self):

	# keep a cycle counter
	self.tcounter = self.tcounter + 1

	new = newchecker(self, self.tcounter)
	self.clist.append(new)

	# call each of the checkers for this time step
	self.call_checkers()

	    
	return 0
	    
	    
	    
