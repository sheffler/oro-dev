#
# APVM:  A Python VPI Module
#
# Python implementation of class for Verilog VPI interface.
#
# Copyright (c) 2004 Tom Sheffler
#
#    This source code is free software; you can redistribute it
#    and/or modify it in source code form under the terms of the GNU
#    General Public License as published by the Free Software
#    Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA
#


import _apvm
from _apvm import *
from BV import BV
from BV import __BVinit__

import string
import sys
import types
import shelve

#
# Fix up argv from simulator args.
#   Tkinter is happier with argv set.
#
import sys
if (not sys.__dict__.has_key("argv")):
    sys.argv = list(sim_info[1])

#
# In order to support optional loggers, vpi_print is not called directly, but
# log-level functions are instead.  These may be re-bound to logger
# method calls.
#
def log_info(s):
    vpi_print(s)

def log_warning(s):
    vpi_print(s)

def log_error(s):
    vpi_print(s)

def log_critical(s):
    vpi_print(s)

#
# Wrap pack/unpack s_vpi_time such that longs are used for lo and hi.
#

def pack_s_vpi_time(typ, lo, hi, dly):

    """Pack s_vpi_time struct, ensuring lo and hi are longs."""

    typ = int(typ)
    lo = long(lo)
    hi = long(hi)
    dly = float(dly)

    return _apvm.pack_s_vpi_time(typ, lo, hi, dly)


def  unpack_s_vpi_time(x):

    """Unpack s_vpi_time struct, ensuring lo and hi are longs."""

    (typ, lo, hi, dly) = _apvm.unpack_s_vpi_time(x)
    lo = long(lo)
    hi = long(hi)
    return (typ, lo, hi, dly)
    



#
# Make a bitvector from the value of a VPI handle.
#
def bv_from_vpi(handle):

    sval = get_val_bin_str(handle)
    # sval = string.lower(sval)  # this may or may not be needed
    return BV(__BVinit__(sval))

#
# Put a bit-vector value on a VPI handle with delay given.
#  - integer delay for vpiSimTime in range 0..2^32-1
#  - long delay for vpiSimTime in range 0..2^64-1
#  - float delay for vpiScaledRealTime
#
def bv_to_vpi(handle, bv, delay=0):

    if type(delay) == type(0):
        s_v_t = pack_s_vpi_time(vpiSimTime, delay, 0, 0.0)
    elif type(delay) == type(0L):
        lo = long(delay & 0xFFFFFFFFL)
        hi = long((delay >> 32) & 0xFFFFFFFFL)
        s_v_t = pack_s_vpi_time(vpiSimTime, lo, hi, 0.0)
    elif type(delay) == type(0.0):
        s_v_t = pack_s_vpi_time(vpiScaledRealTime, 0, 0, delay)
    else:
        raise "Unknown delay type: " + str(type(delay))

    s_v_v = pack_s_vpi_value(vpiBinStrVal, bv.repr)
    # TOM: For Icarus
    # put_value(handle, s_v_v, s_v_t, vpiTransportDelay)
    put_value(handle, s_v_v, s_v_t, vpiPureTransportDelay)
    
    



_debuggingmessages = None

#
# These are used to implement systf object dispatching
#
_gensymcount = 99L
_dispatchdict = { }

def _gensym():

    global _gensymcount
    s = "_apvm_%010d" % _gensymcount
    s = intern(s)
    _gensymcount += 1
    return s

#
# APVM Callback Mechanism
#
# Similar semantics to VPI callback.  If event has not yet transpired,
# it can be cancelled.  Otherwise, the handle is invalid.  It seems
# to me that the only type of callback that is "persistent" is
# cbValueChange.
#

