#
# This simple application models a delay element with enable and
# a programmable delay period.
#

import apvm

_debuggingmessages = None

#
# Invocation:
#   call in an intitial block, this way.
# res = $apvm("me", "apvm_delay", "delayelt", period, in, en, out)
#

class delayelt(apvm.systf):

    def soscb(self):

	# make some formats for our get_value_like fns
	self.intfmt = apvm.pack_s_vpi_value(apvm.vpiIntVal, 0)
	self.strfmt = apvm.pack_s_vpi_value(apvm.vpiBinStrVal, "x")
        self.suppressfmt = apvm.pack_s_vpi_value(apvm.vpiSuppressVal, 0)

	# make a time object
	nulltime = apvm.pack_s_vpi_time(apvm.vpiSimTime, 0, 0, 0.0)

	# register for us to be called back on value changes on in and en
	self.callmeback(apvm.cbValueChange,
			self.vobjs[1],
			nulltime,
			# self.strfmt,
			self.suppressfmt,
			"in")

	self.callmeback(apvm.cbValueChange,
			self.vobjs[2],
			nulltime,
			# self.strfmt,
                        self.suppressfmt,
			"en")

	# make our event queue
	self.events = [ ]

    # read the current delay value as an integer
    def getdelayval(self):

	val = apvm.get_value_like(self.vobjs[0], self.intfmt)
	return val[1]

    # schedule us to be called back with new value on out
    def schedule(self, strval, dly, lo, hi):

        if _debuggingmessages:
            print "schedule", (strval, dly, lo, hi)

	# put on event list to be scheduled next time we wake up
	self.events.append((strval, dly, dly+lo, hi))

	if len(self.events) == 1:
	    # then no pending events, schedule value change
	    dly = apvm.pack_s_vpi_time(apvm.vpiSimTime, dly, 0, 0.0)
	    val = apvm.pack_s_vpi_value(apvm.vpiBinStrVal, strval)
	    # apvm.put_value(self.vobjs[3], val, dly, apvm.vpiTransportDelay)
	    apvm.put_value(self.vobjs[3], val, dly, apvm.vpiPureTransportDelay)

	    # also schedule our callback
	    # self.callmeback(apvm.cbAfterDelay, None, dly, val, "")
	    self.callmeback(apvm.cbAfterDelay, None, dly, self.suppressfmt, "")


    #
    # This is the method called for any callback related to this systf
    #

    def callback(self, reason, h, t, v, idx, ud):

	(timfmt, lo, hi, doub) = apvm.unpack_s_vpi_time(t)

        if _debuggingmessages:
            print "callback", reason, (timfmt, lo, hi, doub)

	if reason == apvm.cbValueChange:

	    # read the values of our input vectors
	    delay = self.getdelayval()

	    valin = apvm.get_value_like(self.vobjs[1], self.strfmt)[1]
	    valen = apvm.get_value_like(self.vobjs[2], self.strfmt)[1]

	    if valen == "1":
		self.schedule(valin, delay, lo, hi)
	    else:
		self.schedule("z", delay, lo, hi)

	elif reason == apvm.cbAfterDelay:

	    # pop the event queue
	    self.events.pop(0)

	    if len(self.events) != 0:

		# Then schedule next val change and next callback
		# because there are no pending val change events on out.

		# figure out delta to the next event time
		(nextstr, nextdly, nextlo, nexthi) = self.events[0]

		delta = nextlo - lo
                if _debuggingmessages:
                    print "delta:", delta, "nextlo/lo", nextlo, lo
		reltime = apvm.pack_s_vpi_time(apvm.vpiSimTime, delta, 0, 0.0)

		# new value came from queue
		val = apvm.pack_s_vpi_value(apvm.vpiBinStrVal, nextstr)
	    
		# schedule value change
		# apvm.put_value(self.vobjs[3], val, reltime, apvm.vpiTransportDelay)
		apvm.put_value(self.vobjs[3], val, reltime, apvm.vpiPureTransportDelay)

		# also schedule our callback
		# self.callmeback(apvm.cbAfterDelay, None, reltime, val, "")
		self.callmeback(apvm.cbAfterDelay, None, reltime, self.suppressfmt, "")

	    else:
		pass

	else:
	    pass


	    

	
	
	
