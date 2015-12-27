#
# A stimulus-response module.
#
# SR FILE LINES:
#   t xxx - move to time t
#   s net 24'b01010101 - set net to value
#   r net 2'b0x - check response net value
#   c comment line xxx
#
# PLUSARGS/config params
#   +name:file=foo.sr
#   +name:debug=1
#   +name:comment=top.comment_net_name
#

from apvm import *
from BV import BV

import string
import pprint

#
# A function that checks actual BV values against expected BV values
#

def _map_fn(a, e):

    if e == 'x' or e == 'z':
	return 0
    if a == e:
	return 0
    else:
	return 1

def check_act_exp(act, exp):

    import operator

    astr = act.repr			# get simple string repr
    bstr = exp.repr

    results = map(_map_fn, act, exp)	# bitwise compare vector

    sum = reduce(operator.add, results)	# add up mismatches

    if sum == 0:
	return 1
    else:
	return None



#
# SR structure
#  a dict of (stim, resp, comm) vectors indexed by time
#

class srclass:

    def __init__(self):

	self.sr = { }
	self.handHash = { }

    def open(self):
	self.time = None
	self.stims = [ ]
	self.resps = [ ]
	self.comms = [ ]

    def close(self):
	if self.time != None:
	    tup = (self.stims, self.resps, self.comms)
	    self.sr[self.time] = tup

    def addstim(self, name, verilogvalue):
	hand = self.lookuphand(name)
	bv = BV(verilogvalue)
	self.stims += [ (hand, bv) ]

    def addresp(self, name, verilogvalue):
	hand = self.lookuphand(name)
	bv = BV(verilogvalue)
	self.resps += [ (hand, bv) ]

    def addcomm(self, comm):
	self.comms += [ ( comm ) ]

    def movetime(self, time):
	self.time = time
	
    def lookuphand(self, name):

	name = intern(name)
	if self.handHash.has_key(name):
	    return self.handHash[name]

	hand = handle_by_name(name, None)  # name, scope
	if not hand:
	    raise "Cannot find VPI name: " + name
	self.handHash[name] = hand
	return hand

    def gettimes(self):
	tlist = self.sr.keys()
	tlist.sort()
	return tlist
	

#
# hash table of times ... with (s,r,c) lists
#

def parsesr(f, debug):

    lines = f.readlines()

    sr = srclass()
    sr.open()

    for l in lines:

	if debug:
	    vpi_print("Reading line: %s" % l)

	s = string.split(l)

	if s[0] == "t":
	    sr.close()
	    sr.open()
	    sr.movetime(long(s[1]))

	elif s[0] == "s":
	    sr.addstim(s[1], s[2])

	elif s[0] == "r":
	    sr.addresp(s[1], s[2])

	elif s[0] == "c":
	    sr.addcomm(string.join(s[1:]))

	else:
	    raise "Unexpected SR line: " + str(s)

    sr.close()
    return sr
    

#
# This is the SR system function class.  An instance is created
# for each call to $apvm("name", "apvm_sr", "sr")
# in the verilog file.  We may support multiple instances one
# day differentiated by their name.
#