def schedule_cb(fn, reason, obj, tim, value, index, userdata):

    """User-friendly callback scheduler. Schedule a VPI callback.
    Arguments are:

      fn - a callable Python object (function or method)
      reason - a VPI reason (cbValueChange, cbAfterDelay, etc)
      obj - VPI handle for an object
      tim - product of pack_s_vpi_time
      value - product of pack_s_vpi_value
      index - object index
      userdata - arbitrary Python data to be associated with callback

    This function returns a Python object (key) that can be used
    with cancel_cb before the callback has expired.
    """

    key = _gensym()

    # 'cbfn0' is a module variable created by the APVM C code for use here.

    cbdata = pack_s_cb_data(reason, cbfn0, obj, tim, value, index, key)
    h = register_cb(cbdata)
    entry = (h, userdata, fn)
    _dispatchdict[key] = entry

    return key

#
# This function removes a callback from the VPI table as well
# as the APVM dispatch table.
#

def cancel_cb(key):

    """Used with the result of schedule_cb.  This function can un-schedule
    a callback if it has not yet expired.
    """

    if _dispatchdict.has_key(key):

        (h, userdata, fn) = _dispatchdict[key]
        status = remove_cb(h)
        print "cancel_cb status: ", status
        status = free_object(h)
        print "free_object status: ", status
        
        del _dispatchdict[key]

    else:
        print "Wassup?"

#
# This is the single function called by the C function registered with VPI
# for all APVM callbacks.  Python allows callable objects to be created
# dynamically.  This single entry point uses the
# dispatch table to dispatch to our Python callbacks.
#

def callback_dispatcher(cbdata):

    (reas, cbfn, obj, tim, value, idx, key) = cbdata
    try:
        (h, userdata, fn) = _dispatchdict[key]
    except:
        # table out of sync - ignore, or flag or whatever?
        pass

    # If this callback cannot occur again, remove it from our table
    # TOM: I am not sure which callbacks can repeat.  (I think only ValueChange.)
    if reas in [cbAfterDelay, cbReadWriteSynch,
                cbReadOnlySynch, cbNextSimTime
                ]:
        del _dispatchdict[key]

        # My current understanding is that we do not have to free_object(h)

    # Perform the callback
    fn(reas, obj, tim, value, idx, userdata)

#
# The package implements a very simple callback mechanism.
# We choose to do most of the work in Python and override the default.
#
_apvm.generic_callback = callback_dispatcher



class systf:

    """This is the base systf class."""

    _systftable = { }			# hashed by name

    def __init__(self, systf, cbfn, name, mname, cname, vobjs):

        """
        The args to this initializer are passed from the C layer of the APVM package.
        They are:
          systf - vpiHandle to the $apvm instance
          cbfn  - generic C callback function.  (Always the same for now.)
          name  - our instance name: either a string or a Verilog object.
          mname - the Python module name
          cname - the Python class name
          vobjs - a tuple of vpiHandles for the remainder of the instance arguments.
        """

	# simply save copies
	self.systf = systf		# our vpiHandle
	self.cbfn = cbfn		# C callback function
	self.name = name		# our name from the $apvm call
	self.mname = mname		# our module from the $apvm call
	self.cname = cname		# our class from the $apvm call
	self.vobjs = vobjs		# handles of the verilog args

	self._systftable[name] = self	# just for kicks

	# Print this instance's Banner
	log_info("*** APVM inst '%s', module '%s', class '%s'\n" %
		 (self.name, self.mname, self.cname))
	
	# Call our start-of-sim method
	self.soscb()


    def soscb(self):

        """Start of simulation callback method."""

	print "Start of simulation method"

    def eoscb(self):

        """End of simulation callback method."""

	print "End of simulation method"

    def StartOfSave(self):

        """Start Of Save callback method."""
        
	if _debuggingmessages:
	    print "StartOfSave %s\n" % self.name

	# open APVM system shelve object
	open_shelve_file()

	# call client method to save data
	self.save_client_data()


    def EndOfSave(self):

        """End of save callback method."""
        
	if _debuggingmessages:
	    print "EndOfSave %s\n" % self.name
	close_shelve_file()


    def save_client_data(self):

	"""
        To implement save/restore, the derived class should call
	self.save_data() with the appropriate data tuple here.
        """

	pass

    def StartOfRestart(self):

        """Start of Restart callback method."""
        
	if _debuggingmessages:
	    print "StartOfRestart %s\n" % self.name

	# open APVM system shelve object
	open_shelve_file()

	# call client method to restore saved data
	self.restore_client_data()


    def EndOfRestart(self):

        """End of Restart callback method."""
        
	if _debuggingmessages:
	    print "EndOfSave %s\n" % self.name
	close_shelve_file()

    def restore_client_data(self):

	"""
	To implement save/restore, the derived class should
	override this method calling self.restore_data().
        """

	pass


    def calltf(self):

        """
        The simple calltf method.  This is called whenever Verilog execution
        reaches the $apvm instance.
        """

	print "Calltf method"
	# return value integer from system function
	return 1


    def callback(self, reason, object, time, value, userdata):

        """The method called as a result of scheduled "callmeback" calls."""

	print "Instance Callback", reason, object, time, value, userdata


    def callmeback(self, reason, object, time, value, userdata):

        """
        Simplified callback mechanism.  Schedule our callback with
        the given reason, time value and userdata.  Upon callback, the
        dispatch function will call our callback method with the
        args given.
        """

	if object == None:
	    object = self.systf

        handle = schedule_cb(self.callback, reason, object, time, value, 0, userdata)

        # This can be used with cancel_cb to cancel it before it transpires
        return handle

    
    #
    # Convenient parameter getting function from config file/plusarg.
    # Programmer use ensures consistent usage across PLI apps.
    #

    def my_config_param_string(self, param):

        """
        Get configuration parameter named "param" from the section of
        the config file named [self.name], or from plusarg of the form
        +name:param=value.
        """

	return config_param_string(self.name, param)

    def my_config_param_int(self, param):

        """
        Like my_config_param_string, but return result as an integer.
        """

	return config_param_int(self.name, param)


    #
    # Save/Restore mechanism is built upon shelve objects.
    # User should call save_data and restore_data.
    # Our unique name is the key in the database
    #

    def save_data(self, key, data):

        """
        Direct access to shelve object.  Clients should try to use save_client_data
        instead, but if a particular key is required, the client may use this.
        """

	global shelve_object
	shelve_object[key] = data

    def restore_data(self, key):

        """
        Direct access to shelve object.  Clients should try to use restore_client_data
        instead, but if a particular key is required, the client may use this.
        """

	global shelve_object
	return shelve_object[key]
    


#
# This simple example prints some things and schedules itself
# to be called back later.
#

class _example(systf):

    def soscb(self):

	print "In SOSCB for new systf instance"
	print "  Name:", self.name
	print "  Module:", self.mname
	print "  Class:", self.cname
	print "  Systf:", self.systf
	print "  Cbfn:", self.cbfn
	print "  Vobjs:", self.vobjs

    	# print the pathnames of the verilog objects
	for v in self.vobjs:
	    print "    ", get_str(vpiFullName, v)

	print "\nAPVM System Info"
	# print dir(_apvm)
	print _apvm.sim_info


    def calltf(self):

	print "In CALLTF for systf instance: ", self.name

	# construct a time 5 units
	t1 = pack_s_vpi_time(vpiSimTime, 5, 0, 0.0)

	# show how to take a time object apart
	print "Time T1", unpack_s_vpi_time(t1)

	# construct a time 10 units
	# t2 = pack_s_vpi_time(vpiScaledRealTime, 0, 0, 10.0)
	t2 = pack_s_vpi_time(vpiSimTime, 10, 0, 0.0)

	# Get the values of our vectors

	format = pack_s_vpi_value(vpiBinStrVal, "01xz")
        for v in self.vobjs:
	    name = get_str(vpiFullName, v)
	    x = get_value_like(v, format)
	    print "  Vector %s: %s" % (name, x[1])

	# Schedule us to be called back at the two times
        spr = pack_s_vpi_value(vpiSuppressVal, 0)
	# self.callmeback(cbAfterDelay, None, t1, format, "my userdata 1")
	self.callmeback(cbAfterDelay, None, t1, spr, "my userdata 1")
	# self.callmeback(cbAfterDelay, None, t2, format, "my userdata 2")
	self.callmeback(cbAfterDelay, None, t2, spr, "my userdata 2")

        return 0

    def callback(self, reason, h, t, v, idx, ud):

	print "In Py CALLBACK", reason, h, t, v, idx, ud
	tt = unpack_s_vpi_time(t)

	print "  at time: ", tt

	# Get the values of our vectors

	format = pack_s_vpi_value( vpiBinStrVal, "01xz")
	for v in self.vobjs:
	    name = get_str(vpiFullName, v)
	    x = get_value_like(v, format)
	    print "  Vector %s: %s" % (name, x[1])

	