class sr(systf):

    
    #
    # We don't define the __init__ method.  Just inherit.
    #

    #
    # Set up things at Start-Of-Simulation (just before time 0)
    #
    def soscb(self):

	# look for filename, open it or cause exception
	### self.filename = plusarg_option("stimresp_file")
	self.filename = config_param_string(self.name, "file")
	self.f = open(self.filename, "r")

	# see if debug flag set
	### self.debug = plusarg_flag("stimresp_debug")
	self.debug = config_param_int(self.name, "debug")
	if self.debug:
	    vpi_print("Turning on SR debugging\n")

	# see if comment vector/net is defined
	### self.commvect = plusarg_option("stimresp_commvect")
	self.commvect = config_param_string(self.name, "commvect")
	self.commhandle = None
	if (self.commvect):
	    self.commhandle = handle_by_name(self.commvect, None)
	    

	# read the file and build our data structure
	self.sr = parsesr(self.f, self.debug)

	if self.debug:
	    vpi_print("SR Dict: \n")
	    vpi_print(pprint.pformat(self.sr.sr))
	    vpi_print("\n")

	# set state for scheduling
	self.times = self.sr.gettimes()
	self.cursor = -1

	# keep track of errors
	self.errcnt = 0


    #
    # This is called once in an init block
    #
    def calltf(self):

	if self.debug:
	    vpi_print("CALLTF for SR\n")

	# call us back with readonly synch at 0
	s_v_t = pack_s_vpi_time(vpiSimTime, 0, 0, 0.0)
	s_v_v = pack_s_vpi_value(vpiBinStrVal, "0x1z")
	self.callmeback(cbReadWriteSynch, None, s_v_t, s_v_v, "no userdata")


    #
    # This is the scheduler task
    #
    def callback(self, reason, h, t, v, idx, ud):

	if self.debug:
	    vpi_print("Callback for SR\n")


	if reason != cbReadOnlySynch:
	    # then we are either at time 0 or at end of time step

	    if self.cursor != -1:
		# check responses for cursor time
		self.checkresponses()
		self.printcomments()

	    if self.cursor == len(self.times) - 1:
		# do cleanup
		error_finalize()
		## if self.errcnt != 0:
		## vpi_print("STIMRESP: total errcnt = %d\n" % self.errcnt)
		## else:
		## vpi_print("STIMRESP: No Errors\n")

	    else:

		thistime = self.times[self.cursor]

		# advance to next step
		self.cursor += 1

		# compute delay until next time
		nexttime = self.times[self.cursor]

		if self.cursor == 0:
		    delay = 0.0
		else:
		    delay = float(nexttime - thistime)

		# schedule the current stims and writable comms after delay
		self.schedulestims(delay)
		self.schedulecomms(delay)

		# figure out how to call us back

                # TOM: icarus doesn't support scaled
		# s_vpi_time = pack_s_vpi_time(vpiScaledRealTime, 0, 0, delay)
		s_vpi_time = pack_s_vpi_time(vpiSimTime, delay, 0, 0.0)
		s_vpi_val = pack_s_vpi_value(vpiBinStrVal, "01")
		self.callmeback(cbAfterDelay, None, s_vpi_time, s_vpi_val, "no userdata")

	else:
	    # we are at beginning of time step, callback with ReadOnly
	    s_vpi_time = pack_s_vpi_time(0, 0, 0.0)
	    self.callmeback(cbReadOnlySynch, None, s_vpi_time, v, "no userdata")
			    
    
    def checkresponses(self):

	cursorentries = self.sr.sr[self.times[self.cursor]]
	rlist = cursorentries[1]

	for (handle, bv) in rlist:
	    actual = bv_from_vpi(handle)
	    check = check_act_exp(actual, bv)
	    if not check:
		# self.errcnt += 1
		net = get_str(vpiFullName, handle)
		error("Time: %g Act/Exp: %s %s %s\n" % (self.times[self.cursor], actual, bv, net))

	    # if debugging requested, print what we just did
	    # if self.debug:
	    # if not check:
	    # failedstr = " ... Failed."
	    # else:
	    # failedstr = ""
	    # error("Act/Exp: %s %s%s\n" % (actual, bv, failedstr))


    def printcomments(self):

	cursorentries = self.sr.sr[self.times[self.cursor]]
	clist = cursorentries[2]
	for c in clist:
	    vpi_print("%s\n" % c)

    def schedulestims(self, delay):

        # TOM: icarus
	# s_v_t = pack_s_vpi_time(vpiScaledRealTime, 0, 0, delay)
	s_v_t = pack_s_vpi_time(vpiSimTime, delay, 0, 0.0)

	cursorentries = self.sr.sr[self.times[self.cursor]]
	slist = cursorentries[0]

	for (handle, bv) in slist:
	    s_v_v = pack_s_vpi_value(vpiBinStrVal, bv.repr)
            # TOM: For Icarus:
	    # put_value(handle, s_v_v, s_v_t, vpiTransportDelay)
	    put_value(handle, s_v_v, s_v_t, vpiPureTransportDelay)

	    # if debugging requested, print what we are doing
	    if self.debug:
		vpi_print("Schedule %g %s\n" % (delay, bv))


    def schedulecomms(self, delay):

	if self.commhandle:

            # TOM: icarus
	    # s_v_t = pack_s_vpi_time(vpiScaledRealTime, 0, 0, delay)
            s_v_t = pack_s_vpi_time(vpiSimTime, delay, 0, 0.0)

	    cursorentries = self.sr.sr[self.times[self.cursor]]
	    clist = cursorentries[2]

	    for c in clist:
		s_v_v = pack_s_vpi_value(vpiStringVal, c)
                # TOM: For Icarus:
		# put_value(handle, s_v_v, s_v_t, vpiTransportDelay)
		put_value(handle, s_v_v, s_v_t, vpiPureTransportDelay)

	    
	    
	    
	    
	
	    


	