################################################################
#
# Plusarg utilities ... -f recursion supported properly
#
################################################################

def __plusarg_option_helper(name, list):

    for i in list:
	if type(i) == types.ListType:
	    # skip the filename
	    res = __plusarg_option_helper(name, i[1:])
	    if res:
		return res
	else:
	    x = string.find(i, name)
	    if x != -1:
		pos = string.find(i, "=")
		return i[pos+1:]
    return None
	    

# look for "+name=value"
def plusarg_option(name):

    n = "+" + name + "="
    return __plusarg_option_helper(n, sim_info[1])


def __plusarg_flag_helper(name, ll):

    for i in ll:
	if type(i) == types.ListType:
	    # skip the filename
	    res =  __plusarg_flag_helper(name, i[1:])
	    if res:
		return res
	else:
	    x = string.find(i, name)
	    if x != -1:
		return 1;
    return None
    

# return true if "+name" is in list
def plusarg_flag(name):

    n = "+" + name
    return __plusarg_flag_helper(n, sim_info[1])



################################################################
#
# Standard ERROR and WARNING Utilities.
#
################################################################

error_count = 0
warning_count = 0

error_count_h = None
warning_count_h = None

error_format = pack_s_vpi_value(vpiIntVal, 0)

#
# Set the verilog net that is used for error counting
# Example:
#   set_error_net("top.error_counter")
#
def set_error_net(path):

    h = handle_by_name(path, None)
    if h:
        global error_count_h
	error_count_h = h
    else:
	sys.stderr.write("Warning: error net %s not found!\n" % path)
	

#
# Set the verilog net that is used for warning counting
#
def set_warning_net(path):

    h = handle_by_name(path, None)
    if h:
        global warning_count_h
	warning_count_h = h
    else:
	sys.stderr.write("Warning: warning net %s not found!\n" % path)
	

#
# Print the error message and increment the Verilog error
# variable if it has been bound.
#
def error(s):

    global error_count, error_count_h

    # sync the error count from verilog
    if error_count_h:
	x = get_value_like(error_count_h, error_format)
	error_count = x[1]

    error_count = error_count + 1

    log_error("*** ERROR %4d: %s\n" % (error_count, s))

    # set the verilog value
    if error_count_h:
	val = pack_s_vpi_value(vpiIntVal, error_count)
	put_value(error_count_h, val, None, None)

#
# Print the warning message and increment the Verilog warning
# variable if it has been bound.
#
def warning(s):

    global warning_count, warning_count_h

    # sync the warning count from verilog
    if warning_count_h:
	x = get_value_like(warning_count_h, error_format)
	warning_count = x[1]

    warning_count = warning_count + 1

    log_warn("*** WARNING %4d: %s\n" % (warning_count, s))

    # set the verilog value
    if warning_count_h:
	val = pack_s_vpi_value(vpiIntVal, warning_count)
	put_value(warning_count_h, val, None, None)

#
# Call this at the end of simulation for a report, if desired.
#
def error_finalize(banner="APVM Simulation Complete"):

    global error_count, error_count_h
    global warning_count, warning_count_h

    # sync the error count from verilog
    if error_count_h:
	x = get_value_like(error_count_h, error_format)
	error_count = x[1]

    # sync the warning count from verilog
    if warning_count_h:
	x = get_value_like(warning_count_h, error_format)
	warning_count = x[1]

    log_info("%s: %4d errors, %4d warnings.\n" %
             (banner, error_count, warning_count))

	
################################################################
#
# Standard configuration utilites, using Python ConfigParser.
#
################################################################

configobject = None

def config_file_find_and_open():

    """Search order for config file is:
    - environment variable APVM_CONFIGFILE
    - local dir file "apvm.cfg"
    - home dir file  "~/apvm.cfg"
    """


    import ConfigParser
    import os

    global configobject
    done = None

    # Try environment variable name first
    filename = os.getenv("APVM_CONFIGFILE")
    if filename:
	try:
	    f = open(filename, "r")
	except:
	    f = None

	if f:
	    configobject = ConfigParser.ConfigParser()
	    configobject.read(filename)
	    done = 1

    # try next file name
    if not done:
	filename = "apvm.cfg"
	try:
	    f = open(filename, "r")
	except:
	    f = None

	if f:
	    configobject = ConfigParser.ConfigParser()
	    configobject.read(filename)
	    done = 1

    # try home directory
    if not done:
	filename = os.path.expanduser("~/apvm.cfg")
	
	try:
	    f = open(filename, "r")
	except:
	    f = None

	if f:
	    configobject = ConfigParser.ConfigParser()
	    configobject.read(filename)
	    done = 1
	
################################################################
#
# Standard Object Configuration Interface
#
# Look for a parameter for the given instance "name", parameter "param."
# We look in the plusargs first, for +name:param=value, then we
# look in the configobject for a section named "name" with param "param."
#
################################################################

#
# Return plusarg or config param for the name given.
#
def config_param_string(name, param):

    np = name + ":" + param

    # look for "name:param" plusarg
    val = plusarg_option(np)

    if val:
	return val

    # look for it in the config object
    try:
	val = configobject.get(name, param)
    except:
	val = None

    return val

#
# Return plusarg or config param as an int (or None if not found)
#
def config_param_int(name, param):

    val = config_param_string(name, param)

    if val:
	return int(val)
    else:
	return None


################################################################
#
# Save/Restore mechanism is built upon shelve.
#
# Each systf instance places its data in the shelve object
# at Save and reads it back at Restore.
#
# Shelve file name uses standard mechanisms to get params.
# param is "apvm:shelve_file"
#
################################################################

shelve_object = None


# This fn is call by every systf object, but needs to only open
# one file on StartOfRestore
def open_shelve_file():

    global shelve_object

    if shelve_object == None:

	sname = config_param_string("apvm", "shelve_file")
	if not sname:
	    sname = "apvm.gdbm"

	shelve_object = shelve.open(sname)


# This is called by every systf object as well on EndOfSave
def close_shelve_file():

    global shelve_object

    if shelve_object:
	shelve_object.close()
	shelve_object = None



################################################################
#
# This module runs some setup code when it is loaded.
#
################################################################

def __init__():

    global _debuggingmessages

    # search for a config file and read it
    config_file_find_and_open()

    # allow this to be set in the config file
    if config_param_string("apvm", "debug"):
	_debuggingmessages = 1

    if _debuggingmessages:
	print "******** APVM CONFIG FILE DUMP ********\n"
	configobject.write(sys.stdout)
	print "******** END OF APVM CONFIG FILE DUMP ********\n"

    # set the error_net and warning_net verilog nets if specified
    errnet = config_param_string("apvm", "error_net")
    if errnet:
	set_error_net(errnet)

	if _debuggingmessages:
	    print "Setting error net to ", errnet

    warnnet = config_param_string("apvm", "warning_net")
    if warnnet:
	set_warning_net(warnnet)

	if _debuggingmessages:
	    print "Setting warning net to ", warnnet


#
# Call module init fn upon module load
#

__init__()

